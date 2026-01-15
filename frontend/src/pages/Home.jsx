import { useEffect, useState } from "react";
import { fetchNews } from "../api/news.js";
import { useNavigate } from "react-router-dom";
import NewsList from "../components/NewsList.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import "../styles/news.css";

export default function Home() {
  const [news, setNews] = useState([]);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchNews()
      .then((data) => {
        // ensure array
        setNews(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        console.error("Failed to load news:", err);
      });
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <div className="news-header-row">
        <h2 className="news-title">Новости</h2>
        {(user?.is_author || user?.is_admin) && (
          <button className="btn-add-news" onClick={() => navigate("/create")}>
            Добавить новость
          </button>
        )}
      </div>

      <NewsList items={news} />
    </div>
  );
}
