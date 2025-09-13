import { useParams, useLocation } from "wouter";
import Layout from "../components/Layout";
import { useGetImageImagesImageIdGet, useDeleteImageImagesImageIdDelete, useToggleLikeImagesImageIdLikePost } from "../api/generated";
import { getImageUrlFromDbUrl } from "../api/axios";
import Comments from "../components/Comments";
import { useState, useEffect } from "react";
import { useAuthStore } from "../state/auth";

export default function LightboxPage() {
    const auth = useAuthStore();
    const { id } = useParams<{ id: string }>();
    const [, setLocation] = useLocation();
    const [likeCount, setLikeCount] = useState(0);
    const [isLiked, setIsLiked] = useState(false);

    const { data: image, error, isLoading } = useGetImageImagesImageIdGet(id!);
    const { trigger: deleteImage, isMutating: isDeleting } = useDeleteImageImagesImageIdDelete(id!);
    const { trigger: toggleLike, isMutating: isToggling } = useToggleLikeImagesImageIdLikePost(id!);

    // Initialize like state from image data
    useEffect(() => {
        if (image) {
            setLikeCount(image.like_count || 0);
            setIsLiked(image.user_liked || false);
        }
    }, [image]);

    const handleLike = async () => {
        if (isToggling) return;
        
        try {
            const result = await toggleLike();
            setIsLiked(result.liked);
            setLikeCount(result.like_count);
        } catch (error) {
            console.error("Failed to toggle like:", error);
        }
    };

    const handleDelete = async () => {
        if (!image?.id) return;

        const confirmDelete = window.confirm("Are you sure you want to delete this image? This action cannot be undone.");
        if (!confirmDelete) return;

        try {
            await deleteImage();
            alert("✅ Image deleted successfully!");
            setLocation("/"); // Redirect to home page after deletion
        } catch (error) {
            alert("❌ Failed to delete image. Please try again.");
            console.error("Delete error:", error);
        }
    };

    if (isLoading) {
        return (
            <Layout>
                <div className="flex-1 flex items-center justify-center">
                    <p className="text-gray-600">Loading image...</p>
                </div>
            </Layout>
        );
    }

    if (error || !image) {
        return (
            <Layout>
                <div className="flex-1 flex items-center justify-center">
                    <p className="text-red-600">Error loading image. Please try again.</p>
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="flex-1 flex flex-col">
                {/* Header with title and actions */}
                <div className="bg-white border-b p-4">
                    <div className="max-w-7xl mx-auto flex justify-between items-center">
                        <div className="flex-1">
                            <button
                                onClick={() =>  {
                                    history.back()
                                }}
                                className="font-bold"
                            >
                                &larr; Back
                            </button>
                            {image.title && (
                                <h1 className="text-2xl font-bold text-gray-900">{image.title}</h1>
                            )}
                            {image.caption && (
                                <p className="text-gray-600 mt-1">{image.caption}</p>
                            )}
                        </div>
                        <div className="flex gap-3 ml-4">
                            <button
                                onClick={handleLike}
                                disabled={isToggling || !auth.accountInformation}
                                className={`flex items-center gap-2 px-4 py-2 rounded transition-colors ${
                                    isLiked 
                                        ? "bg-red-100 text-red-800 hover:bg-red-200" 
                                        : "bg-gray-100 text-gray-800 hover:bg-gray-200"
                                }`}
                            >
                                <span className="text-lg">{isLiked ? "❤️" : "🤍"}</span>
                                <span>{isToggling ? "..." : likeCount}</span>
                            </button>
                            {(auth.accountInformation?.role === "editor" || auth.accountInformation?.role === "admin") && <button
                                onClick={handleDelete}
                                disabled={isDeleting}
                                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 transition-colors"
                            >
                                {isDeleting ? "Deleting..." : "Delete"}
                            </button>}
                        </div>
                    </div>
                </div>

                {/* Main image display */}
                <div className="flex-1 flex items-center justify-center p-4 bg-black">
                    <div className="relative max-w-full max-h-[80vh] flex items-center justify-center">
                        <img
                            src={getImageUrlFromDbUrl(image.url)}
                            alt={image.alt_text || image.title || "Image"}
                            className="max-w-full max-h-[80vh] object-contain rounded shadow-2xl"
                            style={{
                                maxWidth: "95vw",
                                maxHeight: "80vh"
                            }}
                        />
                    </div>
                </div>

                {/* Image metadata and info */}
                <div className="bg-white border-t p-4">
                    <div className="max-w-7xl mx-auto">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                            {/* Basic info */}
                            <div className="space-y-2">
                                <h3 className="font-semibold text-gray-900">Image Info</h3>
                                {image.timestamp && (
                                    <p className="text-gray-600">
                                        <span className="font-medium">Created:</span> {new Date(image.timestamp).toLocaleDateString()}
                                    </p>
                                )}
                                {image.mime_type && (
                                    <p className="text-gray-600">
                                        <span className="font-medium">Type:</span> {image.mime_type}
                                    </p>
                                )}
                                <p className="text-gray-600">
                                    <span className="font-medium">Views:</span> {image.view_count || 0}
                                </p>
                                <p className="text-gray-600">
                                    <span className="font-medium">Downloads:</span> {image.download_count || 0}
                                </p>
                                <p className="text-gray-600">
                                    <span className="font-medium">Likes:</span> {likeCount}
                                </p>
                            </div>

                            {/* License and Attribution */}
                            <div className="space-y-2">
                                <h3 className="font-semibold text-gray-900">License & Attribution</h3>
                                {image.license ? (
                                    <p className="text-gray-600">
                                        <span className="font-medium">License:</span> {image.license}
                                    </p>
                                ) : (
                                    <p className="text-gray-500 italic">No license specified</p>
                                )}
                                {image.attribution ? (
                                    <p className="text-gray-600">
                                        <span className="font-medium">Attribution:</span> {image.attribution}
                                    </p>
                                ) : (
                                    <p className="text-gray-500 italic">No attribution required</p>
                                )}
                            </div>

                            {/* Technical details */}
                            <div className="space-y-2">
                                <h3 className="font-semibold text-gray-900">Available Sizes</h3>
                                {image.small_url && (
                                    <a
                                        href={getImageUrlFromDbUrl(image.small_url)}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="block text-blue-600 hover:text-blue-800 underline"
                                    >
                                        Small version
                                    </a>
                                )}
                                {image.medium_url && (
                                    <a
                                        href={getImageUrlFromDbUrl(image.medium_url)}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="block text-blue-600 hover:text-blue-800 underline"
                                    >
                                        Medium version
                                    </a>
                                )}
                                {image.large_url && (
                                    <a
                                        href={getImageUrlFromDbUrl(image.large_url)}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="block text-blue-600 hover:text-blue-800 underline"
                                    >
                                        Large version
                                    </a>
                                )}
                                {image.url && (
                                    <a
                                        href={getImageUrlFromDbUrl(image.url)}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="block text-blue-600 hover:text-blue-800 underline"
                                    >
                                        Original version
                                    </a>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Comments section */}
                <div className="bg-white border-t p-4">
                    <div className="max-w-7xl mx-auto">
                        <Comments imageId={id!} />
                    </div>
                </div>
            </div>
        </Layout>
    );
}
