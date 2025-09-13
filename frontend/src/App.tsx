import { Redirect, Route, Switch } from "wouter";
import HomePage from "./pages/HomePage";
import AddPhotoToGallery from "./pages/AddPhotoToGallery";
import AllAlbums from "./pages/AllAlbums";
import AlbumDetailPage from "./pages/AlbumDetailPage";
import LightboxPage from "./pages/LightboxPage";
import { useGetSiteInfoSiteInfoGet } from "./api/generated";
import { useEffect } from "react";
import { convertSettingsDictToSettings, useAuthStore } from "./state/auth";
import ProfilePage from "./pages/Profile";
import LoginPage from "./pages/Login";

export default function App() {
  const authStore = useAuthStore()
  const { data: siteInfo, mutate } = useGetSiteInfoSiteInfoGet()

  useEffect(() => {
    if (siteInfo) {
      console.log("SEttings...")
      authStore.setMutate(() => mutate())
      authStore.setAccountInformation(siteInfo.user || null)
      authStore.setSettings(
        convertSettingsDictToSettings(
          siteInfo.settings
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
    {authStore.accountInformation ? <Switch>
      <Route path="/" component={HomePage} />
      <Route path="/add" component={AddPhotoToGallery} />
      <Route path="/albums" component={AllAlbums} />
      <Route path="/albums/:id" component={AlbumDetailPage} />
      <Route path="/albums/new" component={AlbumDetailPage} />
      <Route path="/image/:id" component={LightboxPage} />
      <Route path="/profile" component={ProfilePage} />
      <Route path="*"><Redirect to="/" /></Route>
    </Switch> : <Switch>
      <Route path="/" component={HomePage} />
      {/* <Route path="/add" component={AddPhotoToGallery} /> */}
      <Route path="/albums" component={AllAlbums} />
      <Route path="/albums/:id" component={AlbumDetailPage} />
      {/* <Route path="/albums/new" component={AlbumDetailPage} /> */}
      <Route path="/image/:id" component={LightboxPage} />
      <Route path="/profile"><Redirect to="/login" /></Route>
      <Route path="/login" component={LoginPage} />
      <Route path="*"><Redirect to="/" /></Route>
    </Switch>}
  </main>
}