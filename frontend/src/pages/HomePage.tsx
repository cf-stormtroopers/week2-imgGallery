

import { Link } from "wouter";
import Albums from "../components/Albums";
import Photos from "../components/Photos";
import { useGetHomeImagesImagesHomeGet } from "../api/generated";
import Layout from "../components/Layout";
import { useState } from "react";

export default function HomePage() {
  const { data } = useGetHomeImagesImagesHomeGet();

  const [query, setQuery] = useState<string>("");
  const albums = data?.albums || [];
  const images = data?.images || [];

  return (
    <Layout query={query} setQuery={setQuery}>
      <div className="flex flex-1 h-full flex-row items-stretch">
        <aside className="h-full w-1/4 p-6 border-r border-gray-200 flex flex-col justify-between">
          <div className="flex flex-1 overflow-y-auto p-2">
            <Albums albums={albums} />
          </div>
          <Link to="/albums"><h2 className="text-2xl font-bold mb-4 underline">Albums &rarr;</h2></Link>
        </aside>

        <main className="flex-1 p-6">
          <Photos query={query} images={images} />
        </main>
      </div>
    </Layout>
  );
}
