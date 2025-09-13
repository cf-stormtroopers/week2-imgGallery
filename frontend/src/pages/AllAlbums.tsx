

import { useState } from "react";
import Albums from "../components/Albums";
import AlbumForm from "../components/AlbumForm";
import CollectionForm from "../components/CollectionForm";
import { createAlbumAlbumsPost, createCollectionCollectionsPost, useListAlbumsAlbumsGet, useListCollectionsCollectionsGet } from "../api/generated";
import Layout from "../components/Layout";
import { mutate } from "swr";
import { useAuthStore } from "../state/auth";

export default function AllAlbums() {
  const auth = useAuthStore();

  // Fetch albums and collections
  const albumsData = useListAlbumsAlbumsGet();
  const collectionsData = useListCollectionsCollectionsGet();
  const albums = Array.isArray(albumsData.data) ? albumsData.data : [];
  const collections = Array.isArray(collectionsData.data) ? collectionsData.data : [];

  // State for showing forms
  const [showAlbumForm, setShowAlbumForm] = useState(false);
  const [showCollectionForm, setShowCollectionForm] = useState(false);

  return (
    <Layout>
      {/* Page Body */}
      <div className="flex flex-1">
        {/* Sidebar: Collections */}
        <aside className="w-1/4 p-6 border-r border-gray-200">
          <h2 className="text-lg font-bold mb-4 ">Collections</h2>
          <div className="mb-4">
            {auth.accountInformation?.role === "editor" && <button
              className="bg-sky-800 hover:bg-sky-900 text-white px-4 py-2 rounded font-bold mb-2"
              onClick={() => setShowCollectionForm(true)}
            >
              + New Collection
            </button>}
            <ul className="mt-2 space-y-2">
              {collections.map((c: any) => (
                <li key={c.id} className="text-gray-800 font-medium">
                  {c.name}
                </li>
              ))}
            </ul>
          </div>
          {showCollectionForm && (
            <CollectionForm onSubmit={async ({ name }: { name: string }) => {
              await createCollectionCollectionsPost({
                name,
              })
              collectionsData.mutate()
              setShowCollectionForm(false)
              mutate("/collections/")
            }} />
          )}
        </aside>

        {/* Main Content: Albums */}
        <main className="flex-1 p-6">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold ">All Albums</h1>
            {auth.accountInformation?.role === "editor" && <button
              className="bg-sky-800 hover:bg-sky-900 text-white px-4 py-2 rounded font-bold"
              onClick={() => setShowAlbumForm(true)}
            >
              + New Album
            </button>}
          </div>
          <Albums albums={albums} />
          {showAlbumForm && (
            <AlbumForm
              onSubmit={(data) => {
                createAlbumAlbumsPost({
                  id: "",
                  title: data.title,
                  description: data.description,
                  collection_id: data.collection_id,
                }).then(() => {
                  albumsData.mutate();
                })
                mutate("/albums/")
                setShowAlbumForm(false)
              }}
              collections={collections
                .filter((c: any) => typeof c.id === "string" && typeof c.name === "string")
                .map((c: any) => ({ id: String(c.id), name: c.name }))}
            />
          )}
        </main>
      </div>
    </Layout>
  );
}
