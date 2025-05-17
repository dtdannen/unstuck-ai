interface Window {
  nostr?: {
    getPublicKey: () => Promise<string>
    signEvent: (event: any) => Promise<any>
  }
  NostrTools?: any
  nostrTools?: any
}
