import { Redirect, Route, Switch } from "wouter";
import HomePage from "./pages/HomePage";
import AddPhotoToGallery from "./pages/AddPhotoToGallery";
import AllAlbums from "./pages/AllAlbums";
import AlbumDetailPage from "./pages/AlbumDetailPage";
import LightboxPage from "./pages/LightboxPage";
import { useGetSiteInfoSiteInfoGet } from "./api/generated";
import { useEffect } from "react";
import { convertSettingsDictToSettings, useAuthStore } from "./state/auth";

export default function App() {
  const authStore = useAuthStore()
  const { data: siteInfo } = useGetSiteInfoSiteInfoGet()

  useEffect(() => {
    if (siteInfo) {
      authStore.setAccountInformation(siteInfo.user || null)
      authStore.setSettings(
        convertSettingsDictToSettings(
          siteInfo.settings && typeof siteInfo.settings === "object"
            ? Object.fromEntries(
                Object.entries(siteInfo.settings).map(([k, v]) => [k, String(v)])
              )
            : {}
        )
      )
    }
  }, [siteInfo])

  console.log("App!")

  return <main>
    <Switch>
      <Route path="/" component={HomePage} />
      <Route path="/add" component={AddPhotoToGallery} />
      <Route path="/albums" component={AllAlbums} />
      <Route path="/albums/:id" component={AlbumDetailPage} />
      <Route path="/albums/new" component={AlbumDetailPage} />
      <Route path="/image/:id" component={LightboxPage} />
      <Route path="*"><Redirect to="/" /></Route>
    </Switch>
  </main>
}