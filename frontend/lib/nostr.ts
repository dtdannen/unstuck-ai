"use client";

import NDK, { NDKEvent, NDKUser, NDKFilter, NDKSubscription } from '@nostr-dev-kit/ndk';
import { useState, useEffect } from 'react';

// Define the relays to use
export const RELAYS = [
  'wss://relay.damus.io',
  'wss://relay.nostr.band',
  'wss://relay.primal.net',
  'wss://relay.dvmdash.live'
];

// Initialize NDK
export const ndk = new NDK({
  explicitRelayUrls: RELAYS,
  autoConnectUserRelays: true,
});

// Connect to relays
let connected = false;
export async function ensureConnected() {
  if (!connected) {
    try {
      await ndk.connect();
      connected = true;
      console.log('NDK: Connected to relays');
    } catch (e) {
      console.error('NDK: Failed to connect to relays', e);
      throw e;
    }
  }
  return ndk;
}

// Fetch profile for a user
export async function fetchProfile(pubkey: string): Promise<NDKUser> {
  await ensureConnected();
  const user = ndk.getUser({ pubkey });
  await user.fetchProfile();
  return user;
}

// Fetch tasks (kind 5109 events)
export async function fetchTasks(limit: number = 20): Promise<NDKEvent[]> {
  await ensureConnected();
  
  const filter: NDKFilter = {
    kinds: [5109, 30006],
    limit: limit,
  };
  
  try {
    const events = await ndk.fetchEvents(filter);
    const eventsArray = Array.from(events);
    return eventsArray;
  } catch (e) {
    console.error('NDK: Failed to fetch tasks', e);
    throw e;
  }
}

// Function to create and sign an event
export async function createSignedEvent(kind: number, content: string, tags: string[][]): Promise<NDKEvent | null> {
  await ensureConnected();
  
  // Check if NIP-07 extension is available
  if (!window.nostr) {
    console.error('NDK: No NIP-07 extension found');
    return null;
  }
  
  try {
    // Get the current user via NIP-07
    const signer = ndk.signer;
    if (!signer) {
      const pubkey = await window.nostr.getPublicKey();
      const user = ndk.getUser({ pubkey });
      if (!user) {
        throw new Error('NDK: Failed to get user');
      }
      
      // Create the event
      const event = new NDKEvent(ndk);
      event.kind = kind;
      event.content = content;
      event.tags = tags;
      
      // Sign the event with NIP-07
      await event.sign();
      
      return event;
    } else {
      // If we already have a signer
      const event = new NDKEvent(ndk);
      event.kind = kind;
      event.content = content;
      event.tags = tags;
      
      await event.sign();
      return event;
    }
  } catch (e) {
    console.error('NDK: Failed to create and sign event', e);
    return null;
  }
}

// Subscribe to events in real-time
export function subscribeToEvents(filter: NDKFilter, callback: (event: NDKEvent) => void): () => void {
  ensureConnected().then(() => {
    const subscription = ndk.subscribe(filter, { closeOnEose: false });
    
    subscription.on('event', (event: NDKEvent) => {
      callback(event);
    });
    
    return () => {
      subscription.stop();
    };
  }).catch(e => {
    console.error('NDK: Failed to subscribe to events', e);
  });
  
  // Return unsubscribe function
  return () => {};
}

// Helper function to extract tag value
export function getTagValue(event: NDKEvent, tagName: string): string | null {
  const tag = event.tags.find(t => t[0] === tagName);
  return tag && tag.length > 1 ? tag[1] : null;
}

// Cache for profiles to avoid redundant fetches
const profileCache: Record<string, NDKUser> = {};

// Get profile with caching
export async function getCachedProfile(pubkey: string): Promise<NDKUser | null> {
  if (profileCache[pubkey]) {
    return profileCache[pubkey];
  }
  
  try {
    const user = await fetchProfile(pubkey);
    profileCache[pubkey] = user;
    return user;
  } catch (e) {
    console.error(`NDK: Failed to fetch profile for ${pubkey}`, e);
    return null;
  }
}

// Helper to check if the user is logged in
export function useNostrUser() {
  const [user, setUser] = useState<NDKUser | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const checkUser = async () => {
      try {
        // Check localStorage first
        const storedPubkey = localStorage.getItem("nostrPubkey");
        if (storedPubkey) {
          await ensureConnected();
          const ndkUser = ndk.getUser({ pubkey: storedPubkey });
          
          // Try to fetch profile
          try {
            await ndkUser.fetchProfile();
          } catch (e) {
            console.warn('NDK: Failed to fetch profile for stored user', e);
          }
          
          setUser(ndkUser);
        }
      } catch (e) {
        console.error('NDK: Failed to get stored user', e);
      } finally {
        setLoading(false);
      }
    };
    
    checkUser();
  }, []);
  
  const login = async (): Promise<NDKUser | null> => {
    setLoading(true);
    try {
      if (!window.nostr) {
        alert('Nostr extension (Alby, nos2x, etc.) not found! Please install a Nostr extension.');
        return null;
      }
      
      const pubkey = await window.nostr.getPublicKey();
      await ensureConnected();
      
      const ndkUser = ndk.getUser({ pubkey });
      try {
        await ndkUser.fetchProfile();
      } catch (e) {
        console.warn('NDK: Failed to fetch profile during login', e);
      }
      
      // Store pubkey in localStorage
      localStorage.setItem("nostrPubkey", pubkey);
      
      setUser(ndkUser);
      return ndkUser;
    } catch (e) {
      console.error('NDK: Login failed', e);
      alert(`Nostr login failed: ${e instanceof Error ? e.message : "Unknown error"}`);
      return null;
    } finally {
      setLoading(false);
    }
  };
  
  const logout = () => {
    localStorage.removeItem("nostrPubkey");
    localStorage.removeItem("nostrProfile");
    setUser(null);
  };
  
  return { user, loading, login, logout };
}