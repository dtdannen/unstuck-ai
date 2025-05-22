"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Loader2, Zap, Check } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { useRouter } from 'next/navigation'
import * as bolt11 from 'bolt11'

interface NWCPaymentProps {
  nwcClient: any
  defaultAmount?: number
  memo?: string
  taskId?: string
  onInvoiceGenerated?: (invoice: any) => void
  onPaymentSuccess?: () => void
  className?: string
}

export function NWCPayment({ 
  nwcClient,
  defaultAmount = 100,
  memo = "Payment",
  taskId,
  onInvoiceGenerated,
  onPaymentSuccess,
  className = ""
}: NWCPaymentProps) {
  const [amount, setAmount] = useState(defaultAmount)
  const [invoice, setInvoice] = useState<any>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [paymentComplete, setPaymentComplete] = useState(false)
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [pollInterval, setPollInterval] = useState<NodeJS.Timeout | null>(null)
  
  const { toast } = useToast()
  const router = useRouter()

  // Function to extract payment hash from bolt11 invoice
  const extractPaymentHashFromInvoice = (invoice: string): string | null => {
    try {
      const decoded = bolt11.decode(invoice)
      console.log('Decoded bolt11:', decoded)
      
      // The payment hash should be in the tagsObject
      if (decoded.tagsObject && decoded.tagsObject.payment_hash) {
        return decoded.tagsObject.payment_hash
      }
      
      // Try alternative fields
      if (decoded.paymentHash) {
        return decoded.paymentHash
      }
      
      return null
    } catch (error) {
      console.error('Error extracting payment hash from invoice:', error)
      return null
    }
  }

  useEffect(() => {
    // Cleanup polling on unmount
    return () => {
      if (pollInterval) {
        clearInterval(pollInterval)
      }
    }
  }, [pollInterval])

  const handleGenerateInvoice = async () => {
    if (!nwcClient) {
      toast({
        title: "Error",
        description: "Please connect your wallet first",
        variant: "destructive"
      })
      return
    }

    try {
      setIsGenerating(true)
      
      const response = await nwcClient.makeInvoice({
        amount: amount * 1000, // convert to millisats
        description: memo
      })

      console.log('NWC Invoice Response:', response)
      setInvoice(response)
      onInvoiceGenerated?.(response)
      
      // Extract payment hash from bolt11 invoice
      const paymentHash = extractPaymentHashFromInvoice(response.invoice)
      console.log('Payment hash for polling:', paymentHash)
      startPolling(paymentHash)
      
      toast({
        title: "Invoice Generated",
        description: `Generated invoice for ${amount} sats`,
      })
    } catch (error: any) {
      console.error('Error generating invoice:', error)
      toast({
        title: "Error",
        description: "Failed to generate invoice. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const startPolling = (paymentHash: string) => {
    console.log("Starting polling for payment hash:", paymentHash)
    
    if (!paymentHash) {
      console.error("Cannot start polling: payment hash is undefined")
      return
    }
    
    const interval = setInterval(async () => {
      try {
        console.log("Checking invoice status...")
        const response = await nwcClient.lookupInvoice({
          payment_hash: paymentHash
        })

        console.log("Invoice lookup response:", response)
        
        if (response.state === "settled") {
          console.log("Invoice is PAID!")
          setPaymentComplete(true)
          setShowSuccessModal(true)
          
          // Stop polling
          clearInterval(interval)
          setPollInterval(null)
          
          // Notify parent
          onPaymentSuccess?.()
        }
        
      } catch (error) {
        console.error("Error checking invoice status:", error)
      }
    }, 2000) // Poll every 2 seconds

    setPollInterval(interval)
  }

  const resetPayment = () => {
    setInvoice(null)
    setPaymentComplete(false)
    setShowSuccessModal(false)
    if (pollInterval) {
      clearInterval(pollInterval)
      setPollInterval(null)
    }
  }

  if (!nwcClient) {
    return (
      <div className={`p-4 border rounded-lg bg-gray-50 ${className}`}>
        <p className="text-gray-600 text-center">
          Please connect your wallet to generate invoices
        </p>
      </div>
    )
  }

  if (paymentComplete) {
    return (
      <>
        <div className={`p-4 border rounded-lg bg-green-50 border-green-200 ${className}`}>
          <div className="flex items-center gap-2 text-green-800 mb-2">
            <Check className="h-5 w-5" />
            <span className="font-semibold">Payment Complete!</span>
          </div>
          <p className="text-green-700 text-sm mb-3">
            Your payment of {amount} sats has been processed successfully.
          </p>
          <Button onClick={resetPayment} variant="outline" size="sm">
            Make Another Payment
          </Button>
        </div>

        {/* Success Modal */}
        <Dialog open={showSuccessModal} onOpenChange={setShowSuccessModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-green-600">
                <Check className="h-5 w-5" />
                Invoice Paid!
              </DialogTitle>
            </DialogHeader>
            <div className="text-center py-4">
              <p className="text-lg mb-4">🎉 Your payment has been confirmed!</p>
              <p className="text-gray-600 mb-6">Amount: {amount} sats</p>
              <Button 
                onClick={() => {
                  setShowSuccessModal(false)
                  if (taskId) {
                    router.push(`/work/${taskId}`)
                  }
                }} 
                className="w-full"
              >
                Continue to Work
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </>
    )
  }

  if (invoice) {
    return (
      <div className={`p-4 border rounded-lg ${className}`}>
        <div className="text-center mb-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-yellow-800 mb-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="font-semibold">Waiting for Payment</span>
            </div>
            <p className="text-yellow-700 text-sm">
              Invoice generated for {amount} sats. Please pay using your Lightning wallet.
            </p>
          </div>
        </div>
        
        <div className="text-xs text-gray-500 mb-4">
          <p className="font-medium mb-1">Invoice:</p>
          <code className="break-all bg-gray-100 p-2 rounded block">
            {invoice.invoice.substring(0, 100)}...
          </code>
        </div>
        
        <Button onClick={resetPayment} variant="outline" className="w-full">
          Cancel
        </Button>
      </div>
    )
  }

  return (
    <div className={`p-4 border rounded-lg ${className}`}>
      <div className="space-y-4">
        <div>
          <Label htmlFor="amount">Amount (sats)</Label>
          <Input
            id="amount"
            type="number"
            value={amount}
            onChange={(e) => setAmount(parseInt(e.target.value) || 0)}
            min="1"
            placeholder="Enter amount in satoshis"
          />
        </div>
        
        <Button 
          onClick={handleGenerateInvoice}
          disabled={isGenerating || amount <= 0}
          className="w-full"
        >
          {isGenerating ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Generating Invoice...
            </>
          ) : (
            <>
              <Zap className="h-4 w-4 mr-2" />
              Generate Invoice & Submit Bid
            </>
          )}
        </Button>
      </div>
    </div>
  )
}