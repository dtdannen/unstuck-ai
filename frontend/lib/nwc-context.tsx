"use client"

import React, { createContext, useContext, useState, ReactNode } from 'react'

interface NWCContextType {
  nwcClient: any
  setNwcClient: (client: any) => void
}

const NWCContext = createContext<NWCContextType | undefined>(undefined)

export function NWCProvider({ children }: { children: ReactNode }) {
  const [nwcClient, setNwcClient] = useState<any>(null)

  return (
    <NWCContext.Provider value={{ nwcClient, setNwcClient }}>
      {children}
    </NWCContext.Provider>
  )
}

export function useNWC() {
  const context = useContext(NWCContext)
  if (context === undefined) {
    throw new Error('useNWC must be used within a NWCProvider')
  }
  return context
}