import React, { useState } from "react";
import type { AlbumResponseDTO } from "../api/generated";

interface AlbumFormProps {
  initial?: Partial<AlbumResponseDTO>;
  onSubmit: (data: { title: string; description?: string; collection_id: string }) => void;
  collections: { id: string; name: string }[];
  submitLabel?: string;
}

export const AlbumForm: React.FC<AlbumFormProps> = ({ initial = {}, onSubmit, collections, submitLabel = "Save" }) => {
  const [title, setTitle] = useState(initial.title || "");
  const [description, setDescription] = useState(initial.description || "");
  const [collectionId, setCollectionId] = useState(initial.collection_id || (collections[0]?.id ?? ""));

  return (
    <form
      className="flex flex-col gap-4 bg-white p-6 rounded-lg shadow border border-gray-200"
      onSubmit={e => {
        e.preventDefault();
        onSubmit({ title, description, collection_id: collectionId });
      }}
    >
      <label className="font-bold ">Title</label>
      <input
        className="border rounded px-3 py-2 focus:ring-2 focus:ring-sky-800"
        value={title}
        onChange={e => setTitle(e.target.value)}
        required
      />
      <label className="font-bold ">Description</label>
      <input
        className="border rounded px-3 py-2 focus:ring-2 focus:ring-sky-800"
        value={description}
        onChange={e => setDescription(e.target.value)}
      />
      <label className="font-bold ">Collection</label>
      <select
        className="border rounded px-3 py-2 focus:ring-2 focus:ring-sky-800"
        value={collectionId}
        onChange={e => setCollectionId(e.target.value)}
        required
      >
        {collections.map(col => (
          <option key={col.id} value={col.id}>{col.name}</option>
        ))}
      </select>
      <button
        type="submit"
        className="bg-sky-800 text-white font-bold rounded-md px-4 py-2 mt-2 hover:bg-sky-900 cursor-pointer"
      >
        {submitLabel}
      </button>
    </form>
  );
};

export default AlbumForm;
