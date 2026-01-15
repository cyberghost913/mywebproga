import React, { useState } from "react";

export default function CommentForm({ onSubmit, disabled }) {
  const [text, setText] = useState("");
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSubmit({ text });
    setText("");
  };
  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <textarea value={text} onChange={(e) => setText(e.target.value)} rows={4} placeholder="Ваш комментарий" disabled={disabled} />
      <div>
        <button type="submit" disabled={disabled}>
          Отправить
        </button>
      </div>
    </form>
  );
}
