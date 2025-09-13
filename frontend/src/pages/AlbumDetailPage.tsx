import { useGetAlbumAlbumsAlbumIdGet } from "../api/generated";
import { Link, useRoute } from "wouter";
import AlbumForm from "../components/AlbumForm";
import { useListCollectionsCollectionsGet } from "../api/generated";
import { useUpdateAlbumAlbumsAlbumIdPut } from "../api/generated";
import { useState } from "react";
import Photos from "../components/Photos";
import Layout from "../components/Layout";
import { useAuthStore } from "../state/auth";

export default function AlbumDetailPage() {
  const auth = useAuthStore();
  const [, params] = useRoute("/albums/:id");
  const albumId = params?.id || "";
  const [shouldEditAlbum, setShouldEditAlbum] = useState(false);
  const { data: album, mutate: refetchAlbum, isLoading, error } = useGetAlbumAlbumsAlbumIdGet(albumId);
  const { trigger: updateAlbum } = useUpdateAlbumAlbumsAlbumIdPut(albumId);
  const [editMsg, setEditMsg] = useState<string | null>(null);
  const { data: collectionsData } = useListCollectionsCollectionsGet();
  const collections = Array.isArray(collectionsData) ? collectionsData : [];
  const images = album?.images || [];

  console.log({
    album,
    isLoading,
    error,
    albumId, shouldEditAlbum
  })

  if (isLoading) {
    return <p>Loading...</p>
  }

  if (error) {
    return <p>{JSON.stringify(error)}</p>
  }

  return (
    <Layout>
      {/* Page Body */}
      <div className="flex flex-1">
        {/* Sidebar */}
        {shouldEditAlbum && <aside className="w-1/4 p-6 border-r border-gray-200">
          <h2 className="text-lg font-bold mb-4 ">Album Details</h2>
          <div className="mb-4">
            {/* <div className="font-bold text-xl mb-2">{album?.title}</div>
            <div className="text-gray-600 mb-2">{album?.description}</div> */}
            <AlbumForm
              initial={album}
              collections={collections
                .filter((c: any) => typeof c.id === "string" && typeof c.name === "string")
                .map((c: any) => ({ id: String(c.id), name: c.name }))}
              onSubmit={async (values) => {
                setEditMsg(null);
                try {
                  await updateAlbum({ ...values, id: album?.id });
                  setEditMsg("Album updated!");
                  refetchAlbum();
                  setShouldEditAlbum(false);
                } catch (e) {
                  setEditMsg("Failed to update album.");
                }
              }}
            />
            {editMsg && <div className="mt-2 text-sm ">{editMsg}</div>}
          </div>
        </aside>}

        {/* Main Content */}
        <main className="flex-1 p-6 flex flex-col gap-6">
          <div className="flex justify-between items-center gap-5">
            <div className="flex flex-col">
              <h1 className="text-2xl font-bold">{album?.title ?? ""}</h1>
              <div className="font-bold">Part of {album?.collection_name}</div>
              <div className="">{album?.description}</div>
            </div>
            {(auth.accountInformation?.role === "editor" || auth.accountInformation?.role === "admin") && <button className="underline text-sky-800" onClick={() => setShouldEditAlbum(e => !e)}>Edit</button>}
          </div>
          <Photos images={images} />
        </main>
      </div>
    </Layout>
  );
}
