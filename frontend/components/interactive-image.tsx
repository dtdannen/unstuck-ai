"use client"

import { useState, useRef, useCallback } from 'react'
import useMeasure from 'react-use-measure'
import Image from 'next/image'
import { X, MousePointer, Move, Maximize2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface Point {
  x: number // percentage (0-100)
  y: number // percentage (0-100)
}

interface Action {
  id: string
  type: 'click' | 'doubleClick' | 'drag' | 'moveMouse'
  x?: number
  y?: number
  start?: Point
  end?: Point
  timestamp: number
}

interface InteractiveImageProps {
  src: string
  alt: string
  onActionsChange?: (actions: Action[]) => void
  className?: string
}

export function InteractiveImage({ src, alt, onActionsChange, className }: InteractiveImageProps) {
  const [containerRef, containerBounds] = useMeasure()
  const imageRef = useRef<HTMLImageElement>(null)
  const [actions, setActions] = useState<Action[]>([])
  const [currentTool, setCurrentTool] = useState<'click' | 'doubleClick' | 'drag' | 'moveMouse'>('click')
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState<Point | null>(null)
  const [dragEnd, setDragEnd] = useState<Point | null>(null)
  const [hoveredAction, setHoveredAction] = useState<string | null>(null)
  
  // Get percentage coordinates from mouse event
  const getPercentageCoords = useCallback((e: React.MouseEvent): Point => {
    if (!imageRef.current) return { x: 0, y: 0 }
    
    const rect = imageRef.current.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width) * 100
    const y = ((e.clientY - rect.top) / rect.height) * 100
    
    return { x: Math.max(0, Math.min(100, x)), y: Math.max(0, Math.min(100, y)) }
  }, [])

  // Handle mouse down
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    const coords = getPercentageCoords(e)
    
    if (currentTool === 'drag') {
      setIsDragging(true)
      setDragStart(coords)
    }
  }, [currentTool, getPercentageCoords])

  // Handle mouse move
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isDragging && currentTool === 'drag') {
      const coords = getPercentageCoords(e)
      setDragEnd(coords)
    }
  }, [isDragging, currentTool, getPercentageCoords])

  // Handle mouse up
  const handleMouseUp = useCallback((e: React.MouseEvent) => {
    const coords = getPercentageCoords(e)
    
    if (currentTool === 'drag' && isDragging && dragStart) {
      const newAction: Action = {
        id: `action-${Date.now()}`,
        type: 'drag',
        start: dragStart,
        end: coords,
        timestamp: Date.now()
      }
      const updatedActions = [...actions, newAction]
      setActions(updatedActions)
      onActionsChange?.(updatedActions)
      setIsDragging(false)
      setDragStart(null)
      setDragEnd(null)
    } else if (currentTool === 'click' || currentTool === 'doubleClick' || currentTool === 'moveMouse') {
      const newAction: Action = {
        id: `action-${Date.now()}`,
        type: currentTool,
        x: coords.x,
        y: coords.y,
        timestamp: Date.now()
      }
      const updatedActions = [...actions, newAction]
      setActions(updatedActions)
      onActionsChange?.(updatedActions)
    }
  }, [currentTool, isDragging, dragStart, actions, getPercentageCoords, onActionsChange])

  // Remove an action
  const removeAction = useCallback((actionId: string) => {
    const updatedActions = actions.filter(a => a.id !== actionId)
    setActions(updatedActions)
    onActionsChange?.(updatedActions)
  }, [actions, onActionsChange])

  // Clear all actions
  const clearActions = useCallback(() => {
    setActions([])
    onActionsChange?.([])
  }, [onActionsChange])

  // Format action for display
  const formatAction = (action: Action): string => {
    switch (action.type) {
      case 'click':
        return `Click at (${action.x?.toFixed(1)}%, ${action.y?.toFixed(1)}%)`
      case 'doubleClick':
        return `Double-click at (${action.x?.toFixed(1)}%, ${action.y?.toFixed(1)}%)`
      case 'moveMouse':
        return `Move to (${action.x?.toFixed(1)}%, ${action.y?.toFixed(1)}%)`
      case 'drag':
        return `Drag from (${action.start?.x.toFixed(1)}%, ${action.start?.y.toFixed(1)}%) to (${action.end?.x.toFixed(1)}%, ${action.end?.y.toFixed(1)}%)`
      default:
        return 'Unknown action'
    }
  }

  return (
    <div className={cn("space-y-4", className)}>
      {/* Toolbar */}
      <div className="flex items-center gap-2 p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
        <span className="text-sm font-medium">Tool:</span>
        <div className="flex gap-1">
          <Button
            size="sm"
            variant={currentTool === 'click' ? 'default' : 'outline'}
            onClick={() => setCurrentTool('click')}
          >
            <MousePointer className="h-4 w-4 mr-1" />
            Click
          </Button>
          <Button
            size="sm"
            variant={currentTool === 'doubleClick' ? 'default' : 'outline'}
            onClick={() => setCurrentTool('doubleClick')}
          >
            <MousePointer className="h-4 w-4 mr-1" />
            Double Click
          </Button>
          <Button
            size="sm"
            variant={currentTool === 'drag' ? 'default' : 'outline'}
            onClick={() => setCurrentTool('drag')}
          >
            <Maximize2 className="h-4 w-4 mr-1" />
            Drag
          </Button>
          <Button
            size="sm"
            variant={currentTool === 'moveMouse' ? 'default' : 'outline'}
            onClick={() => setCurrentTool('moveMouse')}
          >
            <Move className="h-4 w-4 mr-1" />
            Move
          </Button>
        </div>
        <div className="ml-auto">
          <Button
            size="sm"
            variant="ghost"
            onClick={clearActions}
            disabled={actions.length === 0}
          >
            Clear All
          </Button>
        </div>
      </div>

      {/* Interactive Image */}
      <div 
        ref={containerRef}
        className="relative overflow-hidden rounded-lg border-2 border-gray-200 dark:border-gray-700"
        style={{ cursor: currentTool === 'drag' ? 'crosshair' : 'pointer' }}
      >
        <img 
          ref={imageRef}
          src={src} 
          alt={alt} 
          className="w-full h-auto select-none block" 
          draggable={false}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseMove={handleMouseMove}
        />
        
        {/* Action Markers */}
        {actions.map((action) => (
          <div key={action.id}>
            {(action.type === 'click' || action.type === 'doubleClick' || action.type === 'moveMouse') && (
              <div
                className={cn(
                  "absolute w-4 h-4 -translate-x-1/2 -translate-y-1/2 pointer-events-auto",
                  action.type === 'click' && "bg-blue-500 rounded-full",
                  action.type === 'doubleClick' && "bg-purple-500 rounded-full ring-2 ring-purple-300",
                  action.type === 'moveMouse' && "bg-green-500 rotate-45",
                  hoveredAction === action.id && "ring-4 ring-opacity-50"
                )}
                style={{ left: `${action.x}%`, top: `${action.y}%` }}
                onMouseEnter={() => setHoveredAction(action.id)}
                onMouseLeave={() => setHoveredAction(null)}
                onClick={(e) => {
                  e.stopPropagation()
                  removeAction(action.id)
                }}
              />
            )}
            
            {action.type === 'drag' && action.start && action.end && (
              <>
                {/* Drag start point */}
                <div
                  className="absolute w-4 h-4 bg-orange-500 rounded-full -translate-x-1/2 -translate-y-1/2"
                  style={{ left: `${action.start.x}%`, top: `${action.start.y}%` }}
                />
                {/* Drag line */}
                <svg
                  className="absolute inset-0 w-full h-full pointer-events-none"
                  style={{ overflow: 'visible' }}
                >
                  <line
                    x1={`${action.start.x}%`}
                    y1={`${action.start.y}%`}
                    x2={`${action.end.x}%`}
                    y2={`${action.end.y}%`}
                    stroke="orange"
                    strokeWidth="2"
                    strokeDasharray="5,5"
                  />
                </svg>
                {/* Drag end point */}
                <div
                  className="absolute w-4 h-4 bg-orange-600 rounded-full -translate-x-1/2 -translate-y-1/2"
                  style={{ left: `${action.end.x}%`, top: `${action.end.y}%` }}
                  onMouseEnter={() => setHoveredAction(action.id)}
                  onMouseLeave={() => setHoveredAction(null)}
                  onClick={(e) => {
                    e.stopPropagation()
                    removeAction(action.id)
                  }}
                />
              </>
            )}
          </div>
        ))}
        
        {/* Current drag preview */}
        {isDragging && dragStart && dragEnd && (
          <>
            <div
              className="absolute w-4 h-4 bg-orange-500 rounded-full -translate-x-1/2 -translate-y-1/2 opacity-50"
              style={{ left: `${dragStart.x}%`, top: `${dragStart.y}%` }}
            />
            <svg
              className="absolute inset-0 w-full h-full pointer-events-none"
              style={{ overflow: 'visible' }}
            >
              <line
                x1={`${dragStart.x}%`}
                y1={`${dragStart.y}%`}
                x2={`${dragEnd.x}%`}
                y2={`${dragEnd.y}%`}
                stroke="orange"
                strokeWidth="2"
                strokeDasharray="5,5"
                opacity="0.5"
              />
            </svg>
            <div
              className="absolute w-4 h-4 bg-orange-600 rounded-full -translate-x-1/2 -translate-y-1/2 opacity-50"
              style={{ left: `${dragEnd.x}%`, top: `${dragEnd.y}%` }}
            />
          </>
        )}
      </div>

      {/* Actions List */}
      {actions.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Recorded Actions ({actions.length})</h4>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {actions.map((action, index) => (
              <div
                key={action.id}
                className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-900 rounded text-sm"
                onMouseEnter={() => setHoveredAction(action.id)}
                onMouseLeave={() => setHoveredAction(null)}
              >
                <Badge variant="outline" className="font-mono">{index + 1}</Badge>
                <span className="flex-1">{formatAction(action)}</span>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => removeAction(action.id)}
                  className="h-6 w-6 p-0"
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}