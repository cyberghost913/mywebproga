import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchOneNews, updateNews } from "../api/news.js";
import { useAuth } from "../context/AuthContext.jsx";

export default function EditNews() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [news, setNews] = useState(null);
  const [header, setHeader] = useState("");
  const [contentText, setContentText] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchOneNews(id)
      .then((n) => {
        setNews(n);
        setHeader(n?.header ?? "");
        try {
          const c = n?.content;
          if (!c) setContentText("");
          else if (typeof c === "string") setContentText(c);
          else if (c.blocks && Array.isArray(c.blocks)) {
            setContentText(c.blocks.map((b) => b.data?.text ?? "").join("\n\n"));
          } else setContentText(JSON.stringify(c, null, 2));
        } catch {
          setContentText("");
        }
      })
      .catch((err) => {
        console.error("Failed to load news:", err);
      });
  }, [id]);

  if (!news) return <p style={{ padding: 20 }}>Загрузка...</p>;

  if (!user) return <p style={{ padding: 20 }}>Требуется авторизация</p>;
  const canManage = user.is_admin || Number(user.id) === Number(news.author_id);
  if (!canManage) return <p style={{ padding: 20 }}>Нет прав для редактирования</p>;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        header,
        content: { blocks: [{ type: "paragraph", data: { text: contentText } }] },
        author_id: user.id,
      };
      await updateNews(id, payload);
      navigate(`/news/${id}`);
    } catch (err) {
      console.error("update news failed:", err);
      if (err?.response?.status === 422) {
        alert("Ошибка 422. Проверьте формат полей.");
      } else {
        alert("Не удалось обновить новость");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Редактировать новость</h2>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 10, maxWidth: 900 }}>
        <input required placeholder="Заголовок" value={header} onChange={(e) => setHeader(e.target.value)} />
        <textarea required placeholder="Содержимое" rows={10} value={contentText} onChange={(e) => setContentText(e.target.value)} />
        <div>
          <button type="submit" disabled={loading}>{loading ? "Сохранение..." : "Сохранить"}</button>
          <button type="button" onClick={() => navigate(-1)} style={{ marginLeft: 8 }}>Отмена</button>
        </div>
      </form>
    </div>
  );
}
