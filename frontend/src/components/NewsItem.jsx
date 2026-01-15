import React from "react";
import { Link } from "react-router-dom";
import "../styles/news.css";

export default function NewsItem({ news }) {
  const formatDate = (d) => {
    if (!d) return "—";
    try {
      const dt = new Date(d);
      if (isNaN(dt)) return String(d);
      return dt.toLocaleString();
    } catch {
      return String(d);
    }
  };

  const author = news.author_name ?? news.author ?? news.author_id ?? "—";

  return (
    <article className="news-item">
      <Link to={`/news/${news.id}`} className="news-link">
        <h3 className="news-item-title">{news.header}</h3>
      </Link>

      <div className="news-meta">
        Автор: {author}  •  Дата: {formatDate(news.date ?? news.created_at ?? news.date)}
      </div>
    </article>
  );
}
