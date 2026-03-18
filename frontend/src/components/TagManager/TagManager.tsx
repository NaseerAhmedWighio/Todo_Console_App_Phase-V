"use client";

import React, { useState, useEffect } from "react";
import { tagsService, Tag } from "../../services/tags";

interface TagManagerProps {
  onTagSelected?: (tagId: string) => void;
  selectedTagIds?: string[];
}

export const TagManager: React.FC<TagManagerProps> = ({
  onTagSelected,
  selectedTagIds = [],
}) => {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTagName, setNewTagName] = useState("");
  const [newTagColor, setNewTagColor] = useState("#6B7280");

  // Color presets
  const colorPresets = [
    "#6B7280", // Gray
    "#EF4444", // Red
    "#F97316", // Orange
    "#EAB308", // Yellow
    "#22C55E", // Green
    "#3B82F6", // Blue
    "#8B5CF6", // Purple
    "#EC4899", // Pink
  ];

  const loadTags = async () => {
    try {
      setLoading(true);
      const fetchedTags = await tagsService.listTags();
      console.log('Tags fetched:', fetchedTags);
      setTags(fetchedTags);
      setError("");
    } catch (err: any) {
      const errorMsg = err.response?.status === 401 
        ? "Please login to view tags" 
        : err.response?.data?.detail || "Failed to load tags";
      setError(errorMsg);
      console.error("Error loading tags:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTags();
  }, []);

  const handleCreateTag = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTagName.trim()) return;

    try {
      setLoading(true);
      const createdTag = await tagsService.createTag({
        name: newTagName.trim(),
        color: newTagColor,
      });
      console.log('Tag created successfully:', createdTag);
      setNewTagName("");
      setNewTagColor("#6B7280");
      setShowCreateForm(false);
      await loadTags();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || "Failed to create tag";
      setError(errorMsg);
      console.error("Error creating tag:", err);
      console.error("Error response:", err.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTag = async (tagId: string) => {
    if (!confirm("Delete this tag? It will be removed from all tasks.")) return;

    try {
      setLoading(true);
      await tagsService.deleteTag(tagId);
      await loadTags();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete tag");
      console.error("Error deleting tag:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleTagClick = (tagId: string) => {
    if (onTagSelected) {
      onTagSelected(tagId);
    }
  };

  const isSelected = (tagId: string) => selectedTagIds.includes(tagId);

  return (
    <div className="tag-manager bg-white dark:bg-[#1e293b] rounded-lg shadow p-4 border-glow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
          Tags
        </h3>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium transition-colors duration-300"
        >
          {showCreateForm ? "Cancel" : "+ New Tag"}
        </button>
      </div>

      {error && (
        <div className="text-red-500 dark:text-red-400 mb-4 text-sm">{error}</div>
      )}

      {showCreateForm && (
        <form onSubmit={handleCreateTag} className="mb-4 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Tag Name
            </label>
            <input
              type="text"
              value={newTagName}
              onChange={(e) => setNewTagName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
              placeholder="Enter tag name"
              maxLength={50}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Color
            </label>
            <div className="flex gap-2 flex-wrap">
              {colorPresets.map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setNewTagColor(color)}
                  className={`w-8 h-8 rounded-full border-2 transition-all duration-200 ${
                    newTagColor === color
                      ? "border-gray-900 dark:border-white scale-110"
                      : "border-transparent hover:scale-105"
                  }`}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>
          <button
            type="submit"
            disabled={loading || !newTagName.trim()}
            className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors duration-300 disabled:opacity-50"
          >
            {loading ? "Creating..." : "Create Tag"}
          </button>
        </form>
      )}

      {loading && !showCreateForm && (
        <div className="text-center py-4 text-gray-500 dark:text-gray-400">
          Loading tags...
        </div>
      )}

      {!loading && tags.length === 0 && (
        <div className="text-center py-4 text-gray-500 dark:text-gray-400">
          No tags yet. Create your first tag!
        </div>
      )}

      <div className="space-y-2">
        {tags.map((tag) => (
          <div
            key={tag.id}
            className={`flex items-center justify-between p-2 rounded-md transition-all duration-200 cursor-pointer ${
              isSelected(tag.id)
                ? "bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700"
                : "hover:bg-gray-50 dark:hover:bg-gray-800"
            }`}
            onClick={() => handleTagClick(tag.id)}
          >
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: tag.color }}
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {tag.name}
              </span>
              {tag.usage_count !== undefined && (
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  ({tag.usage_count})
                </span>
              )}
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteTag(tag.id);
              }}
              className="text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors duration-300"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TagManager;
