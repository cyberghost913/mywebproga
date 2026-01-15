import { createContext, useContext, useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";

const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [access, setAccess] = useState(localStorage.getItem("access") || null);
  const [refresh, setRefresh] = useState(localStorage.getItem("refresh") || null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (access) {
      try {
        const decoded = jwtDecode(access);
        setUser({
          id: decoded.id,
          username: decoded.username,
          is_admin: !!decoded.is_admin,
          is_active: !!decoded.is_active,
          is_author: !!decoded.is_author,
        });
      } catch (e) {
        console.error("Invalid access token:", e);
        logout();
      }
    } else {
      setUser(null);
    }
  }, [access]);

  const login = (accessToken, refreshToken) => {
    localStorage.setItem("access", accessToken);
    localStorage.setItem("refresh", refreshToken);
    setAccess(accessToken);
    setRefresh(refreshToken);
  };

  const logout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setAccess(null);
    setRefresh(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, access, refresh, login, logout, setAccess, setRefresh }}>
      {children}
    </AuthContext.Provider>
  );
};
