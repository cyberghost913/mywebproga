import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createNews } from "../api/news.js";
import { useAuth } from "../context/AuthContext.jsx";

export default function CreateNews() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [header, setHeader] = useState("");
  const [contentText, setContentText] = useState("");
  const [loading, setLoading] = useState(false);

  if (!user) return <p style={{ padding: 20 }}>Требуется авторизация</p>;
  if (!user.is_admin && !user.is_author) return <p style={{ padding: 20 }}>Нет доступа</p>;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        header,
        content: { blocks: [{ type: "paragraph", data: { text: contentText } }] },
        author_id: user.id,
      };

      await createNews(payload);
      navigate("/");
    } catch (err) {
      console.error("create news failed:", err);
      alert("Не удалось создать новость");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Создать новость</h2>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 10, maxWidth: 800 }}>
        <input required placeholder="Заголовок" value={header} onChange={(e) => setHeader(e.target.value)} />
        <textarea required placeholder="Содержимое" rows={8} value={contentText} onChange={(e) => setContentText(e.target.value)} />
        <div>
          <button type="submit" disabled={loading}>{loading ? "Создание..." : "Создать"}</button>
        </div>
      </form>
    </div>
  );
}
