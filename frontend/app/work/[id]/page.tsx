"use client"

import { useState, useEffect, use } from "react"
import { Button } from "@/components/ui/button"
import { Loader2, Check, Send, Code, Image as ImageIcon } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { Textarea } from "@/components/ui/textarea"
import { ndk, ensureConnected, useNostrUser, createSignedEvent, getTagValue } from "@/lib/nostr"
import { NDKEvent, NDKFilter } from '@nostr-dev-kit/ndk'
import { InteractiveImage } from "@/components/interactive-image"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription } from "@/components/ui/alert"

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
  const [actions, setActions] = useState<any[]>([])
  const [mode, setMode] = useState<'interactive' | 'manual'>('interactive')
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
    if (!user || !task) return
    
    // Check if we have content to submit
    if (mode === 'manual' && !instructions.trim()) {
      alert("Please provide instructions")
      return
    }
    
    if (mode === 'interactive' && actions.length === 0) {
      alert("Please record at least one action")
      return
    }

    try {
      setSubmitting(true)
      
      // Prepare content based on mode
      let content = ''
      if (mode === 'interactive') {
        // Convert actions to the expected JSON format
        const formattedActions = actions.map(action => {
          if (action.type === 'drag' && action.start && action.end) {
            return {
              type: action.type,
              start: { x: action.start.x, y: action.start.y },
              end: { x: action.end.x, y: action.end.y }
            }
          } else {
            return {
              type: action.type,
              x: action.x,
              y: action.y
            }
          }
        })
        
        content = JSON.stringify({ actions: formattedActions }, null, 2)
      } else {
        content = instructions.trim()
      }
      
      // Create a result event (kind 6109) with the work
      const tags = [
        ["e", task.id], // Reference to the original task
        ["p", task.author.pubkey], // Tag the task creator
        ["result", "completed"], // Mark as completed
        ["format", mode === 'interactive' ? "json" : "text"] // Indicate format type
      ]
      
      const resultEvent = await createSignedEvent(
        6109,
        content,
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

      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1e1e1e] mb-2">{title}</h1>
          <p className="text-[#757575]">{description}</p>
        </div>

        <div>
            
            <Tabs value={mode} onValueChange={(v) => setMode(v as 'interactive' | 'manual')} className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="interactive">
                  <ImageIcon className="h-4 w-4 mr-2" />
                  Interactive Mode
                </TabsTrigger>
                <TabsTrigger value="manual">
                  <Code className="h-4 w-4 mr-2" />
                  Manual Mode
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="interactive" className="space-y-4">
                <Alert>
                  <AlertDescription>
                    Click on the image to record actions. The AI will execute these actions in the order you create them.
                  </AlertDescription>
                </Alert>
                
                {imageUrl ? (
                  <InteractiveImage
                    src={imageUrl}
                    alt="Task screenshot"
                    onActionsChange={setActions}
                  />
                ) : (
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                    <p className="text-gray-500">No image available for this task</p>
                  </div>
                )}
                
                {actions.length > 0 && (
                  <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                    <h4 className="text-sm font-medium mb-2">JSON Output Preview:</h4>
                    <pre className="text-xs overflow-x-auto">
                      {JSON.stringify({
                        actions: actions.map(action => {
                          if (action.type === 'drag' && action.start && action.end) {
                            return {
                              type: action.type,
                              start: { x: action.start.x, y: action.start.y },
                              end: { x: action.end.x, y: action.end.y }
                            }
                          } else {
                            return {
                              type: action.type,
                              x: action.x,
                              y: action.y
                            }
                          }
                        })
                      }, null, 2)}
                    </pre>
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="manual" className="space-y-4">
                <div>
                  <label htmlFor="instructions" className="block text-sm font-medium mb-2">
                    Instructions for the AI Agent
                  </label>
                  <Textarea
                    id="instructions"
                    placeholder="Provide detailed step-by-step instructions. For example:
                    
1. Click on the Safari icon located at coordinates (50, 30)
2. Wait for the browser to open
3. The Safari icon is blue and has a compass design

Be specific about coordinates (use percentages 0-100), colors, and visual elements."
                    value={instructions}
                    onChange={(e) => setInstructions(e.target.value)}
                    rows={12}
                    className="resize-none"
                  />
                  <p className="text-xs text-[#757575] mt-1">
                    Use percentage coordinates (0-100) for better accuracy across different screen sizes.
                  </p>
                </div>
              </TabsContent>
            </Tabs>

            <div className="mt-4">
              <Button
                onClick={handleSubmitWork}
                disabled={submitting || (!instructions.trim() && mode === 'manual') || (actions.length === 0 && mode === 'interactive') || !user}
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
                <p className="text-[#757575] text-sm text-center mt-2">
                  Please login with Nostr to submit your work
                </p>
              )}
            </div>
        </div>
      </div>
    </div>
  )
}