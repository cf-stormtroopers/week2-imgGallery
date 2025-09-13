import React, { useState } from "react";
import { 
  useListUsersUsersGet,
  useAddUserUsersPost,
  useUpdateUserUsersUserIdPut,
  deleteUserUsersUserIdDelete
} from "../api/generated";

export default function UserManager() {
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingUser, setEditingUser] = useState<any>(null);
  const [newUser, setNewUser] = useState({
    username: "",
    password: "",
    display_name: "",
    role: "public"
  });

  const { data: users = [], error, isLoading, mutate } = useListUsersUsersGet();
  const { trigger: addUser, isMutating: isAdding } = useAddUserUsersPost();
  const { trigger: updateUser } = useUpdateUserUsersUserIdPut(editingUser?.id || "");

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUser.username || !newUser.password) return;

    try {
      await addUser({
        username: newUser.username,
        password: newUser.password,
        display_name: newUser.display_name || null,
        role: newUser.role
      });
      setNewUser({ username: "", password: "", display_name: "", role: "public" });
      setShowAddForm(false);
      mutate();
      alert("✅ User added successfully!");
    } catch (error) {
      alert("❌ Failed to add user");
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;

    try {
      await updateUser({
        password: editingUser.password || null,
        display_name: editingUser.display_name || null,
        role: editingUser.role
      });
      setEditingUser(null);
      mutate();
      alert("✅ User updated successfully!");
    } catch (error) {
      alert("❌ Failed to update user");
    }
  };

  const handleDeleteUser = async (userId: string, username: string) => {
    const confirmDelete = window.confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`);
    if (!confirmDelete) return;

    try {
      await deleteUserUsersUserIdDelete(userId);
      mutate();
      alert("✅ User deleted successfully!");
    } catch (error) {
      alert("❌ Failed to delete user");
    }
  };

  const startEdit = (user: any) => {
    setEditingUser({
      id: user.id,
      username: user.username,
      display_name: user.display_name || "",
      role: user.role,
      password: ""
    });
  };

  if (isLoading) return <p className="text-gray-600">Loading users...</p>;
  if (error) return <p className="text-red-600">Error loading users</p>;

  return (
    <div className="space-y-6">
      {/* Add User Button */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">User Management</h3>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2 bg-sky-800 text-white rounded hover:bg-sky-900 transition-colors"
        >
          {showAddForm ? "Cancel" : "Add User"}
        </button>
      </div>

      {/* Add User Form */}
      {showAddForm && (
        <form onSubmit={handleAddUser} className="bg-gray-50 p-4 rounded border space-y-4">
          <h4 className="font-medium">Add New User</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Username"
              value={newUser.username}
              onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
              className="border rounded px-3 py-2"
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={newUser.password}
              onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
              className="border rounded px-3 py-2"
              required
            />
            <input
              type="text"
              placeholder="Display Name"
              value={newUser.display_name}
              onChange={(e) => setNewUser({ ...newUser, display_name: e.target.value })}
              className="border rounded px-3 py-2"
            />
            <select
              value={newUser.role}
              onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
              className="border rounded px-3 py-2"
            >
              <option value="public">Public</option>
              <option value="editor">Editor</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <button
            type="submit"
            disabled={isAdding}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            {isAdding ? "Adding..." : "Add User"}
          </button>
        </form>
      )}

      {/* Edit User Form */}
      {editingUser && (
        <form onSubmit={handleUpdateUser} className="bg-blue-50 p-4 rounded border space-y-4">
          <h4 className="font-medium">Edit User: {editingUser.username}</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="password"
              placeholder="New Password (leave blank to keep current)"
              value={editingUser.password}
              onChange={(e) => setEditingUser({ ...editingUser, password: e.target.value })}
              className="border rounded px-3 py-2"
            />
            <input
              type="text"
              placeholder="Display Name"
              value={editingUser.display_name}
              onChange={(e) => setEditingUser({ ...editingUser, display_name: e.target.value })}
              className="border rounded px-3 py-2"
            />
            <select
              value={editingUser.role}
              onChange={(e) => setEditingUser({ ...editingUser, role: e.target.value })}
              className="border rounded px-3 py-2"
            >
              <option value="public">Public</option>
              <option value="editor">Editor</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Update User
            </button>
            <button
              type="button"
              onClick={() => setEditingUser(null)}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Users Table */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              <th className="border border-gray-300 px-4 py-2 text-left">Username</th>
              <th className="border border-gray-300 px-4 py-2 text-left">Display Name</th>
              <th className="border border-gray-300 px-4 py-2 text-left">Role</th>
              <th className="border border-gray-300 px-4 py-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 ? (
              <tr>
                <td colSpan={4} className="border border-gray-300 px-4 py-2 text-center text-gray-500">
                  No users found
                </td>
              </tr>
            ) : (
              users.map((user: any) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-medium">{user.username}</td>
                  <td className="border border-gray-300 px-4 py-2">{user.display_name || "-"}</td>
                  <td className="border border-gray-300 px-4 py-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      user.role === "admin" ? "bg-red-100 text-red-800" :
                      user.role === "editor" ? "bg-blue-100 text-blue-800" :
                      "bg-gray-100 text-gray-800"
                    }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="border border-gray-300 px-4 py-2">
                    <div className="flex gap-2">
                      <button
                        onClick={() => startEdit(user)}
                        className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteUser(user.id, user.username)}
                        className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}