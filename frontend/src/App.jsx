import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import NewsPage from "./pages/NewsPage.jsx";
import CreateNews from "./pages/CreateNews.jsx";
import EditNews from "./pages/EditNews.jsx"; 
import Profile from "./pages/Profile.jsx";
import Header from "./components/Header.jsx";

export default function App() {
  return (
    <>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/news/:id" element={<NewsPage />} />
        <Route path="/create" element={<CreateNews />} />
        <Route path="/edit/:id" element={<EditNews />} />   
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </>
  );
}
