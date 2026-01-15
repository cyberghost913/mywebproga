import { api } from "./api";

export const loginRequest = async (username, password) => {
  const params = new URLSearchParams();
  params.append("username", username);
  params.append("password", password);
  const { data } = await api.post("/auth/login", params);
  return data;
};

export const refreshTokenRequest = async (refresh_token) => {
  const { data } = await api.post("/auth/refresh", { refresh_token });
  return data;
};

export const logoutRequest = async (refresh_token) => {
  const { data } = await api.post("/auth/logout", { refresh_token });
  return data;
};

export const getSessions = async () => {
  const { data } = await api.get("/auth/sessions");
  return data;
};
