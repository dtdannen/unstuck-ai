"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2, Clock, CheckCircle, Send, DollarSign } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { ndk, ensureConnected, useNostrUser, getTagValue } from "@/lib/nostr"
import { NDKEvent, NDKFilter } from '@nostr-dev-kit/ndk'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"

interface TaskWithDetails {
  originalTask: NDKEvent
  bid?: NDKEvent
  work?: NDKEvent
  status: 'bidding' | 'working' | 'completed'
  bidAmount?: number
  invoice?: string
}

// Helper functions
function getTaskTitle(event: NDKEvent): string {
  return getTagValue(event, 'title') || 
         getTagValue(event, 'name') || 
         event.content.substring(0, 50) + (event.content.length > 50 ? '...' : '') ||
         `Task ${event.id.substring(0, 8)}...`
}

function getImageUrl(event: NDKEvent): string | null {
  return getTagValue(event, 'image') || getTagValue(event, 'img')
}

export default function MyTasksPage() {
  const [tasks, setTasks] = useState<TaskWithDetails[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useNostrUser()

  useEffect(() => {
    if (user) {
      loadMyTasks()
    } else {
      setLoading(false)
    }
  }, [user])

  async function loadMyTasks() {
    if (!user) return

    try {
      setLoading(true)
      setError(null)
      
      await ensureConnected()
      
      // Fetch all bids (kind 7000) created by the current user
      const bidFilter: NDKFilter = {
        kinds: [7000],
        authors: [user.pubkey]
      }
      
      const bids = await ndk.fetchEvents(bidFilter)
      console.log(`Found ${bids.size} bids by user`)
      
      // Fetch all work submissions (kind 6109) created by the current user
      const workFilter: NDKFilter = {
        kinds: [6109],
        authors: [user.pubkey]
      }
      
      const workSubmissions = await ndk.fetchEvents(workFilter)
      console.log(`Found ${workSubmissions.size} work submissions by user`)
      
      // Create a map to group by task ID
      const taskMap = new Map<string, TaskWithDetails>()
      
      // Process bids
      for (const bid of bids) {
        const taskId = getTagValue(bid, 'e') // Get referenced task ID
        if (!taskId) continue
        
        const bidAmount = parseInt(getTagValue(bid, 'amount') || '0')
        const invoice = getTagValue(bid, 'bolt11')
        
        taskMap.set(taskId, {
          originalTask: null as any, // Will fetch later
          bid,
          status: 'bidding',
          bidAmount,
          invoice
        })
      }
      
      // Process work submissions
      for (const work of workSubmissions) {
        const taskId = getTagValue(work, 'e') // Get referenced task ID
        if (!taskId) continue
        
        const existing = taskMap.get(taskId)
        if (existing) {
          existing.work = work
          existing.status = 'completed'
        } else {
          taskMap.set(taskId, {
            originalTask: null as any,
            work,
            status: 'completed'
          })
        }
      }
      
      // Fetch original tasks
      const taskIds = Array.from(taskMap.keys())
      if (taskIds.length > 0) {
        const tasksFilter: NDKFilter = {
          ids: taskIds
        }
        
        const originalTasks = await ndk.fetchEvents(tasksFilter)
        
        // Update map with original tasks
        for (const task of originalTasks) {
          const taskDetails = taskMap.get(task.id)
          if (taskDetails) {
            taskDetails.originalTask = task
            
            // Check if we have a bid but no work yet - means we're working on it
            if (taskDetails.bid && !taskDetails.work) {
              taskDetails.status = 'working'
            }
          }
        }
      }
      
      // Convert map to array and filter out tasks without original task data
      const tasksArray = Array.from(taskMap.values())
        .filter(task => task.originalTask)
        .sort((a, b) => {
          // Sort by most recent activity
          const aTime = Math.max(
            a.bid?.created_at || 0,
            a.work?.created_at || 0,
            a.originalTask?.created_at || 0
          )
          const bTime = Math.max(
            b.bid?.created_at || 0,
            b.work?.created_at || 0,
            b.originalTask?.created_at || 0
          )
          return bTime - aTime
        })
      
      setTasks(tasksArray)
      console.log(`Loaded ${tasksArray.length} tasks with details`)
      
    } catch (e) {
      console.error("Error loading tasks:", e)
      setError("Failed to load your tasks")
    } finally {
      setLoading(false)
    }
  }

  function getStatusBadge(status: string) {
    switch (status) {
      case 'bidding':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800"><Clock className="h-3 w-3 mr-1" />Pending</Badge>
      case 'working':
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800"><Send className="h-3 w-3 mr-1" />In Progress</Badge>
      case 'completed':
        return <Badge variant="secondary" className="bg-green-100 text-green-800"><CheckCircle className="h-3 w-3 mr-1" />Completed</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  if (!user) {
    return (
      <div className="container py-12">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">My Tasks</h1>
          <p className="text-[#757575] mb-6">Please login to view your tasks</p>
          <Link href="/">
            <Button className="bg-[#2c2c2c] hover:bg-[#1e1e1e]">Go to Homepage</Button>
          </Link>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="container py-12 flex justify-center items-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#757575]" />
        <span className="ml-2">Loading your tasks...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container py-12">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <Button onClick={loadMyTasks} className="bg-[#2c2c2c] hover:bg-[#1e1e1e]">
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  const biddingTasks = tasks.filter(t => t.status === 'bidding')
  const workingTasks = tasks.filter(t => t.status === 'working')
  const completedTasks = tasks.filter(t => t.status === 'completed')

  return (
    <div className="container py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[#1e1e1e] mb-2">My Tasks</h1>
        <p className="text-[#757575]">Track your bids, ongoing work, and completed tasks</p>
      </div>

      <Tabs defaultValue="all" className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="all">All Tasks ({tasks.length})</TabsTrigger>
          <TabsTrigger value="bidding">Pending Bids ({biddingTasks.length})</TabsTrigger>
          <TabsTrigger value="working">In Progress ({workingTasks.length})</TabsTrigger>
          <TabsTrigger value="completed">Completed ({completedTasks.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          <TaskList tasks={tasks} />
        </TabsContent>

        <TabsContent value="bidding">
          <TaskList tasks={biddingTasks} emptyMessage="No pending bids" />
        </TabsContent>

        <TabsContent value="working">
          <TaskList tasks={workingTasks} emptyMessage="No tasks in progress" />
        </TabsContent>

        <TabsContent value="completed">
          <TaskList tasks={completedTasks} emptyMessage="No completed tasks" />
        </TabsContent>
      </Tabs>
    </div>
  )

  function TaskList({ tasks, emptyMessage = "No tasks found" }: { tasks: TaskWithDetails[], emptyMessage?: string }) {
  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-[#757575]">{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div className="grid gap-4">
      {tasks.map((task) => {
        const title = getTaskTitle(task.originalTask)
        const imageUrl = getImageUrl(task.originalTask)
        const taskId = task.originalTask.id

        return (
          <Card key={taskId} className="overflow-hidden hover:shadow-lg transition-shadow">
            <CardContent className="p-0">
              <div className="flex items-start gap-4 p-4">
                {imageUrl && (
                  <div className="w-24 h-24 relative flex-shrink-0 rounded-lg overflow-hidden">
                    <Image
                      src={imageUrl}
                      alt={title}
                      fill
                      className="object-cover"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement
                        target.src = "/placeholder.svg?height=96&width=96"
                      }}
                    />
                  </div>
                )}
                
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-lg">{title}</h3>
                    {getStatusBadge(task.status)}
                  </div>
                  
                  <p className="text-sm text-[#757575] mb-3">
                    {task.originalTask.content.substring(0, 100)}
                    {task.originalTask.content.length > 100 ? '...' : ''}
                  </p>
                  
                  <div className="flex items-center gap-4 text-sm text-[#757575]">
                    {task.bidAmount && (
                      <span className="flex items-center gap-1">
                        <DollarSign className="h-3 w-3" />
                        {task.bidAmount} sats
                      </span>
                    )}
                    <span>
                      Created: {new Date((task.originalTask.created_at || 0) * 1000).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <div className="mt-3">
                    {task.status === 'bidding' && (
                      <p className="text-sm text-yellow-700 bg-yellow-50 px-3 py-1 rounded-md inline-block">
                        Waiting for task creator to accept your bid
                      </p>
                    )}
                    
                    {task.status === 'working' && (
                      <Link href={`/work/${taskId}`}>
                        <Button size="sm" className="bg-[#2c2c2c] hover:bg-[#1e1e1e]">
                          Continue Working
                        </Button>
                      </Link>
                    )}
                    
                    {task.status === 'completed' && task.work && (
                      <div className="text-sm text-green-700 bg-green-50 px-3 py-1 rounded-md">
                        Completed on {new Date((task.work.created_at || 0) * 1000).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
  }
}