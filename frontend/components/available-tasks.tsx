"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Loader2 } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { fetchTasks, getCachedProfile, getTagValue } from "@/lib/nostr"
import { NDKEvent, NDKUser } from '@nostr-dev-kit/ndk'

interface TaskWithProfile {
  event: NDKEvent
  profile?: NDKUser
}

export default function AvailableTasks() {
  const [tasks, setTasks] = useState<TaskWithProfile[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadTasks()
  }, [])

  async function loadTasks() {
    try {
      setLoading(true)
      setError(null)

      // Fetch tasks from relays
      const events = await fetchTasks(20)
      console.log('Fetched tasks:', events)

      // Create task objects with events
      const tasksWithProfile: TaskWithProfile[] = events.map(event => ({
        event,
        profile: undefined
      }))

      // Fetch profiles for task creators
      const profilePromises = tasksWithProfile.map(async (task) => {
        try {
          const profile = await getCachedProfile(task.event.author.pubkey)
          task.profile = profile || undefined
        } catch (e) {
          console.warn(`Failed to fetch profile for ${task.event.author.pubkey}:`, e)
        }
      })

      await Promise.all(profilePromises)

      // Sort tasks by creation time (newest first)
      tasksWithProfile.sort((a, b) => (b.event.created_at || 0) - (a.event.created_at || 0))

      setTasks(tasksWithProfile)
    } catch (error) {
      console.error("Error loading tasks:", error)
      setError("Failed to load tasks. Please try again later.")
    } finally {
      setLoading(false)
    }
  }

  // Function to extract image URL from tags
  function getImageUrl(event: NDKEvent): string | null {
    const imageUrl = getTagValue(event, 'image') || getTagValue(event, 'img')
    if (imageUrl) return imageUrl

    // Also check for image URLs in content
    try {
      const contentObj = JSON.parse(event.content)
      if (contentObj.image) return contentObj.image
      if (contentObj.img) return contentObj.img
    } catch (e) {
      // Not JSON or doesn't have image field
    }

    return null
  }

  // Function to get task title
  function getTaskTitle(event: NDKEvent): string {
    // Check for title in tags
    const title = getTagValue(event, 'title') || getTagValue(event, 'name')
    if (title) return title

    // Check for description tag
    const description = getTagValue(event, 'description') || getTagValue(event, 'desc')
    if (description && description.length < 50) return description

    // Check for title in content
    try {
      const contentObj = JSON.parse(event.content)
      if (contentObj.title) return contentObj.title
      if (contentObj.name) return contentObj.name
    } catch (e) {
      // Not JSON or doesn't have title field
    }

    // If content is short, use it as title
    if (event.content && event.content.length < 50) {
      return event.content
    }

    // Fallback to task ID
    return `Task ${event.id.substring(0, 8)}...`
  }

  // Function to get task description
  function getTaskDescription(event: NDKEvent): string {
    // Check for description in tags
    const description = getTagValue(event, 'description') || getTagValue(event, 'desc')
    if (description) return description

    // Check for description in content
    try {
      const contentObj = JSON.parse(event.content)
      if (contentObj.description) return contentObj.description
      if (contentObj.desc) return contentObj.desc
    } catch (e) {
      // If content is not JSON, use it as description
      if (event.content) {
        return event.content.length > 150 ? `${event.content.substring(0, 147)}...` : event.content
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
        <Button onClick={loadTasks} className="mt-4 bg-[#2c2c2c] hover:bg-[#1e1e1e]">
          Try Again
        </Button>
      </div>
    )
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-[#757575]">No tasks available at the moment.</p>
        <Button onClick={loadTasks} className="mt-4 bg-[#2c2c2c] hover:bg-[#1e1e1e]">
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
                    {task.profile?.profile?.picture ? (
                      <Image
                        src={task.profile.profile.picture || "/placeholder.svg"}
                        alt={task.profile.profile.name || "Creator"}
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
                      {task.profile?.profile?.name || `${task.event.author.pubkey.substring(0, 8)}...`}
                    </span>
                  </div>
                  <span className="text-xs text-[#757575]">
                    {new Date((task.event.created_at || 0) * 1000).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div className="flex justify-end p-2 bg-[#f5f5f5]">
                <Link href={`/task/${task.event.id}`}>
                  <Button className="bg-[#2c2c2c] hover:bg-[#1e1e1e]">Bid Task</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}