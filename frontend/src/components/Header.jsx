import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header style={{ display: "flex", gap: "12px", padding: "12px", borderBottom: "1px solid #ddd" }}>
      <Link to="/">Home</Link>
      <div style={{ marginLeft: "auto" }}>
        {!user && <Link to="/login">Войти</Link>}
        {user && (
          <>
            <Link to="/profile">Профиль ({user.username})</Link>
            <button
              onClick={() => {
                logout();
                navigate("/");
              }}
            >
              Выйти
            </button>
          </>
        )}
      </div>
    </header>
  );
}