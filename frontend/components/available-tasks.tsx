"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Loader2 } from "lucide-react"
import Image from "next/image"

// Define the relays to use
const RELAYS = ["wss://relay.damus.io", "wss://relay.nostr.band", "wss://relay.primal.net", "wss://relay.dvmdash.live"]

interface TaskEvent {
  id: string
  pubkey: string
  created_at: number
  kind: number
  tags: string[][]
  content: string
  sig: string
}

interface TaskWithProfile {
  event: TaskEvent
  profile?: {
    name?: string
    picture?: string
    about?: string
  }
}

export default function AvailableTasks() {
  const [tasks, setTasks] = useState<TaskWithProfile[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTasks()
  }, [])

  async function fetchTasks() {
    if (typeof window === "undefined") return

    try {
      setLoading(true)
      setError(null)

      // Check if the library is available
      if (!window.nostrTools && !window.NostrTools) {
        console.error("Nostr tools not found in window object")
        setError("Nostr library not available. Please refresh the page.")
        setLoading(false)
        return
      }

      // Try to get the SimplePool constructor from either global object
      const nostrLib = window.nostrTools || window.NostrTools

      if (!nostrLib.SimplePool) {
        console.error("SimplePool not found in nostr library")
        setError("Nostr library not properly loaded. Please refresh the page.")
        setLoading(false)
        return
      }

      const pool = new nostrLib.SimplePool()
      const taskEvents: TaskWithProfile[] = []

      // Fetch kind 5109 events (tasks)
      const tasksPromise = new Promise<void>((resolve) => {
        const sub = pool.subscribeMany(
          RELAYS,
          [
            {
              kinds: [5109, 30006], // Include both kinds mentioned
              limit: 20,
            },
          ],
          {
            onevent(event) {
              console.log("Task event received:", event)
              taskEvents.push({ event })
            },
            oneose() {
              // End of stored events
              setTimeout(() => {
                sub.close()
                resolve()
              }, 1000) // Give a little extra time for any late events
            },
          },
        )
      })

      // Wait for tasks to be fetched
      await tasksPromise

      // If we have tasks, fetch profiles for the task creators
      if (taskEvents.length > 0) {
        const pubkeys = [...new Set(taskEvents.map((task) => task.event.pubkey))]

        const profilesPromise = new Promise<void>((resolve) => {
          const profileSub = pool.subscribeMany(
            RELAYS,
            [
              {
                kinds: [0],
                authors: pubkeys,
              },
            ],
            {
              onevent(event) {
                try {
                  const profile = JSON.parse(event.content)
                  // Update tasks with profile data
                  taskEvents.forEach((task) => {
                    if (task.event.pubkey === event.pubkey) {
                      task.profile = profile
                    }
                  })
                } catch (e) {
                  console.error("Failed to parse profile data:", e)
                }
              },
              oneose() {
                setTimeout(() => {
                  profileSub.close()
                  resolve()
                }, 1000)
              },
            },
          )
        })

        await profilesPromise
      }

      // Sort tasks by creation time (newest first)
      taskEvents.sort((a, b) => b.event.created_at - a.event.created_at)

      setTasks(taskEvents)

      // Close all connections
      pool.close(RELAYS)
    } catch (error) {
      console.error("Error fetching tasks:", error)
      setError("Failed to fetch tasks. Please try again later.")
    } finally {
      setLoading(false)
    }
  }

  // Function to extract image URL from tags
  function getImageUrl(task: TaskEvent): string | null {
    const imageTag = task.tags.find((tag) => tag[0] === "image" || tag[0] === "img")
    if (imageTag && imageTag.length > 1) {
      return imageTag[1]
    }

    // Also check for image URLs in content
    try {
      const contentObj = JSON.parse(task.content)
      if (contentObj.image) return contentObj.image
      if (contentObj.img) return contentObj.img
    } catch (e) {
      // Not JSON or doesn't have image field
    }

    return null
  }

  // Function to get task title
  function getTaskTitle(task: TaskEvent): string {
    // Check for title in tags
    const titleTag = task.tags.find((tag) => tag[0] === "title" || tag[0] === "name")
    if (titleTag && titleTag.length > 1) {
      return titleTag[1]
    }

    // Check for title in content
    try {
      const contentObj = JSON.parse(task.content)
      if (contentObj.title) return contentObj.title
      if (contentObj.name) return contentObj.name
    } catch (e) {
      // Not JSON or doesn't have title field
    }

    // If content is short, use it as title
    if (task.content && task.content.length < 50) {
      return task.content
    }

    // Fallback to task ID
    return `Task ${task.id.substring(0, 8)}...`
  }

  // Function to get task description
  function getTaskDescription(task: TaskEvent): string {
    // Check for description in tags
    const descTag = task.tags.find((tag) => tag[0] === "description" || tag[0] === "desc")
    if (descTag && descTag.length > 1) {
      return descTag[1]
    }

    // Check for description in content
    try {
      const contentObj = JSON.parse(task.content)
      if (contentObj.description) return contentObj.description
      if (contentObj.desc) return contentObj.desc
    } catch (e) {
      // If content is not JSON, use it as description
      if (task.content) {
        return task.content.length > 150 ? `${task.content.substring(0, 147)}...` : task.content
      }
    }

    return "No description available"
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[#757575]" />
        <span className="ml-2">Loading tasks...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">{error}</p>
        <Button onClick={fetchTasks} className="mt-4 bg-[#2c2c2c] hover:bg-[#1e1e1e]">
          Try Again
        </Button>
      </div>
    )
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-[#757575]">No tasks available at the moment.</p>
        <Button onClick={fetchTasks} className="mt-4 bg-[#2c2c2c] hover:bg-[#1e1e1e]">
          Refresh
        </Button>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {tasks.map((task) => {
        const imageUrl = getImageUrl(task.event)
        const title = getTaskTitle(task.event)
        const description = getTaskDescription(task.event)

        return (
          <Card key={task.event.id} className="overflow-hidden">
            <CardContent className="p-0">
              {imageUrl && (
                <div className="aspect-video relative">
                  <Image
                    src={imageUrl || "/placeholder.svg"}
                    alt={title}
                    fill
                    className="object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      target.src = "/placeholder.svg?height=256&width=256"
                    }}
                  />
                </div>
              )}
              <div className="p-4">
                <h3 className="font-semibold mb-2">{title}</h3>
                <p className="text-sm text-[#757575] mb-4">{description}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    {task.profile?.picture ? (
                      <Image
                        src={task.profile.picture || "/placeholder.svg"}
                        alt={task.profile.name || "Creator"}
                        width={24}
                        height={24}
                        className="rounded-full mr-2"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement
                          target.src = "/placeholder.svg?height=24&width=24"
                        }}
                      />
                    ) : (
                      <div className="w-6 h-6 rounded-full bg-[#e3e3e3] mr-2"></div>
                    )}
                    <span className="text-xs text-[#757575]">
                      {task.profile?.name || `${task.event.pubkey.substring(0, 8)}...`}
                    </span>
                  </div>
                  <span className="text-xs text-[#757575]">
                    {new Date(task.event.created_at * 1000).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div className="flex justify-end p-2 bg-[#f5f5f5]">
                <Button className="bg-[#2c2c2c] hover:bg-[#1e1e1e]">Bid Task</Button>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
