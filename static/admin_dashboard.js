const token = localStorage.getItem("token");
const btnLogout = document.getElementById("btnLogout");

const tblDiseases = document.getElementById("tblDiseases");
const tblSymptoms = document.getElementById("tblSymptoms");
const formDisease = document.getElementById("formDisease");
const formSymptom = document.getElementById("formSymptom");

const ruleDisease = document.getElementById("ruleDisease");
const ruleSymptoms = document.getElementById("ruleSymptoms");
const btnSaveRule = document.getElementById("btnSaveRule");

let diseases = [];
let symptoms = [];
let rules = {};

if (!token) location.href = "/admin/login";

async function api(path, opts = {}) {
  opts.headers = Object.assign({}, opts.headers || {}, {
    Authorization: `Bearer ${token}`,
  });
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));
}

function render() {
  tblDiseases.innerHTML = diseases.map(d => `
    <tr class="border-t">
      <td class="p-2 font-mono">${esc(d.code)}</td>
      <td class="p-2">${esc(d.name)}</td>
      <td class="p-2">${esc(d.priority)}</td>
      <td class="p-2">
        <button data-edit-d="${esc(d.code)}" class="text-blue-600 hover:underline">Edit</button>
        <button data-del-d="${esc(d.code)}" class="ml-3 text-rose-600 hover:underline">Hapus</button>
      </td>
    </tr>
  `).join("");

  tblSymptoms.innerHTML = symptoms.map(s => `
    <tr class="border-t">
      <td class="p-2 font-mono">${esc(s.code)}</td>
      <td class="p-2">${esc(s.question)}</td>
      <td class="p-2">
        <button data-edit-s="${esc(s.code)}" class="text-blue-600 hover:underline">Edit</button>
        <button data-del-s="${esc(s.code)}" class="ml-3 text-rose-600 hover:underline">Hapus</button>
      </td>
    </tr>
  `).join("");

  ruleDisease.innerHTML = diseases.map(d => `<option value="${esc(d.code)}">${esc(d.code)} - ${esc(d.name)}</option>`).join("");
  ruleSymptoms.innerHTML = symptoms.map(s => `<option value="${esc(s.code)}">${esc(s.code)} - ${esc(s.question)}</option>`).join("");

  applyRuleSelection();
}

function applyRuleSelection() {
  const dcode = ruleDisease.value;
  const selected = new Set((rules[dcode] || []));
  for (const opt of ruleSymptoms.options) {
    opt.selected = selected.has(opt.value);
  }
}

async function loadAll() {
  diseases = await api("/api/diseases");
  symptoms = await api("/api/symptoms");
  rules = await api("/api/rules");
  render();
}

formDisease?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(formDisease);
  const payload = {
    code: fd.get("code"),
    name: fd.get("name"),
    description: fd.get("description"),
    priority: Number(fd.get("priority") || 100),
  };

  try {
    await api(`/api/diseases/${payload.code}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).catch(async (err) => {
      if (String(err.message).includes("tidak ditemukan")) {
        return api("/api/diseases", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }
      throw err;
    });
    await loadAll();
    formDisease.reset();
  } catch (err) {
    alert(err.message);
  }
});

formSymptom?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(formSymptom);
  const payload = { code: fd.get("code"), question: fd.get("question") };

  try {
    await api(`/api/symptoms/${payload.code}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).catch(async (err) => {
      if (String(err.message).includes("tidak ditemukan")) {
        return api("/api/symptoms", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }
      throw err;
    });
    await loadAll();
    formSymptom.reset();
  } catch (err) {
    alert(err.message);
  }
});

tblDiseases?.addEventListener("click", async (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  const edit = btn.getAttribute("data-edit-d");
  const del = btn.getAttribute("data-del-d");

  if (edit) {
    const d = diseases.find(x => x.code === edit);
    if (!d) return;
    formDisease.code.value = d.code;
    formDisease.name.value = d.name;
    formDisease.priority.value = d.priority;
    formDisease.description.value = d.description;
  }
  if (del) {
    if (!confirm(`Hapus penyakit ${del}?`)) return;
    try {
      await api(`/api/diseases/${del}`, { method: "DELETE" });
      await loadAll();
    } catch (err) {
      alert(err.message);
    }
  }
});

tblSymptoms?.addEventListener("click", async (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  const edit = btn.getAttribute("data-edit-s");
  const del = btn.getAttribute("data-del-s");

  if (edit) {
    const s = symptoms.find(x => x.code === edit);
    if (!s) return;
    formSymptom.code.value = s.code;
    formSymptom.question.value = s.question;
  }
  if (del) {
    if (!confirm(`Hapus gejala ${del}?`)) return;
    try {
      await api(`/api/symptoms/${del}`, { method: "DELETE" });
      await loadAll();
    } catch (err) {
      alert(err.message);
    }
  }
});

ruleDisease?.addEventListener("change", applyRuleSelection);

btnSaveRule?.addEventListener("click", async () => {
  const dcode = ruleDisease.value;
  const selected = Array.from(ruleSymptoms.selectedOptions).map(o => o.value);
  try {
    await api(`/api/diseases/${dcode}/symptoms`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symptom_codes: selected }),
    });
    await loadAll();
    alert("Rules tersimpan.");
  } catch (err) {
    alert(err.message);
  }
});

btnLogout?.addEventListener("click", () => {
  localStorage.removeItem("token");
  location.href = "/admin/login";
});

loadAll().catch(err => {
  alert(err.message);
  localStorage.removeItem("token");
  location.href = "/admin/login";
});
