import AvailableTasksComponent from "@/components/available-tasks"
import { Button } from "@/components/ui/button"
import Image from "next/image"

export default function AvailableTasksPage() {
  return (
    <div className="container py-12">
      <h1 className="text-3xl font-bold text-[#1e1e1e] mb-8">Available Tasks</h1>
      <AvailableTasksComponent />
    </div>
  )
}

// AvailableTasks component can be defined in a separate file if needed
// For now, it's included here for completeness
const AvailableTasks = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Task Card 1 */}
      <div className="border rounded-lg overflow-hidden">
        <div className="p-4">
          <div className="aspect-video relative mb-4">
            <Image src="/majestic-mountain-vista.png" alt="Mountain landscape" fill className="object-cover rounded" />
          </div>
          <h3 className="font-semibold mb-2">Human Verification Captcha</h3>
          <p className="text-sm text-[#757575]">
            Complete the puzzle by dragging the puzzle piece to the correct location.
          </p>
        </div>
        <div className="flex justify-end p-2 bg-[#f5f5f5]">
          <Button className="bg-[#2c2c2c] hover:bg-[#1e1e1e]">Bid Task</Button>
        </div>
      </div>

      {/* Task Card 2 */}
      <div className="border rounded-lg overflow-hidden">
        <div className="p-4">
          <div className="aspect-video relative mb-4 bg-[#e3e3e3] flex items-center justify-center">
            <p className="text-[#757575]">What is 2 + 2 * (common's) cap?</p>
          </div>
          <h3 className="font-semibold mb-2">Text Input Captcha</h3>
          <p className="text-sm text-[#757575]">
            To help prevent automated submissions, provide the value if you are human.
          </p>
        </div>
        <div className="flex justify-end p-2 bg-[#f5f5f5]">
          <Button className="bg-[#2c2c2c] hover:bg-[#1e1e1e]">Bid Task</Button>
        </div>
      </div>

      {/* Task Card 3 */}
      <div className="border rounded-lg overflow-hidden">
        <div className="p-4">
          <div className="aspect-video relative mb-4 bg-[#e3e3e3] flex items-center justify-center">
            <p className="text-[#757575] text-center px-4">
              As a protection against automated spam, you'll need to type in the words that appear in this image to
              register an account.
              <br />
              (What is this?)
            </p>
          </div>
          <h3 className="font-semibold mb-2">Text Input Captcha</h3>
          <p className="text-sm text-[#757575]">Type the text shown in the image.</p>
        </div>
        <div className="flex justify-end p-2 bg-[#f5f5f5]">
          <Button className="bg-[#2c2c2c] hover:bg-[#1e1e1e]">Bid Task</Button>
        </div>
      </div>

      {/* Task Card 4 */}
      <div className="border rounded-lg overflow-hidden">
        <div className="p-4">
          <div className="aspect-video relative mb-4 bg-[#e3e3e3] flex items-center justify-center">
            <Image src="/captcha-text.png" alt="Captcha text" fill className="object-cover" />
          </div>
          <h3 className="font-semibold mb-2">Text Input Captcha</h3>
          <p className="text-sm text-[#757575]">Type the two words shown in the image.</p>
        </div>
        <div className="flex justify-end p-2 bg-[#f5f5f5]">
          <Button className="bg-[#2c2c2c] hover:bg-[#1e1e1e]">Bid Task</Button>
        </div>
      </div>

      {/* More task cards can be added here */}
    </div>
  )
}
