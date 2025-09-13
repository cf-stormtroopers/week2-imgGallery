import { Link } from "wouter";
import { useAuthStore } from "../state/auth";
import { useState, useEffect } from "react";

export default function Header({
  setQuery,
  query
}: {
  setQuery?: (query: string) => void
  query?: string
}) {
  const auth = useAuthStore()
  const [localQuery, setLocalQuery] = useState(query || "")

  // Debounce the search query
  useEffect(() => {
    const timer = setTimeout(() => {
      if (setQuery) {
        setQuery(localQuery)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [localQuery, setQuery])

  // Update local query when external query changes
  useEffect(() => {
    setLocalQuery(query || "")
  }, [query])

  return (
    <header className="flex items-center justify-between bg-sky-800 text-white shadow px-6 py-8">
      <div className="flex items-center gap-4">
        {/* Profile */}

        {/* Home Link */}
        <Link href="/">
          <a className="text-2xl font-bold hover:underline">
            {auth.settings.site_title || "Home"}
          </a>
        </Link>
      </div>

      {/* Search */}
      {setQuery && <div className="flex-1 max-w-xl mx-6">
        <input
          type="text"
          placeholder="Search with AI ✨"
          className="w-full px-4 py-2 rounded-full border border-gray-200 bg-white text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-sky-400"
          onChange={(e) => setLocalQuery(e.target.value)}
          value={localQuery}
        />
      </div>}

      <div className="flex flex-row gap-4">
        {/* Add Button */}
        {(auth.accountInformation?.role === "editor" || auth.accountInformation?.role === "admin") && <Link href="/add" className="w-10 h-10 rounded-full bg-white hover:bg-sky-200 text-gray-800 text-xl flex items-center justify-center cursor-pointer">
          {/* svg from /icons8-plus.svg */}
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path d="M12 4v16m8-8H4" />
          </svg>
        </Link>}


        <Link href="/profile" className="w-10 h-10 rounded-full bg-white hover:bg-sky-200 text-gray-800 text-xl flex items-center justify-center cursor-pointer">
          <span className="text-lg">👤</span>
        </Link>
      </div>
    </header>
  );
}