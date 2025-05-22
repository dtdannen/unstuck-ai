// Dynamic imports to handle module loading
const loadBitcoinConnect = async () => {
  const { requestProvider } = await import('@getalby/bitcoin-connect')
  return { requestProvider }
}

const loadLightningTools = async () => {
  const { LightningAddress } = await import('@getalby/lightning-tools')
  return { LightningAddress }
}

export interface InvoiceData {
  paymentRequest: string
  paymentHash: string
  verify: string
  successAction?: {
    tag: string
    message?: string
    url?: string
  }
}

export interface PaymentResult {
  preimage: string
}

export class BitcoinConnectInvoice {
  private lightningAddress: any = null
  private invoice: InvoiceData | null = null
  private onPaymentCallback?: (result: PaymentResult) => void

  constructor(private lnAddress: string = 'hello@getalby.com') {
    this.initLightningAddress()
  }

  private async initLightningAddress() {
    const { LightningAddress } = await loadLightningTools()
    this.lightningAddress = new LightningAddress(this.lnAddress)
  }

  async generateInvoice(amountSats: number, memo?: string): Promise<InvoiceData> {
    if (!this.lightningAddress) {
      await this.initLightningAddress()
    }

    // Fetch the LNURL data
    await this.lightningAddress.fetch()
    
    // Request the invoice
    const invoiceRequest = {
      satoshi: amountSats,
      comment: memo || `Payment for ${amountSats} sats`
    }
    
    this.invoice = await this.lightningAddress.requestInvoice(invoiceRequest)
    return this.invoice
  }

  async payInvoice(): Promise<PaymentResult> {
    if (!this.invoice) {
      throw new Error('No invoice generated. Call generateInvoice first.')
    }

    try {
      const { requestProvider } = await loadBitcoinConnect()
      const provider = await requestProvider()
      const result = await provider.sendPayment(this.invoice.paymentRequest)
      
      if (this.onPaymentCallback) {
        this.onPaymentCallback(result)
      }
      
      return result
    } catch (error) {
      console.error('Payment failed:', error)
      throw error
    }
  }

  onPayment(callback: (result: PaymentResult) => void) {
    this.onPaymentCallback = callback
  }

  getInvoice(): InvoiceData | null {
    return this.invoice
  }

  getPaymentRequest(): string | null {
    return this.invoice?.paymentRequest || null
  }
}

// Utility function to check payment status
export async function checkPaymentStatus(paymentHash: string): Promise<boolean> {
  // This would typically check with your backend or lightning node
  // For now, we'll return a placeholder
  try {
    // In a real implementation, you'd check the payment status
    // against your lightning node or payment processor
    return false
  } catch (error) {
    console.error('Error checking payment status:', error)
    return false
  }
}

// React hook for Bitcoin Connect integration
export function useBitcoinConnect(lnAddress?: string) {
  const bitcoinConnect = new BitcoinConnectInvoice(lnAddress)
  
  return {
    generateInvoice: (amountSats: number, memo?: string) => 
      bitcoinConnect.generateInvoice(amountSats, memo),
    payInvoice: () => bitcoinConnect.payInvoice(),
    onPayment: (callback: (result: PaymentResult) => void) => 
      bitcoinConnect.onPayment(callback),
    getInvoice: () => bitcoinConnect.getInvoice(),
    getPaymentRequest: () => bitcoinConnect.getPaymentRequest()
  }
}