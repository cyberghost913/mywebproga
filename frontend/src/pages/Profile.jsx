import { useAuth } from "../context/AuthContext.jsx";
import { getSessions } from "../api/auth.js";
import { useEffect, useState } from "react";
import "../styles/profile.css";

export default function Profile() {
  const { user, refresh, logout } = useAuth();
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    if (!user) return;
    getSessions()
      .then((s) => setSessions(s))
      .catch((e) => {
        console.error("Failed to load sessions:", e);
      });
  }, [user]);

  if (!user) return <p style={{ padding: 20 }}>Неавторизован</p>;
  return (
    <div style={{ padding: 20 }}>
      <h2>Профиль</h2>
      <p>ID: {user.id}</p>
      <p>Имя: {user.username}</p>
      <p>Автор: {user.is_author ? "Да" : "Нет"}</p>
      <p>Админ: {user.is_admin ? "Да" : "Нет"}</p>

      <h3 style={{ marginTop: 20 }}>Открытые сессии</h3>
      {sessions.length === 0 && <div>Сессий не найдено</div>}
      {sessions.map((s, i) => (
        <div key={i} className="session-card">
          <div><b>UA:</b> {s.user_agent ?? "—"}</div>
          <div><b>IP:</b> {s.ip_address ?? "—"}</div>
          <div><b>Создана:</b> {s.created_at ?? "—"}</div>
          <div><b>Последняя активность:</b> {s.last_used_at ?? "—"}</div>
        </div>
      ))}

      <div style={{ marginTop: 16 }}>
        <button onClick={() => logout()}>Выйти</button>
      </div>
    </div>
  );
}
