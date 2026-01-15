import React from "react";
import NewsItem from "./NewsItem.jsx";

export default function NewsList({ items }) {
  if (!items || items.length === 0) return <div>Новости отсутствуют</div>;
  return (
    <div style={{ display: "grid", gap: 12 }}>
      {items.map((n) => (
        <NewsItem key={n.id} news={n} />
      ))}
    </div>
  );
}
