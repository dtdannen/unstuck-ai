export default function AboutUs() {
  return (
    <div className="container py-12">
      <h1 className="text-3xl font-bold text-[#1e1e1e] mb-6">About Us</h1>

      <div className="prose max-w-none">
        <p>
          Unstuck is a platform that connects people who need help with small tasks to those who are willing to complete
          them in exchange for Bitcoin satoshis (sats).
        </p>

        <h2>Our Mission</h2>
        <p>
          Our mission is to create a decentralized marketplace for microtasks that leverages the Nostr protocol and
          Bitcoin's Lightning Network to enable seamless, borderless collaboration.
        </p>

        <h2>How It Works</h2>
        <p>
          Users can post tasks that need to be completed, such as captcha solving, data verification, content
          moderation, and more. Other users can bid on these tasks and earn sats for completing them successfully.
        </p>

        <h2>Why Nostr?</h2>
        <p>
          Nostr (Notes and Other Stuff Transmitted by Relays) is a simple, open protocol that enables
          censorship-resistant and decentralized social media. By building on Nostr, we ensure that our platform remains
          resilient, user-controlled, and free from central points of failure.
        </p>

        <h2>Join Us</h2>
        <p>
          Whether you're looking to earn some extra sats or need help with tasks that require human intelligence,
          Unstuck provides a platform where everyone can contribute and benefit. Join us today and be part of building
          the future of work!
        </p>
      </div>
    </div>
  )
}
