const form = document.getElementById("loginForm");
const msg = document.getElementById("loginMsg");

async function api(path, opts) {
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

form?.addEventListener("submit", async (e) => {
  e.preventDefault();
  msg.textContent = "";
  const fd = new FormData(form);
  const payload = { email: fd.get("email"), password: fd.get("password") };

  try {
    const data = await api("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    localStorage.setItem("token", data.access_token);
    location.href = "/admin";
  } catch (err) {
    msg.textContent = err.message;
  }
});
