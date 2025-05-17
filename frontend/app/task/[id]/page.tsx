import { Button } from "@/components/ui/button"
import Image from "next/image"
import Link from "next/link"

interface TaskPageProps {
  params: {
    id: string
  }
}

export default function TaskPage({ params }: TaskPageProps) {
  // In a real app, you would fetch task data based on the ID
  const taskId = params.id

  return (
    <div className="container py-12">
      <div className="mb-6">
        <Link href="/available-tasks" className="text-[#757575] hover:text-[#f5a623] flex items-center gap-2">
          ← Back to Available Tasks
        </Link>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <div className="aspect-video relative mb-4 border rounded-lg overflow-hidden">
            <Image src="/captcha-task.png" alt="Task preview" fill className="object-cover" />
          </div>

          <div className="border rounded-lg p-4 mt-4">
            <h3 className="font-semibold mb-2">Task Details</h3>
            <ul className="space-y-2 text-[#757575]">
              <li>
                <span className="font-medium text-[#2c2c2c]">Task ID:</span> {taskId}
              </li>
              <li>
                <span className="font-medium text-[#2c2c2c]">Posted:</span> May 15, 2023
              </li>
              <li>
                <span className="font-medium text-[#2c2c2c]">Reward:</span> 100 sats
              </li>
              <li>
                <span className="font-medium text-[#2c2c2c]">Estimated time:</span> &lt; 1 minute
              </li>
              <li>
                <span className="font-medium text-[#2c2c2c]">Difficulty:</span> Easy
              </li>
            </ul>
          </div>
        </div>

        <div>
          <h1 className="text-2xl font-bold text-[#1e1e1e] mb-4">Human Verification Captcha</h1>
          <p className="text-[#757575] mb-6">
            Complete the puzzle by dragging the puzzle piece to the correct location in the image. This helps websites
            verify that you are a human and not an automated bot.
          </p>

          <div className="border rounded-lg p-6 mb-6">
            <h3 className="font-semibold mb-4">Task Instructions</h3>
            <ol className="list-decimal list-inside space-y-2 text-[#757575]">
              <li>Look at the image and identify the missing piece</li>
              <li>Drag the puzzle piece to the correct location</li>
              <li>Click submit when you're done</li>
              <li>You'll receive sats upon successful verification</li>
            </ol>
          </div>

          <div className="flex gap-4">
            <Button className="bg-[#2c2c2c] hover:bg-[#1e1e1e]">Bid Task</Button>
            <Button variant="outline" className="border-[#2c2c2c] text-[#2c2c2c] hover:bg-[#f5f5f5]">
              Save for Later
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
