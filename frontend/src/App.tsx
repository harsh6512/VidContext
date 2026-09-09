import HomeLayout from "@/layouts/HomeLayout";
import LearnLayout from "@/layouts/LearnLayout";
import LandingPage from "@/pages/LandingPage";
import Signup from "@/pages/Signup";
import LoginPage from "@/pages/LoginPage";
import SearchPage from "@/pages/SearchPage";
import LearningPage from "@/pages/LearningPage";
import { createBrowserRouter, redirect, RouterProvider } from "react-router";
import { GlobalContextProvider } from "@/context/GlobalContext";
import { Toaster } from "react-hot-toast";

const authCheck = () => {
  const userData = localStorage.getItem("you-user");
  const user = userData ? JSON.parse(userData) : null;

  if (!user) return redirect("/login");
  return null;
}

const guestOnlyCheck = () => {
  const userData = localStorage.getItem("you-user");
  const user = userData ? JSON.parse(userData) : null;

  if (user) return redirect("/learn");
  return null;
}

const router = createBrowserRouter([
  {
    path: "/",
    Component: HomeLayout,
    children: [
      { index: true, Component: LandingPage, loader: guestOnlyCheck },
      { path: "signup", Component: Signup, loader: guestOnlyCheck },
      { path: "login", Component: LoginPage, loader: guestOnlyCheck },
    ],
  },
  {
    path: "/learn",
    Component: LearnLayout,
    loader: authCheck,
    children: [
      { index: true, Component: SearchPage },
      { path: ":id", Component: LearningPage },
    ],
  }
]);

function App() {
  return (
    <GlobalContextProvider>
      <RouterProvider router={router} />
      <Toaster />
    </GlobalContextProvider>
  );
}

export default App;
