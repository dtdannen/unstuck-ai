"use client"

import { useState, useEffect, useCallback } from 'react'

export interface InvoiceData {
  paymentRequest: string
  paymentHash?: string
  verify?: string
  successAction?: {
    tag: string
    message?: string
    url?: string
  }
}

export interface PaymentResult {
  preimage: string
}

let bitcoinConnectLoaded = false
let lightningToolsLoaded = false

// Load Bitcoin Connect script dynamically
const loadBitcoinConnect = async () => {
  if (bitcoinConnectLoaded) return
  
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.type = 'module'
    script.src = 'https://esm.sh/@getalby/bitcoin-connect@3.8.0'
    script.onload = () => {
      bitcoinConnectLoaded = true
      resolve(true)
    }
    script.onerror = reject
    document.head.appendChild(script)
  })
}

export function useBitcoinConnect() {
  const [isLoaded, setIsLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [invoice, setInvoice] = useState<InvoiceData | null>(null)

  useEffect(() => {
    loadBitcoinConnect()
      .then(() => setIsLoaded(true))
      .catch((err) => {
        console.error('Failed to load Bitcoin Connect:', err)
        setError('Failed to load Bitcoin Connect')
      })
  }, [])

  const generateInvoice = useCallback(async (amountSats: number, memo?: string): Promise<InvoiceData> => {
    try {
      // Use Lightning Tools to generate invoice
      const { LightningAddress } = await import('@getalby/lightning-tools')
      const ln = new LightningAddress('hello@getalby.com')
      
      await ln.fetch()
      
      const invoiceData = await ln.requestInvoice({
        satoshi: amountSats,
        comment: memo || `Payment for ${amountSats} sats`
      })
      
      setInvoice(invoiceData)
      return invoiceData
    } catch (err) {
      console.error('Error generating invoice:', err)
      throw new Error('Failed to generate invoice')
    }
  }, [])

  const payInvoice = useCallback(async (bolt11: string): Promise<PaymentResult> => {
    if (!isLoaded) {
      throw new Error('Bitcoin Connect not loaded')
    }

    try {
      // Access requestProvider from global scope after script loads
      const { requestProvider } = (window as any)
      if (!requestProvider) {
        throw new Error('Bitcoin Connect requestProvider not available')
      }
      
      const provider = await requestProvider()
      const result = await provider.sendPayment(bolt11)
      return result
    } catch (err) {
      console.error('Payment failed:', err)
      throw new Error('Payment failed')
    }
  }, [isLoaded])

  return {
    isLoaded,
    error,
    generateInvoice,
    payInvoice,
    invoice
  }
}