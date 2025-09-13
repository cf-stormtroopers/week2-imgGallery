
import React, { useRef, useState } from "react";
import { useListAlbumsAlbumsGet, useCreateImageImagesPost } from "../api/generated";
import Layout from "../components/Layout";

export default function AddPhotoToGallery() {
  const albumsResult = useListAlbumsAlbumsGet();
  const albums: any[] = Array.isArray(albumsResult.data) ? albumsResult.data : [];
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [caption, setCaption] = useState("");
  const [altText, setAltText] = useState("");
  const [license, setLicense] = useState("");
  const [attribution, setAttribution] = useState("");
  const [privacy, setPrivacy] = useState("public");
  const [selectedAlbumIds, setSelectedAlbumIds] = useState<Set<string>>(new Set());
  const [message, setMessage] = useState<string | null>(null);
  const { trigger: uploadImage, isMutating } = useCreateImageImagesPost();
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    setSelectedFile(file || null);
    if (file) {
      setPreviewUrl(URL.createObjectURL(file));
    } else {
      setPreviewUrl(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    if (!selectedFile) {
      setMessage("Please select an image file.");
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);
    if (title) formData.append('title', title);
    if (caption) formData.append('caption', caption);
    if (altText) formData.append('alt_text', altText);
    if (license) formData.append('license', license);
    if (attribution) formData.append('attribution', attribution);
    formData.append('privacy', privacy);
    formData.append('timestamp', new Date().toISOString());
    formData.append('albums', JSON.stringify(Array.from(selectedAlbumIds)));

    await uploadImage({
      file: selectedFile,
      title: title || undefined,
      caption: caption || undefined,
      alt_text: altText || undefined,
      timestamp: new Date().toISOString(),
      albums: JSON.stringify(Array.from(selectedAlbumIds)),
      privacy: privacy || "public",
      license: license || undefined,
      attribution: attribution || undefined,
    });
    setMessage("✅ Upload successful!");

    setSelectedFile(null);
    setPreviewUrl(null);
    setTitle("");
    setCaption("");
    setAltText("");
    setLicense("");
    setAttribution("");
    setPrivacy("public");
    setSelectedAlbumIds(new Set());
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const toggleAlbum = (id: string) => {
    setSelectedAlbumIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  return (
    <Layout>
      <main className="flex-1 p-6 overflow-y-auto text-gray-800">
        <h1 className="text-2xl font-semibold mb-6 text-gray-900">Add a Photo</h1>
        <form
          onSubmit={handleUpload}
          className="bg-white p-6 rounded shadow flex flex-col gap-6"
        >
          {/* Upload + sidebar inputs */}
          <div className="flex flex-col lg:flex-row gap-6">
            {/* Upload box */}
            <div className="flex-1 border-dashed border-2 rounded p-6 text-center relative text-gray-700 flex items-center justify-center">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              {previewUrl ? (
                <img src={previewUrl} alt="Preview" className="max-w-xs max-h-64 object-cover rounded" />
              ) : (
                <p className="text-gray-500">
                  Click to upload <br /> or Drag and Drop
                </p>
              )}
            </div>

            {/* Sidebar inputs */}
            <div className="w-full lg:w-1/3 space-y-4">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700">Title</label>
                <input
                  className="mt-1 w-full border rounded p-2 text-gray-800"
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Photo title..."
                />
              </div>

              {/* Caption */}
              <div>
                <label className="block text-sm font-medium text-gray-700">Caption</label>
                <input
                  className="mt-1 w-full border rounded p-2 text-gray-800"
                  type="text"
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                  placeholder="Photo caption..."
                />
              </div>

              {/* Alt Text */}
              <div>
                <label className="block text-sm font-medium text-gray-700">Alt Text</label>
                <input
                  className="mt-1 w-full border rounded p-2 text-gray-800"
                  type="text"
                  value={altText}
                  onChange={(e) => setAltText(e.target.value)}
                  placeholder="Alt text..."
                />
              </div>

              {/* License */}
              <div>
                <label className="block text-sm font-medium text-gray-700">License</label>
                <input
                  className="mt-1 w-full border rounded p-2 text-gray-800"
                  type="text"
                  value={license}
                  onChange={(e) => setLicense(e.target.value)}
                  placeholder="e.g., CC BY 4.0, All Rights Reserved..."
                  maxLength={100}
                />
              </div>

              {/* Attribution */}
              <div>
                <label className="block text-sm font-medium text-gray-700">Attribution</label>
                <input
                  className="mt-1 w-full border rounded p-2 text-gray-800"
                  type="text"
                  value={attribution}
                  onChange={(e) => setAttribution(e.target.value)}
                  placeholder="Photo by..."
                  maxLength={255}
                />
              </div>

              {/* Privacy */}
              <div>
                <label className="block text-sm font-medium text-gray-700">Privacy</label>
                <select
                  className="mt-1 w-full border rounded p-2 text-gray-800"
                  value={privacy}
                  onChange={(e) => setPrivacy(e.target.value)}
                >
                  <option value="public">Public</option>
                  <option value="unlisted">Unlisted</option>
                  <option value="private">Private</option>
                </select>
              </div>
            </div>
          </div>

          {/* Album selection inside form */}
          <div className="mt-6 bg-white p-6 rounded border-2 border-gray-300">
            <h2 className="text-lg font-medium mb-3 text-gray-900">Add to Album</h2>
            {albumsResult.isLoading && <p className="text-gray-500">Loading albums…</p>}
            {Boolean(albumsResult.error) && (
              <p className="text-red-500">Could not load albums.</p>
            )}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {albums.map((a: any) => (
                <label
                  key={String(a?.id ?? a?.title ?? Math.random())}
                  className="flex items-center justify-between border rounded p-3 cursor-pointer text-gray-800"
                >
                  <span>{a.title ?? a.name ?? String(a.id)}</span>
                  <input
                    type="checkbox"
                    checked={selectedAlbumIds.has(String(a.id))}
                    onChange={() => toggleAlbum(String(a.id))}
                  />
                </label>
              ))}
              {albums.length === 0 && (
                <p className="text-sm text-gray-500 col-span-full">No albums yet.</p>
              )}
            </div>
          </div>

          {/* Feedback + Submit */}
          <div className="mt-6 flex flex-col items-center">
            {message && (
              <div className="mb-4 text-sm font-medium text-gray-800">{message}</div>
            )}
            <button
              type="submit"
              disabled={isMutating}
              className="px-6 py-2 bg-sky-800 hover:bg-sky-900 text-white rounded font-bold disabled:opacity-50"
            >
              {isMutating ? "Uploading..." : "Add"}
            </button>
          </div>
        </form>
      </main>
    </Layout>
  );
}
