"use client"

import Link from "next/link"
import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Loader2, User, Settings, LogOut, CheckSquare } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useNostrUser } from "@/lib/nostr"

export default function NostrLoginButton() {
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const { user, loading, login, logout } = useNostrUser()

  const handleLogin = async () => {
    await login()
  }

  const handleLogout = () => {
    logout()
    setDropdownOpen(false)
  }

  // Get display name from profile
  const displayName = user?.profile?.name || user?.profile?.displayName || 
    (user?.pubkey ? `${user.pubkey.substring(0, 10)}...` : "")

  // Get initials for avatar fallback
  const getInitials = () => {
    if (!displayName) return "U"
    return displayName.charAt(0).toUpperCase()
  }

  const handleAvatarClick = () => {
    setDropdownOpen(!dropdownOpen)
  }

  if (loading) {
    return (
      <Button disabled className="bg-[#2c2c2c] opacity-75 text-white">
        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
        Loading...
      </Button>
    )
  }

  return user ? (
    <div className="flex items-center gap-3">
      <div className="flex flex-col items-end">
        <span className="text-sm font-medium">{displayName}</span>
      </div>

      <DropdownMenu open={dropdownOpen} onOpenChange={setDropdownOpen}>
        <DropdownMenuTrigger asChild>
          <button className="focus:outline-none">
            <Avatar
              className="h-8 w-8 border border-[#e3e3e3] cursor-pointer hover:ring-2 hover:ring-[#f5a623] transition-all"
              onClick={handleAvatarClick}
            >
              <AvatarImage src={user.profile?.picture || "/placeholder.svg"} alt={displayName} />
              <AvatarFallback>{getInitials()}</AvatarFallback>
            </Avatar>
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent
          align="end"
          className="w-56 bg-white shadow-lg rounded-md border border-gray-200 py-1 mt-1"
        >
          <DropdownMenuLabel className="font-semibold px-3 py-2">My Account</DropdownMenuLabel>
          <DropdownMenuSeparator className="bg-gray-200 h-px my-1" />

          <DropdownMenuItem className="px-3 py-2 hover:bg-gray-100 cursor-pointer flex items-center gap-2">
            <User className="h-4 w-4" />
            <Link href="/profile" className="w-full">
              Profile
            </Link>
          </DropdownMenuItem>

          <DropdownMenuItem className="px-3 py-2 hover:bg-gray-100 cursor-pointer flex items-center gap-2">
            <CheckSquare className="h-4 w-4" />
            <Link href="/my-tasks" className="w-full">
              My Tasks
            </Link>
          </DropdownMenuItem>

          <DropdownMenuItem className="px-3 py-2 hover:bg-gray-100 cursor-pointer flex items-center gap-2">
            <Settings className="h-4 w-4" />
            <Link href="/settings" className="w-full">
              Settings
            </Link>
          </DropdownMenuItem>

          <DropdownMenuSeparator className="bg-gray-200 h-px my-1" />

          <DropdownMenuItem
            onClick={handleLogout}
            className="px-3 py-2 hover:bg-gray-100 cursor-pointer text-red-500 flex items-center gap-2"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  ) : (
    <Button onClick={handleLogin} disabled={loading} className="bg-[#2c2c2c] hover:bg-[#1e1e1e] text-white">
      {loading ? "Connecting..." : "Login with Nostr"}
    </Button>
  )
}