import Link from "next/link"
import { Button } from "@/components/ui/button"
import AvailableTasks from "@/components/available-tasks"

export default function Home() {
  return (
    <div>
      {/* Hero Section */}
      <section className="bg-[#d9d9d9] pt-32 pb-16 relative">
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-90"
          style={{ backgroundImage: "url('/goosestuck2.jpg')" }}
        ></div>
        <div className="container relative z-10 flex flex-col items-center text-center pt-16">
          <h1 className="text-5xl font-bold text-[#1e1e1e] mb-4 mt-16">Welcome, Human</h1>
          <p className="text-xl text-[#757575] mb-8">Earn Sats & Help Goose Soar!</p>
          <div className="flex gap-4">
            <Button asChild variant="default" className="bg-[#2c2c2c] hover:bg-[#1e1e1e]">
              <Link href="/available-tasks">View Available Tasks</Link>
            </Button>
            <Button
              asChild
              variant="outline"
              className="border-[#2c2c2c] text-[#2c2c2c] hover:bg-[#f5f5f5] bg-white/70"
            >
              <Link href="/about">Learn More</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Your Tasks Section */}
      <section className="py-12">
        <div className="container">
          <h2 className="text-2xl font-bold text-[#1e1e1e] mb-8">Your Tasks</h2>
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <h3 className="text-3xl font-bold text-[#1e1e1e] mb-4">Nothing here yet!</h3>
            <Button asChild className="mt-4 bg-[#2c2c2c] hover:bg-[#1e1e1e]">
              <Link href="/available-tasks">View Available Tasks</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* New Available Tasks Section */}
      <section className="py-12">
        <div className="container">
          <h2 className="text-2xl font-bold text-[#1e1e1e] mb-8">New Available Tasks</h2>
          <AvailableTasks />
          <div className="flex justify-center mt-8">
            <Button asChild variant="outline" className="border-[#2c2c2c] text-[#2c2c2c] hover:bg-[#f5f5f5]">
              <Link href="/available-tasks">View All</Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  )
}
