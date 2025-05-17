"use client"

import { useEffect, useState } from "react"

export default function NostrScript() {
  const [scriptLoaded, setScriptLoaded] = useState(false)

  useEffect(() => {
    // Create and append the script element
    const script = document.createElement("script")
    script.src = "https://unstuck-goose.nyc3.cdn.digitaloceanspaces.com/nostr.bundle.js"
    script.async = true

    // Set up event handlers to track loading
    script.onload = () => {
      console.log("Nostr bundle script loaded successfully")
      setScriptLoaded(true)

      // Debug what's available after loading
      console.log("Window object after script load:", Object.keys(window))

      // Check for the NostrTools global (capital N and T based on console logs)
      if (window.NostrTools) {
        console.log("NostrTools available:", Object.keys(window.NostrTools))
      } else {
        console.log("NostrTools not found in window object after loading")

        // Check for other possible global variables
        const possibleGlobals = ["NostrTools", "nostrTools", "Nostr", "nostr", "NostrBundle"]
        for (const name of possibleGlobals) {
          if (window[name]) {
            console.log(`Found global: window.${name}`, Object.keys(window[name]))
          }
        }
      }
    }

    script.onerror = () => {
      console.error("Failed to load Nostr bundle script")
    }

    document.body.appendChild(script)

    // Clean up on unmount
    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script)
      }
    }
  }, [])

  return null
}
