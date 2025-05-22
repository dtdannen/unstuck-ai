"use client"

import { useState, useEffect, use } from "react"
import { Button } from "@/components/ui/button"
import { Loader2, Check, Send } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { Textarea } from "@/components/ui/textarea"
import { ndk, ensureConnected, useNostrUser, createSignedEvent, getTagValue } from "@/lib/nostr"
import { NDKEvent, NDKFilter } from '@nostr-dev-kit/ndk'

interface WorkPageProps {
  params: Promise<{
    id: string
  }>
}

export default function WorkPage({ params }: WorkPageProps) {
  const [task, setTask] = useState<NDKEvent | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [workComplete, setWorkComplete] = useState(false)
  const [instructions, setInstructions] = useState('')
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

  async function handleSubmitWork() {
    if (!user || !task || !instructions.trim()) return

    try {
      setSubmitting(true)
      
      // Create a result event (kind 6109) with the work instructions
      const tags = [
        ["e", task.id], // Reference to the original task
        ["p", task.author.pubkey], // Tag the task creator
        ["result", "completed"] // Mark as completed
      ]
      
      const resultEvent = await createSignedEvent(
        6109,
        instructions.trim(),
        tags
      )
      
      if (resultEvent) {
        await resultEvent.publish()
        console.log("Work submitted successfully")
        setWorkComplete(true)
      } else {
        alert("Failed to submit work")
      }
    } catch (e) {
      console.error("Error submitting work:", e)
      alert("Failed to submit work")
    } finally {
      setSubmitting(false)
    }
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
  const title = getTagValue(task, 'title') || getTagValue(task, 'name') || 
    (description && description.length < 50 ? description : `Task ${task.id.substring(0, 8)}...`)

  if (workComplete) {
    return (
      <div className="container py-12">
        <div className="max-w-2xl mx-auto text-center">
          <div className="border rounded-lg p-8 bg-green-50 border-green-200">
            <div className="flex items-center justify-center gap-2 text-green-800 mb-4">
              <Check className="h-8 w-8" />
              <h1 className="text-2xl font-bold">Work Submitted!</h1>
            </div>
            <p className="text-green-700 mb-6">
              Your work has been submitted successfully. The task creator will review your submission.
            </p>
            <Link href="/available-tasks">
              <Button className="bg-[#2c2c2c] hover:bg-[#1e1e1e]">
                Find More Tasks
              </Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container py-12">
      <div className="mb-6">
        <Link href="/available-tasks" className="text-[#757575] hover:text-[#f5a623] flex items-center gap-2">
          ← Back to Available Tasks
        </Link>
      </div>

      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1e1e1e] mb-2">Complete Your Work</h1>
          <p className="text-[#757575]">Provide detailed instructions for the task below</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h2 className="text-xl font-semibold mb-4">Task Details</h2>
            
            {imageUrl && (
              <div className="aspect-video relative mb-4 border rounded-lg overflow-hidden">
                <Image 
                  src={imageUrl} 
                  alt="Task screenshot" 
                  fill 
                  className="object-cover"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement
                    target.src = "/placeholder.svg?height=400&width=600"
                  }}
                />
              </div>
            )}

            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-2">{title}</h3>
              <p className="text-[#757575] text-sm mb-4">{description}</p>
              
              <div className="text-xs text-[#757575]">
                <p><span className="font-medium">Task ID:</span> {taskId.substring(0, 16)}...</p>
                <p><span className="font-medium">Posted:</span> {
                  new Date((task.created_at || 0) * 1000).toLocaleDateString()
                }</p>
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-xl font-semibold mb-4">Your Work</h2>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="instructions" className="block text-sm font-medium mb-2">
                  Instructions for the AI Agent
                </label>
                <Textarea
                  id="instructions"
                  placeholder="Provide detailed step-by-step instructions. For example:
                  
1. Click on the Safari icon located at coordinates (120, 45)
2. Wait for the browser to open
3. The Safari icon is blue and has a compass design

Be specific about coordinates, colors, and visual elements to help the AI understand what to do."
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  rows={12}
                  className="resize-none"
                />
                <p className="text-xs text-[#757575] mt-1">
                  Be as detailed as possible - include click coordinates, visual descriptions, and step-by-step actions.
                </p>
              </div>

              <Button
                onClick={handleSubmitWork}
                disabled={submitting || !instructions.trim() || !user}
                className="w-full bg-[#2c2c2c] hover:bg-[#1e1e1e]"
              >
                {submitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Submitting Work...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Submit Work
                  </>
                )}
              </Button>

              {!user && (
                <p className="text-[#757575] text-sm text-center">
                  Please login with Nostr to submit your work
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}