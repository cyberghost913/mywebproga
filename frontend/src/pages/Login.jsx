import { useState } from "react";
import { loginRequest } from "../api/auth.js";
import { useAuth } from "../context/AuthContext.jsx";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await loginRequest(username, password);
      login(res.value, res.refresh_token);
      navigate("/");
    } catch (err) {
      console.error("Login failed:", err);
      alert("Ошибка авторизации");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "10px", maxWidth: 420 }}>
      <h2>Вход</h2>
      <input placeholder="Логин" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input placeholder="Пароль" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button type="submit" disabled={loading}>
        {loading ? "Выполняется..." : "Войти"}
      </button>
    </form>
  );
}
