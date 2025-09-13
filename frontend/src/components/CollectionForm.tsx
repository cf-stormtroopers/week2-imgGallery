import React, { useState } from "react";
import type { CollectionDTO } from "../api/generated";

interface CollectionFormProps {
  initial?: Partial<CollectionDTO>;
  onSubmit: (data: { name: string }) => void;
  submitLabel?: string;
  onDelete?: () => void;
}

export const CollectionForm: React.FC<CollectionFormProps> = ({ initial = {}, onSubmit, submitLabel = "Save", onDelete }) => {
  const [name, setName] = useState(initial.name || "");

  return (
    <form
      className="flex flex-col gap-4 bg-white p-6 rounded-lg shadow border border-gray-200"
      onSubmit={e => {
        e.preventDefault();
        onSubmit({ name });
      }}
    >
      <label className="font-bold ">Collection Name</label>
      <input
        className="border rounded px-3 py-2 focus:ring-2 focus:ring-sky-800"
        value={name}
        onChange={e => setName(e.target.value)}
        required
      />
      <div className="flex gap-2 items-center">
        <button
          type="submit"
          className="bg-sky-800 text-white font-bold rounded-md px-4 py-2 hover:bg-sky-900 cursor-pointer"
        >
          {submitLabel}
        </button>
        {onDelete && (
          <button
            type="button"
            className="ml-2 p-2 rounded-full bg-red-100 hover:bg-red-400 text-red-700 hover:text-white font-bold cursor-pointer"
            onClick={onDelete}
            title="Delete Collection"
          >
            <span role="img" aria-label="delete">🗑️</span>
          </button>
        )}
      </div>
    </form>
  );
};

export default CollectionForm;
