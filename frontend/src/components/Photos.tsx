import React from "react";
import Thumbnail from "./Thumbnail";
import { useSearchImagesImagesSearchGet, type ImageResponseDTO } from "../api/generated";
import { Link } from "wouter";

interface PhotosProps {
    images: ImageResponseDTO[];
    onClickImage?: (image: ImageResponseDTO) => void;
    className?: string;
    query?: string;
}

// Masonry grid layout
export const Photos: React.FC<PhotosProps> = ({ images, onClickImage, className = "", query = "" }) => {
    const { data: photos, isLoading } = useSearchImagesImagesSearchGet({
        query: query
    }, {
        swr: { enabled: query.length > 2 }
    })

    const imagesToShow = (photos && photos.length > 0) ? photos : images;

    if (isLoading) {
        return <p>Loading...</p>
    }

    console.log("Photos component - query:", query);

    if (imagesToShow.length === 0 || (query.length > 2 && (!photos || photos.length === 0))) {
        return <p>No images found.</p>
    }

    return (
        <div
            className={`w-full columns-2 sm:columns-3 md:columns-4 lg:columns-5 xl:columns-6 gap-4 ${className}`}
        >
            {imagesToShow.map((img) => (
                <Link
                    to={`/image/${img.id}`}
                    key={img.id}
                    className="cursor-pointer group relative break-inside-avoid mb-4 inline-block w-full"
                    onClick={() => onClickImage?.(img)}
                >
                    <Thumbnail
                        filename={img.small_url || img.url || ""}
                        alt={img.title || ""}
                        size="small"
                        className="w-full h-auto shadow rounded-md group-hover:ring-4 group-hover:ring-sky-800"
                    />
                    {img.title && <div className="absolute bottom-2 left-2 bg-sky-800 text-white text-xs font-bold px-2 py-1 rounded-md opacity-80">
                        {img.title}
                    </div>}
                </Link>
            ))}
        </div>
    );
};

export default Photos;
