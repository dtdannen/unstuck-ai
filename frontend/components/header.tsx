import Link from "next/link"
import Image from "next/image"
import NostrLoginButton from "@/components/nostr-login-button"

export default function Header() {
  return (
    <header className="border-b bg-white">
      <div className="container flex items-center justify-between py-4">
        <Link href="/" className="flex items-center">
          <Image src="/unstuckgoose.png" alt="Unstuck Logo" width={180} height={60} priority />
        </Link>
        <nav className="flex items-center gap-6">
          <Link href="/available-tasks" className="text-[#2c2c2c] hover:text-[#f5a623] transition-colors">
            Available Tasks
          </Link>
          <Link href="/about-us" className="text-[#2c2c2c] hover:text-[#f5a623] transition-colors">
            About Us
          </Link>
          <div className="h-6 w-px bg-[#2c2c2c] mx-2"></div>
          <NostrLoginButton />
        </nav>
      </div>
    </header>
  )
}
