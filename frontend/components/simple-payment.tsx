"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Loader2, Copy, Check, Zap } from 'lucide-react'
import QRCode from 'react-qr-code'
import { useBitcoinConnect, InvoiceData, PaymentResult } from '@/hooks/use-bitcoin-connect'
import { useToast } from '@/hooks/use-toast'

interface SimplePaymentProps {
  onPaymentSuccess?: (result: PaymentResult) => void
  onInvoiceGenerated?: (invoice: InvoiceData) => void
  defaultAmount?: number
  memo?: string
  className?: string
}

export function SimplePayment({ 
  onPaymentSuccess, 
  onInvoiceGenerated,
  defaultAmount = 100,
  memo = "Payment",
  className = ""
}: SimplePaymentProps) {
  const [amount, setAmount] = useState(defaultAmount)
  const [invoice, setInvoice] = useState<InvoiceData | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isPaying, setIsPaying] = useState(false)
  const [copied, setCopied] = useState(false)
  const [paymentComplete, setPaymentComplete] = useState(false)
  
  const { toast } = useToast()
  const { isLoaded, generateInvoice, payInvoice } = useBitcoinConnect()

  const handleGenerateInvoice = async () => {
    try {
      setIsGenerating(true)
      const invoiceData = await generateInvoice(amount, memo)
      setInvoice(invoiceData)
      onInvoiceGenerated?.(invoiceData)
      toast({
        title: "Invoice Generated",
        description: `Generated invoice for ${amount} sats`,
      })
    } catch (error) {
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

  const handlePayInvoice = async () => {
    if (!invoice) return
    
    try {
      setIsPaying(true)
      const result = await payInvoice(invoice.paymentRequest)
      setPaymentComplete(true)
      toast({
        title: "Payment Successful! ⚡",
        description: "Your payment has been processed successfully.",
      })
      onPaymentSuccess?.(result)
    } catch (error) {
      console.error('Error paying invoice:', error)
      toast({
        title: "Payment Failed",
        description: "Failed to process payment. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsPaying(false)
    }
  }

  const copyToClipboard = async () => {
    if (invoice?.paymentRequest) {
      try {
        await navigator.clipboard.writeText(invoice.paymentRequest)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
        toast({
          title: "Copied!",
          description: "Invoice copied to clipboard",
        })
      } catch (error) {
        console.error('Failed to copy:', error)
      }
    }
  }

  const resetPayment = () => {
    setInvoice(null)
    setPaymentComplete(false)
    setCopied(false)
  }

  if (paymentComplete) {
    return (
      <Card className={`w-full max-w-md ${className}`}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-600">
            <Check className="h-5 w-5" />
            Payment Complete!
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 mb-4">
            Your payment of {amount} sats has been processed successfully.
          </p>
          <Button onClick={resetPayment} variant="outline" className="w-full">
            Make Another Payment
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={`w-full max-w-md ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-orange-500" />
          Lightning Payment {!isLoaded && "(Loading Bitcoin Connect...)"}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {!invoice ? (
          <>
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
                  Generate Invoice
                </>
              )}
            </Button>
          </>
        ) : (
          <>
            <div className="text-center space-y-4">
              <div className="bg-white p-4 rounded-lg border">
                <QRCode 
                  value={invoice.paymentRequest}
                  size={200}
                  level="M"
                />
              </div>
              
              <div className="text-sm">
                <p className="font-medium mb-2">Amount: {amount} sats</p>
                <div className="flex items-center gap-2">
                  <code className="flex-1 p-2 bg-gray-100 rounded text-xs break-all">
                    {invoice.paymentRequest.substring(0, 50)}...
                  </code>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={copyToClipboard}
                  >
                    {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button 
                onClick={handlePayInvoice}
                disabled={isPaying || !isLoaded}
                className="flex-1"
              >
                {isPaying ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Zap className="h-4 w-4 mr-2" />
                    Pay with Wallet
                  </>
                )}
              </Button>
              
              <Button 
                onClick={resetPayment}
                variant="outline"
              >
                Cancel
              </Button>
            </div>

            {/* Fallback payment options */}
            <div className="text-center text-sm text-gray-500">
              <p>Scan QR code with your lightning wallet or copy the invoice</p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}