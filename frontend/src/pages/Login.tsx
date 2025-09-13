import { useState } from "react";
import { useLocation } from "wouter";
import { useLoginAuthLoginPost } from "../api/generated";
import { useAuthStore } from "../state/auth";

export default function LoginPage() {
    const auth = useAuthStore();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const { trigger: login, isMutating } = useLoginAuthLoginPost();
    const [, setLocation] = useLocation()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        try {
            const res = await login({ username: email, password });
            console.log(res)
            if (res?.ok === "true") {
                await auth.mutate()
                setLocation("/");
            } else {
                alert("❌ Login failed. Please check your credentials and try again.");
            }
        } catch (err) {
            setError("❌ Login failed. Please check your credentials and try again.");
        }
    };

    return <div className="flex items-center justify-center h-screen">
        <form className="bg-white p-6 rounded shadow flex flex-col gap-6">
            <h2 className="text-2xl font-bold">Login to Image Gallery</h2>
            {error && <p className="text-red-600">{error}</p>}
            <div className="flex flex-col">
                <label className="font-bold mb-2">Username</label>
                <input
                    type="text"
                    className="border rounded px-3 py-2 focus:ring-2 focus:ring-sky-800"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    required
                />
            </div>
            <div className="flex flex-col">
                <label className="font-bold mb-2">Password</label>
                <input
                    type="password"
                    className="border rounded px-3 py-2 focus:ring-2 focus:ring-sky-800"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    required
                />
            </div>
            <button
                type="submit"
                className="bg-sky-800 text-white font-bold rounded-md px-4 py-2 hover:bg-sky-900 cursor-pointer disabled:opacity-50"
                disabled={isMutating}
                onClick={handleSubmit}
            >
                {isMutating ? "Logging in..." : "Login"}
            </button>
        </form>
    </div>
}