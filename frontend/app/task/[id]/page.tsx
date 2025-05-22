"use client"

import { useState, useEffect, use } from "react"
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { ndk, ensureConnected, useNostrUser, createSignedEvent, getTagValue } from "@/lib/nostr"
import { NDKEvent, NDKFilter } from '@nostr-dev-kit/ndk'
import { SimplePayment } from "@/components/simple-payment"
import { InvoiceData, PaymentResult } from "@/hooks/use-bitcoin-connect"

interface TaskPageProps {
  params: Promise<{
    id: string
  }>
}

export default function TaskPage({ params }: TaskPageProps) {
  const [task, setTask] = useState<NDKEvent | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [showPayment, setShowPayment] = useState(false)
  const [bidAmount, setBidAmount] = useState(100)
  const { user } = useNostrUser()
  const { id: taskId } = use(params)

  useEffect(() => {
    loadTask()
  }, [taskId])

  async function loadTask() {
    try {
      setLoading(true)
      setError(null)
      
      await ensureConnected()
      
      const filter: NDKFilter = {
        ids: [taskId]
      }
      
      const events = await ndk.fetchEvents(filter)
      const eventsArray = Array.from(events)
      
      if (eventsArray.length > 0) {
        setTask(eventsArray[0])
      } else {
        setError("Task not found")
      }
    } catch (e) {
      console.error("Error loading task:", e)
      setError("Failed to load task")
    } finally {
      setLoading(false)
    }
  }

  async function handleBidClick() {
    if (!user || !task) return
    setShowPayment(true)
  }

  async function handleInvoiceGenerated(invoice: InvoiceData) {
    if (!user || !task) return

    try {
      setSubmitting(true)
      
      // Create a bid event (kind 7000) with the real invoice
      const tags = [
        ["e", task.id], // Reference to the original task
        ["p", task.author.pubkey], // Tag the task creator
        ["amount", bidAmount.toString()], // Bid amount in sats
        ["bolt11", invoice.paymentRequest] // Real lightning invoice
      ]
      
      const bidEvent = await createSignedEvent(
        7000,
        `I'd like to complete this task for ${bidAmount} sats`,
        tags
      )
      
      if (bidEvent) {
        await bidEvent.publish()
        console.log("Bid submitted successfully with invoice:", invoice.paymentRequest.substring(0, 50) + "...")
      } else {
        alert("Failed to submit bid")
      }
    } catch (e) {
      console.error("Error submitting bid:", e)
      alert("Failed to submit bid")
    } finally {
      setSubmitting(false)
    }
  }

  async function handlePaymentSuccess(result: PaymentResult) {
    console.log("Payment successful:", result)
    alert("Payment completed! Your bid has been submitted successfully.")
    setShowPayment(false)
  }

  if (loading) {
    return (
      <div className="container py-12 flex justify-center items-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#757575]" />
        <span className="ml-2">Loading task...</span>
      </div>
    )
  }

  if (error || !task) {
    return (
      <div className="container py-12">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error || "Task not found"}</p>
          <Link href="/available-tasks">
            <Button className="bg-[#2c2c2c] hover:bg-[#1e1e1e]">Back to Available Tasks</Button>
          </Link>
        </div>
      </div>
    )
  }

  const imageUrl = getTagValue(task, 'image') || getTagValue(task, 'img')
  const description = getTagValue(task, 'description') || getTagValue(task, 'desc') || task.content
  const maxPrice = getTagValue(task, 'max_price')
  const title = getTagValue(task, 'title') || getTagValue(task, 'name') || 
    (description && description.length < 50 ? description : `Task ${task.id.substring(0, 8)}...`)

  return (
    <div className="container py-12">
      <div className="mb-6">
        <Link href="/available-tasks" className="text-[#757575] hover:text-[#f5a623] flex items-center gap-2">
          ← Back to Available Tasks
        </Link>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div>
          {imageUrl && (
            <div className="aspect-video relative mb-4 border rounded-lg overflow-hidden">
              <Image 
                src={imageUrl} 
                alt="Task preview" 
                fill 
                className="object-cover"
                onError={(e) => {
                  const target = e.target as HTMLImageElement
                  target.src = "/placeholder.svg?height=400&width=600"
                }}
              />
            </div>
          )}

          <div className="border rounded-lg p-4 mt-4">
            <h3 className="font-semibold mb-2">Task Details</h3>
            <ul className="space-y-2 text-[#757575]">
              <li>
                <span className="font-medium text-[#2c2c2c]">Task ID:</span> {taskId.substring(0, 16)}...
              </li>
              <li>
                <span className="font-medium text-[#2c2c2c]">Posted:</span> {
                  new Date((task.created_at || 0) * 1000).toLocaleDateString()
                }
              </li>
              {maxPrice && (
                <li>
                  <span className="font-medium text-[#2c2c2c]">Max Reward:</span> {maxPrice} sats
                </li>
              )}
              <li>
                <span className="font-medium text-[#2c2c2c]">Author:</span> {task.author.pubkey.substring(0, 16)}...
              </li>
            </ul>
          </div>
        </div>

        <div>
          <h1 className="text-2xl font-bold text-[#1e1e1e] mb-4">{title}</h1>
          <p className="text-[#757575] mb-6">{description}</p>

          <div className="border rounded-lg p-6 mb-6">
            <h3 className="font-semibold mb-4">Task Instructions</h3>
            <div className="text-[#757575] whitespace-pre-wrap">
              {description || "No specific instructions provided. Please review the image and provide assistance as requested."}
            </div>
          </div>

          <div className="space-y-4">
            {user ? (
              !showPayment ? (
                <div className="flex gap-4">
                  <Button 
                    onClick={handleBidClick}
                    className="bg-[#2c2c2c] hover:bg-[#1e1e1e]"
                  >
                    Submit Bid
                  </Button>
                  <Button variant="outline" className="border-[#2c2c2c] text-[#2c2c2c] hover:bg-[#f5f5f5]">
                    Save for Later
                  </Button>
                </div>
              ) : (
                <div>
                  <h3 className="font-semibold mb-4">Generate Invoice & Submit Bid</h3>
                  <SimplePayment
                    defaultAmount={bidAmount}
                    memo={`Bid for task: ${task.id.substring(0, 16)}...`}
                    onInvoiceGenerated={handleInvoiceGenerated}
                    onPaymentSuccess={handlePaymentSuccess}
                    className="mx-auto"
                  />
                  <div className="mt-4 text-center">
                    <Button 
                      variant="outline" 
                      onClick={() => setShowPayment(false)}
                      className="text-sm"
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              )
            ) : (
              <p className="text-[#757575]">Please login to submit a bid</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}