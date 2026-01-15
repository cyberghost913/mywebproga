import { api } from "./api";

export const fetchComments = () => api.get("/comments/").then((r) => r.data);
export const createComment = (payload) => api.post("/comments/", payload).then((r) => r.data);
export const deleteComment = (id) => api.delete(`/comments/${id}`).then((r) => r.data);
export const updateComment = (id, payload) => api.put(`/comments/${id}`, payload).then((r) => r.data);
