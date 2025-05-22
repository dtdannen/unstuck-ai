import Link from "next/link"
import Image from "next/image"
import { Twitter, Instagram, Youtube, Linkedin } from "lucide-react"

export default function Footer() {
  return (
    <footer className="bg-white py-12 border-t">
      <div className="container">
        <div className="flex flex-col space-y-10">
          <div className="flex items-center">
            <Image src="/unstuckgoose.png" alt="Unstuck Logo" width={150} height={50} />
          </div>

          <div className="flex flex-wrap gap-x-12 gap-y-8">
            <div className="flex flex-col space-y-4 min-w-[160px]">
              <h3 className="font-semibold text-[#2c2c2c]">Use cases</h3>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                UI design
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                UX design
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Wireframing
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Diagramming
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Brainstorming
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Online whiteboard
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Team collaboration
              </Link>
            </div>

            <div className="flex flex-col space-y-4 min-w-[160px]">
              <h3 className="font-semibold text-[#2c2c2c]">Explore</h3>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Design
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Prototyping
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Development features
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Design systems
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Collaboration features
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Design process
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Fig-Jam
              </Link>
            </div>

            <div className="flex flex-col space-y-4 min-w-[160px]">
              <h3 className="font-semibold text-[#2c2c2c]">Resources</h3>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Blog
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Best practices
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Colors
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Color wheel
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Support
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Developers
              </Link>
              <Link href="#" className="text-[#757575] hover:text-[#f5a623]">
                Resource library
              </Link>
            </div>
          </div>

          <div className="flex gap-4">
            <Link href="#" aria-label="Twitter">
              <Twitter className="w-5 h-5 text-[#757575] hover:text-[#f5a623]" />
            </Link>
            <Link href="#" aria-label="Instagram">
              <Instagram className="w-5 h-5 text-[#757575] hover:text-[#f5a623]" />
            </Link>
            <Link href="#" aria-label="YouTube">
              <Youtube className="w-5 h-5 text-[#757575] hover:text-[#f5a623]" />
            </Link>
            <Link href="#" aria-label="LinkedIn">
              <Linkedin className="w-5 h-5 text-[#757575] hover:text-[#f5a623]" />
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
