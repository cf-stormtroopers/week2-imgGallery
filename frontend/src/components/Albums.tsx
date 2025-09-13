import React from "react";
import type { AlbumResponseDTO } from "../api/generated";
import { Link } from "wouter";

interface AlbumsProps {
    albums: AlbumResponseDTO[];
    onClickAlbum?: (album: AlbumResponseDTO) => void;
    className?: string;
}

export const Albums: React.FC<AlbumsProps> = ({ albums, onClickAlbum, className = "" }) => {
    const albumsByCollection = albums.reduce((acc, album) => {
        const collection = album.collection_name || "Uncategorized";
        if (!acc[collection]) {
            acc[collection] = [];
        }
        acc[collection].push(album);
        return acc;
    }, {} as Record<string, AlbumResponseDTO[]>);

    return (
        <div className={`flex flex-col gap-8 ${className}`}>
            {Object.entries(albumsByCollection).map(([collection, albums]) => (
                <div key={collection} className="w-full">
                    <h2 className="text-lg font-light mb-4 text-gray-900">{collection}</h2>
                    <div className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
                        {albums.map((album) => (
                            <Link
                                key={album.id}
                                className="bg-white rounded-lg shadow p-6 flex flex-col gap-2 border border-gray-200 cursor-pointer hover:ring-4 hover:ring-sky-800 transition-all duration-200 hover:shadow-lg min-h-[200px]"
                                onClick={() => onClickAlbum?.(album)}
                                to={`/albums/${album.id}`}
                            >
                                <div className="text-2xl font-bold mb-2">{album.title}</div>
                                <div className="text-gray-600 text-sm flex-grow">{album.description}</div>
                            </Link>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default Albums;