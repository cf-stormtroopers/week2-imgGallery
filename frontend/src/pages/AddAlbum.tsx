import { useState } from "react";
import Layout from "../components/Layout";

export default function AddAlbum() {
  const [albumName, setAlbumName] = useState("");
  const [collection, setCollection] = useState("");
  const [albums, setAlbums] = useState<{ name: string; collection: string }[]>([]);

  const collections = ["Collection One", "Collection Two"]; // placeholder

  const handleAddAlbum = () => {
    if (!albumName || !collection) return;
    setAlbums([...albums, { name: albumName, collection }]);
    setAlbumName("");
    setCollection("");
  };

  return (
    <Layout>
      <div
        className="flex flex-1 p-6 gap-6 overflow-hidden min-h-screen 
                   bg-gradient-to-br from-background via-accent/20 to-primary/20 
                   text-gray-900"
      >
        {/* Left: Albums */}
        <div className="flex-1 overflow-y-auto">
          <h1
            className="text-6xl font-extrabold mb-10 text-gradientStart drop-shadow-[0_4px_6px_rgba(0,0,0,0.25)]"
          >
            Albums
          </h1>

          {collections.map((col) => (
            <div key={col} className="mb-12">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gradientStart">
                  {col}
                </h2>
                <div className="flex gap-3 text-gray-900">
                  <button
                    title="Edit"
                    className="p-2 rounded-full bg-white/70 hover:bg-primary hover:text-white 
                               shadow-sm hover:scale-105 transition transform"
                  >
                    ✏️
                  </button>
                  <button
                    title="Delete"
                    className="p-2 rounded-full bg-white/70 hover:bg-accent hover:text-white 
                               shadow-sm hover:scale-105 transition transform"
                  >
                    ❌
                  </button>
                </div>
              </div>

              <div className="flex flex-wrap gap-6">
                {albums
                  .filter((a) => a.collection === col)
                  .map((a, idx) => (
                    <div
                      key={idx}
                      className="w-40 h-40 flex items-center justify-center 
                                 text-white font-semibold shadow-md rounded-2xl border border-border 
                                 bg-gradient-to-br from-gradientStart via-gradientMiddle to-gradientEnd 
                                 hover:scale-105 hover:shadow-lg transition-all duration-300"
                    >
                      {a.name}
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>

        {/* Right: Add Album Form */}
        <div
          className="w-80 
                     bg-white/70 backdrop-blur-xl shadow-lg rounded-2xl p-8 flex flex-col gap-6 
                     border border-border transition-all duration-300"
        >
          <h2 className="text-2xl font-bold text-gradientStart">
            Create New Album
          </h2>

          <input
            type="text"
            placeholder="Album name"
            value={albumName}
            onChange={(e) => setAlbumName(e.target.value)}
            className="px-4 py-3 border border-border rounded-xl w-full 
                       text-gray-900 focus:ring-2 focus:ring-accent focus:outline-none 
                       shadow-sm"
          />

          <div className="relative">
            <select
              value={collection}
              onChange={(e) => setCollection(e.target.value)}
              className="appearance-none px-4 py-3 w-full rounded-xl text-gray-900 
                         bg-white border border-border shadow-sm
                         focus:ring-2 focus:ring-accent focus:border-accent
                         transition duration-300 cursor-pointer"
            >
              <option value="">Select collection</option>
              {collections.map((col) => (
                <option key={col} value={col} className="text-gray-900">
                  {col}
                </option>
              ))}
            </select>
            <span className="pointer-events-none absolute right-3 top-1/2 transform -translate-y-1/2 text-accent">
              ▼
            </span>
          </div>

          <button
            onClick={handleAddAlbum}
            className="px-5 py-3 rounded-xl font-bold 
                       bg-white border border-border shadow-md
                       hover:scale-105 hover:shadow-lg transition-all duration-300"
          >
            ✨ Create Album ✨
          </button>
        </div>
      </div>
    </Layout>
  );
/* The button is already present in your code:
  <button
    onClick={handleAddAlbum}
    className="px-5 py-3 rounded-xl font-bold 
           bg-white border border-border shadow-md
           hover:scale-105 hover:shadow-lg transition-all duration-300"
  >
    ✨ Create Album ✨
  </button>
*/
}