import type React from "react";
import Header from "./Header";

export default function Layout({ children, query, setQuery }: { children: React.ReactNode, setQuery?: (query: string) => void, query?: string }) {
  return (
    <div className="min-h-screen flex flex-col text-gray-900">
      <Header setQuery={setQuery} query={query} />
      <main className="flex-1 flex flex-col">{children}</main>
    </div>
  );
}
