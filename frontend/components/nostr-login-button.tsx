"use client"

import Link from "next/link"
import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Loader2, User, Settings, LogOut, CheckSquare } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

// Define the relays to use
const RELAYS = ["wss://relay.damus.io", "wss://relay.nostr.band", "wss://relay.primal.net", "wss://relay.dvmdash.live"]

// Define profile type
interface NostrProfile {
  name?: string
  displayName?: string
  picture?: string
  about?: string
  nip05?: string
}

export default function NostrLoginButton() {
  const [pubkey, setPubkey] = useState<string | null>(null)
  const [profile, setProfile] = useState<NostrProfile | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingProfile, setIsLoadingProfile] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)

  // Check if user is already logged in on component mount
  useEffect(() => {
    const storedPubkey = localStorage.getItem("nostrPubkey")
    if (storedPubkey) {
      setPubkey(storedPubkey)

      // Load profile data if we have a pubkey
      const storedProfile = localStorage.getItem("nostrProfile")
      if (storedProfile) {
        try {
          setProfile(JSON.parse(storedProfile))
        } catch (e) {
          console.error("Failed to parse stored profile:", e)
        }
      }
    }
  }, [])

  // Fetch profile when pubkey changes
  useEffect(() => {
    if (pubkey && !profile) {
      fetchNostrProfile(pubkey)
    }
  }, [pubkey, profile])

  async function fetchNostrProfile(pubkey: string) {
    if (typeof window === "undefined") return

    try {
      setIsLoadingProfile(true)
      console.log("Fetching profile for pubkey:", pubkey)

      // Import directly from the global object
      if (!window.nostrTools && !window.NostrTools) {
        console.error("Nostr tools not found in window object")

        // Fallback to basic profile
        const basicProfile = {
          name: `User ${pubkey.substring(0, 8)}`,
          picture: null,
        }
        setProfile(basicProfile)
        localStorage.setItem("nostrProfile", JSON.stringify(basicProfile))
        setIsLoadingProfile(false)
        return
      }

      // Try to get the SimplePool constructor from either global object
      const nostrLib = window.nostrTools || window.NostrTools

      if (!nostrLib.SimplePool) {
        console.error("SimplePool not found in nostr library")

        // Fallback to basic profile
        const basicProfile = {
          name: `User ${pubkey.substring(0, 8)}`,
          picture: null,
        }
        setProfile(basicProfile)
        localStorage.setItem("nostrProfile", JSON.stringify(basicProfile))
        setIsLoadingProfile(false)
        return
      }

      const pool = new nostrLib.SimplePool()

      // Using the subscription approach from the example
      const profilePromise = new Promise<NostrProfile | null>((resolve) => {
        let profileData: NostrProfile | null = null

        // Set a timeout to resolve if we don't get a profile in 5 seconds
        const timeout = setTimeout(() => {
          resolve(profileData)
        }, 5000)

        const sub = pool.subscribeMany(
          RELAYS,
          [
            {
              kinds: [0],
              authors: [pubkey],
              limit: 1,
            },
          ],
          {
            onevent(event) {
              try {
                profileData = JSON.parse(event.content)
                console.log("Profile data received:", profileData)
                clearTimeout(timeout)
                sub.close()
                resolve(profileData)
              } catch (e) {
                console.error("Failed to parse profile data:", e)
              }
            },
            oneose() {
              // End of stored events
              setTimeout(() => {
                sub.close()
                resolve(profileData)
              }, 1000) // Give a little extra time for any late events
            },
          },
        )
      })

      // Wait for profile data or timeout
      const profileData = await profilePromise

      if (profileData) {
        setProfile(profileData)
        localStorage.setItem("nostrProfile", JSON.stringify(profileData))
      } else {
        console.log("No profile events found")

        // Fallback to basic profile
        const basicProfile = {
          name: `User ${pubkey.substring(0, 8)}`,
          picture: null,
        }
        setProfile(basicProfile)
        localStorage.setItem("nostrProfile", JSON.stringify(basicProfile))
      }

      // Close all connections
      pool.close(RELAYS)
    } catch (error) {
      console.error("Error fetching Nostr profile:", error)

      // Fallback to basic profile
      const basicProfile = {
        name: `User ${pubkey.substring(0, 8)}`,
        picture: null,
      }
      setProfile(basicProfile)
      localStorage.setItem("nostrProfile", JSON.stringify(basicProfile))
    } finally {
      setIsLoadingProfile(false)
    }
  }

  async function nostrLogin() {
    if (typeof window === "undefined") return

    // @ts-ignore - Nostr extension types
    if (window.nostr) {
      try {
        setIsLoading(true)

        // Request the user's public key (NIP-07)
        // @ts-ignore - Nostr extension types
        const userPubkey = await window.nostr.getPublicKey()

        // Store pubkey in state and localStorage
        setPubkey(userPubkey)
        localStorage.setItem("nostrPubkey", userPubkey)

        // Optionally, sign a challenge (for authentication)
        const challenge = `auth-${Math.random().toString(36).substring(2, 15)}`

        // @ts-ignore - Nostr extension types
        const signed = await window.nostr.signEvent({
          kind: 22242, // Kind for authentication
          pubkey: userPubkey,
          created_at: Math.floor(Date.now() / 1000),
          tags: [],
          content: challenge,
        })

        console.log("Signed event:", signed)

        // In a real app, you would send 'signed' to your backend to verify login
      } catch (err) {
        console.error("Nostr login failed:", err)
        alert(`Nostr login failed: ${err instanceof Error ? err.message : "Unknown error"}`)
      } finally {
        setIsLoading(false)
      }
    } else {
      alert("Nostr extension (Alby, nos2x, etc.) not found! Please install a Nostr extension.")
    }
  }

  function handleLogout() {
    setPubkey(null)
    setProfile(null)
    localStorage.removeItem("nostrPubkey")
    localStorage.removeItem("nostrProfile")
    setDropdownOpen(false)
  }

  // Get display name from profile
  const displayName = profile?.name || profile?.displayName || (pubkey ? `${pubkey.substring(0, 10)}...` : "")

  // Get initials for avatar fallback
  const getInitials = () => {
    if (!displayName) return "U"
    return displayName.charAt(0).toUpperCase()
  }

  const handleAvatarClick = () => {
    console.log("Avatar clicked, toggling dropdown")
    setDropdownOpen(!dropdownOpen)
  }

  return pubkey ? (
    <div className="flex items-center gap-3">
      {isLoadingProfile ? (
        <Loader2 className="h-6 w-6 animate-spin text-[#757575]" />
      ) : (
        <>
          <div className="flex flex-col items-end">
            <span className="text-sm font-medium">{displayName}</span>
          </div>

          <DropdownMenu open={dropdownOpen} onOpenChange={setDropdownOpen}>
            <DropdownMenuTrigger asChild>
              <button className="focus:outline-none">
                <Avatar
                  className="h-8 w-8 border border-[#e3e3e3] cursor-pointer hover:ring-2 hover:ring-[#f5a623] transition-all"
                  onClick={handleAvatarClick}
                >
                  <AvatarImage src={profile?.picture || "/placeholder.svg"} alt={displayName} />
                  <AvatarFallback>{getInitials()}</AvatarFallback>
                </Avatar>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="w-56 bg-white shadow-lg rounded-md border border-gray-200 py-1 mt-1"
            >
              <DropdownMenuLabel className="font-semibold px-3 py-2">My Account</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-gray-200 h-px my-1" />

              <DropdownMenuItem className="px-3 py-2 hover:bg-gray-100 cursor-pointer flex items-center gap-2">
                <User className="h-4 w-4" />
                <Link href="/profile" className="w-full">
                  Profile
                </Link>
              </DropdownMenuItem>

              <DropdownMenuItem className="px-3 py-2 hover:bg-gray-100 cursor-pointer flex items-center gap-2">
                <CheckSquare className="h-4 w-4" />
                <Link href="/my-tasks" className="w-full">
                  My Tasks
                </Link>
              </DropdownMenuItem>

              <DropdownMenuItem className="px-3 py-2 hover:bg-gray-100 cursor-pointer flex items-center gap-2">
                <Settings className="h-4 w-4" />
                <Link href="/settings" className="w-full">
                  Settings
                </Link>
              </DropdownMenuItem>

              <DropdownMenuSeparator className="bg-gray-200 h-px my-1" />

              <DropdownMenuItem
                onClick={handleLogout}
                className="px-3 py-2 hover:bg-gray-100 cursor-pointer text-red-500 flex items-center gap-2"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </>
      )}
    </div>
  ) : (
    <Button onClick={nostrLogin} disabled={isLoading} className="bg-[#2c2c2c] hover:bg-[#1e1e1e] text-white">
      {isLoading ? "Connecting..." : "Login with Nostr"}
    </Button>
  )
}
