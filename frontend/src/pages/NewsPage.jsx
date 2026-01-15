import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchOneNews, deleteNews } from "../api/news.js";
import { fetchComments, createComment, deleteComment } from "../api/comments.js";
import { useAuth } from "../context/AuthContext.jsx";
import CommentList from "../components/CommentList.jsx";
import CommentForm from "../components/CommentForm.jsx";

export default function NewsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [news, setNews] = useState(null);
  const [comments, setComments] = useState([]);

  useEffect(() => {
    fetchOneNews(id)
      .then(setNews)
      .catch((err) => {
        console.error("Failed to load news:", err);
      });

    fetchComments()
      .then((all) => setComments(all.filter((c) => Number(c.news_id) === Number(id))))
      .catch((err) => {
        console.error("Failed to load comments:", err);
      });
  }, [id]);

  const submitComment = async (payload) => {
    try {
      const newComment = await createComment({ ...payload, news_id: Number(id) });
      if (Number(newComment.news_id) === Number(id)) setComments((p) => [...p, newComment]);
    } catch (e) {
      console.error("Failed to create comment:", e);
      alert("Не удалось отправить комментарий");
    }
  };

  const handleDeleteComment = async (commentId) => {
    try {
      await deleteComment(commentId);
      setComments((p) => p.filter((c) => c.id !== commentId));
    } catch (e) {
      console.error("Failed to delete comment:", e);
      alert("Не удалось удалить комментарий");
    }
  };

  const handleDeleteNews = async () => {
    if (!confirm("Удалить новость?")) return;
    try {
      await deleteNews(id);
      navigate("/");
    } catch (e) {
      console.error("Failed to delete news:", e);
      alert("Не удалось удалить новость");
    }
  };

  if (!news) return <p style={{ padding: 20 }}>Загрузка...</p>;

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
  const canManage = user && (user.is_admin || Number(user.id) === Number(news.author_id));

  return (
    <div style={{ padding: 20 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <h2 style={{ margin: 0 }}>{news.header}</h2>
        <div style={{ color: "#666" }}> {author} • {formatDate(news.date ?? news.created_at ?? news.date)}</div>
        {canManage && (
          <>
            <button className="btn-small" onClick={() => navigate(`/edit/${news.id}`)}>Редактировать</button>
            <button className="btn-small btn-danger" onClick={handleDeleteNews}>Удалить</button>
          </>
        )}
      </div>

      <div style={{ marginTop: 12 }}>
        {(() => {
          try {
            const c = news.content;
            if (!c) return null;
            if (typeof c === "string") return <div>{c}</div>;
            if (c.blocks && Array.isArray(c.blocks)) {
              return c.blocks.map((b, i) => <p key={i} dangerouslySetInnerHTML={{ __html: b.data.text }} />);
            }
            return <pre>{JSON.stringify(c)}</pre>;
          } catch {
            return <pre>{JSON.stringify(news.content)}</pre>;
          }
        })()}
      </div>

      <hr style={{ margin: "20px 0" }} />

      <h3>Комментарии</h3>
      <CommentList comments={comments} onDelete={handleDeleteComment} currentUser={user} />
      {user ? <CommentForm onSubmit={submitComment} /> : <p>Чтобы оставить комментарий — войдите в систему.</p>}
    </div>
  );
}
