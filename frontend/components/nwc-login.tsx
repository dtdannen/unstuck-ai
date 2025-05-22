"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Wallet, LogOut } from 'lucide-react'
import { nwc } from '@getalby/sdk'

interface NWCLoginProps {
  onNWCClientChange?: (client: any) => void
}

export function NWCLogin({ onNWCClientChange }: NWCLoginProps) {
  const [nwcClient, setNwcClient] = useState<any>(null)
  const [nwcUrl, setNwcUrl] = useState('')
  const [connecting, setConnecting] = useState(false)
  const [walletInfo, setWalletInfo] = useState<any>(null)
  const [showDialog, setShowDialog] = useState(false)

  useEffect(() => {
    // Load saved NWC connection on mount
    const savedNwcUrl = localStorage.getItem('nwcUrl')
    if (savedNwcUrl) {
      setNwcUrl(savedNwcUrl)
      connectNWC(savedNwcUrl)
    }
  }, [])

  const connectNWC = async (url?: string) => {
    try {
      setConnecting(true)
      const connectionUrl = url || nwcUrl
      
      if (!connectionUrl) {
        throw new Error("Please enter an NWC connection string")
      }
      
      const client = new nwc.NWCClient({
        nostrWalletConnectUrl: connectionUrl,
      })
      
      const info = await client.getInfo()
      
      setNwcClient(client)
      setWalletInfo(info)
      setShowDialog(false)
      
      // Save to localStorage
      localStorage.setItem('nwcUrl', connectionUrl)
      
      // Notify parent component
      onNWCClientChange?.(client)
      
    } catch (error: any) {
      console.error('NWC connection failed:', error)
      alert("Connection failed: " + error.message)
    } finally {
      setConnecting(false)
    }
  }

  const disconnect = () => {
    if (nwcClient) {
      nwcClient.close()
    }
    setNwcClient(null)
    setWalletInfo(null)
    setNwcUrl('')
    localStorage.removeItem('nwcUrl')
    onNWCClientChange?.(null)
  }

  if (nwcClient && walletInfo) {
    return (
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-2 text-sm">
          <Wallet className="h-4 w-4 text-green-600" />
          <span className="text-green-600 font-medium">{walletInfo.alias}</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={disconnect}
          className="text-gray-500 hover:text-red-600"
        >
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    )
  }

  return (
    <Dialog open={showDialog} onOpenChange={setShowDialog}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="flex items-center gap-2">
          <Wallet className="h-4 w-4" />
          Connect Wallet
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Connect Lightning Wallet</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <label htmlFor="nwc-url" className="block text-sm font-medium mb-2">
              NWC Connection String
            </label>
            <Input
              id="nwc-url"
              type="password"
              placeholder="nostr+walletconnect://..."
              value={nwcUrl}
              onChange={(e) => setNwcUrl(e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">
              Get this from your Lightning wallet (Alby, etc.)
            </p>
          </div>
          <Button
            onClick={() => connectNWC()}
            disabled={connecting || !nwcUrl}
            className="w-full"
          >
            {connecting ? "Connecting..." : "Connect"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}