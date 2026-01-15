import React from "react";

export default function CommentList({ comments, onDelete, currentUser }) {
  if (!comments || comments.length === 0) return <div>Комментарии отсутствуют</div>;
  return (
    <ul style={{ paddingLeft: 0 }}>
      {comments.map((c) => (
        <li key={c.id} style={{ listStyle: "none", marginBottom: 12, padding: 8, border: "1px solid #eee", borderRadius: 6 }}>
          <div style={{ fontWeight: "bold" }}>{c.author_name ?? `User ${c.author_id}`}</div>
          <div style={{ marginTop: 6 }}>{c.text}</div>
          <div style={{ fontSize: 12, color: "#666", marginTop: 6 }}>Комментарий ID: {c.id}</div>
          {(currentUser?.is_admin || currentUser?.id === c.author_id) && (
            <div style={{ marginTop: 6 }}>
              <button onClick={() => onDelete?.(c.id)}>Удалить</button>
            </div>
          )}
        </li>
      ))}
    </ul>
  );
}
