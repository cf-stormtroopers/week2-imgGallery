import React, { useState } from "react";
import { 
  useGetImageCommentsImagesImageIdCommentsGet,
  useAddCommentImagesImageIdCommentsPost,
  deleteCommentImagesImageIdCommentsCommentIdDelete
} from "../api/generated";

interface CommentsProps {
  imageId: string;
}

export default function Comments({ imageId }: CommentsProps) {
  const [commentText, setCommentText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: comments = [], error, isLoading, mutate } = useGetImageCommentsImagesImageIdCommentsGet(imageId);
  const { trigger: addComment } = useAddCommentImagesImageIdCommentsPost(imageId);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentText.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await addComment({ content: commentText.trim() });
      setCommentText("");
      mutate(); // Refresh comments
    } catch (error) {
      console.error("Failed to add comment:", error);
      alert("❌ Failed to add comment. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (commentId: string) => {
    const confirmDelete = window.confirm("Are you sure you want to delete this comment?");
    if (!confirmDelete) return;

    try {
      await deleteCommentImagesImageIdCommentsCommentIdDelete(imageId, commentId);
      mutate(); // Refresh comments
    } catch (error) {
      console.error("Failed to delete comment:", error);
      alert("❌ Failed to delete comment. Please try again.");
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Comments</h3>
        <p className="text-gray-600">Loading comments...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Comments</h3>
        <p className="text-red-600">Error loading comments.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Comments ({comments.length})</h3>
      
      {/* Add comment form */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <textarea
          value={commentText}
          onChange={(e) => setCommentText(e.target.value)}
          placeholder="Add a comment..."
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          maxLength={500}
        />
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-500">
            {commentText.length}/500 characters
          </span>
          <button
            type="submit"
            disabled={!commentText.trim() || isSubmitting}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSubmitting ? "Posting..." : "Post Comment"}
          </button>
        </div>
      </form>

      {/* Comments list */}
      <div className="space-y-4">
        {comments.length === 0 ? (
          <p className="text-gray-500 italic">No comments yet. Be the first to comment!</p>
        ) : (
          comments.map((comment) => (
            <div key={comment.id} className="border-b border-gray-200 pb-3">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-gray-900">
                      {comment.username || "Anonymous"}
                    </span>
                    <span className="text-sm text-gray-500">
                      {new Date(comment.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-gray-700">{comment.content}</p>
                </div>
                <button
                  onClick={() => handleDelete(comment.id)}
                  className="ml-2 text-red-600 hover:text-red-800 text-sm px-2 py-1 rounded hover:bg-red-50 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}