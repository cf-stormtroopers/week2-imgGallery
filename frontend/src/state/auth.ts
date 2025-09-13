import { create } from "zustand";
import { logoutAuthLogoutPost, type UserResponseDTO } from "../api/generated";
import { mutate } from "swr";

export interface Settings {
    site_title: string
    allow_registration: boolean
}

export function convertSettingsDictToSettings(settings: Record<string, string>): Settings {
    return {
        site_title: settings["site_title"] || "",
        allow_registration: settings["allow_registration"] === "true"
    }
}

const EmptySettings: Settings = {
    site_title: "",
    allow_registration: false
}

export interface AuthState {
    accountInformation: UserResponseDTO | null;
    settings: Settings;

    setAccountInformation: (info: UserResponseDTO | null) => void;
    setSettings: (settings: Settings) => void;
    reset: () => void;

    logout: () => Promise<void>
    mutate: () => void
    setMutate: (mutate: () => void) => void
}

export const useAuthStore = create<AuthState>((set) => ({
    accountInformation: null,
    settings: EmptySettings,

    setAccountInformation: (info) => set({ accountInformation: info }),
    setSettings: (settings) => set({ settings: settings }),

    reset: () =>
        set({
            settings: EmptySettings,
            accountInformation: null,
        }),

    logout: async () => {
        await logoutAuthLogoutPost()
        set({
            settings: EmptySettings,
            accountInformation: null,
        })
    },

    mutate: () => mutate("/site/info"),
    setMutate: (mutate) => set({ mutate }),
}));
