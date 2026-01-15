import { api } from "./api";

export const fetchNews = () => api.get("/news/").then((r) => r.data);
export const fetchOneNews = (id) => api.get(`/news/${id}`).then((r) => r.data);

export const createNews = (payload) => {
  return api.post("/news/", payload).then((r) => r.data);
};

export const updateNews = (id, payload) => {
  return api.put(`/news/${id}`, payload).then((r) => r.data);
};

export const deleteNews = (id) => api.delete(`/news/${id}`).then((r) => r.data);
