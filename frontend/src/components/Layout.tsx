import type React from "react";
import Header from "./Header";

export default function Layout({ children, query, setQuery }: { children: React.ReactNode, setQuery?: (query: string) => void, query?: string }) {
  return (
    <div className="h-screen flex flex-col text-gray-900 overflow-y-none">
      <Header setQuery={setQuery} query={query} />
      <main className="flex-1 flex flex-col overflow-y-auto">{children}</main>
    </div>
  );
}
