import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { useAuthStore } from "../state/auth";
import { logoutAuthLogoutPost, updateSiteSettingsSiteSettingsPost } from "../api/generated";
import UserManager from "../components/UserManager";

export default function ProfilePage() {
    const auth = useAuthStore();
    const [siteName, setSiteName] = useState(auth.settings?.site_title || "");

    async function saveSiteTitle() {
        try {
            await updateSiteSettingsSiteSettingsPost({
                key: "site_name",
                value: siteName
            });
            auth.mutate();
            alert("Site title updated!");
        } catch (_) {
            alert("Failed to update site title.");
        }
    }

    async function logout() {
        try {
            await logoutAuthLogoutPost();
            auth.setAccountInformation(null);
            auth.mutate();
        } catch (_) {
            alert("Failed to log out.");
        }
    }

    useEffect(() => {
        setSiteName(auth.settings?.site_title || "");
    }, [auth.settings?.site_title]);

    return <Layout>
        <div className="flex flex-col p-6">
            <h2 className="font-bold text-2xl">Profile</h2>
            <p><span className="font-bold">Username</span> {auth.accountInformation?.username}</p>
            <p><span className="font-bold">Display Name</span> {auth.accountInformation?.display_name}</p>
            <button className="text-red-800 underline text-left" onClick={logout}>Logout</button>

            <div className="h-4"></div>

            {auth.accountInformation?.role === "admin" && <><h2 className="font-bold text-2xl">Settings</h2>
                <div className="flex flex-col max-w-[30rem]">
                    <label className="">Site Name</label>
                    <input
                        type="text"
                        className="border rounded px-3 py-2 focus:ring-2 focus:ring-sky-800"
                        value={siteName}
                        onChange={e => setSiteName(e.target.value)}
                    />
                    <button className="mt-2 bg-sky-800 rounded-md shadow font-bold text-white p-2 px-4 w-min" onClick={saveSiteTitle}>Save</button>
                </div></>}

            <div className="h-4"></div>

            {auth.accountInformation?.role === "admin" && <><h2 className="font-bold text-2xl">Users</h2>
                <UserManager /></>}
        </div>
    </Layout>;
}