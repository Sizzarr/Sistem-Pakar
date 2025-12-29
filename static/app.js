const startBox = document.getElementById("startBox");
const qaBox = document.getElementById("qaBox");
const resultBox = document.getElementById("resultBox");

const btnStart = document.getElementById("btnStart");
const btnYes = document.getElementById("btnYes");
const btnNo = document.getElementById("btnNo");
const btnReset = document.getElementById("btnReset");
const btnAgain = document.getElementById("btnAgain");

const sessionIdEl = document.getElementById("sessionId");
const questionText = document.getElementById("questionText");
const questionCode = document.getElementById("questionCode");

const resultMain = document.getElementById("resultMain");
const resultSymptoms = document.getElementById("resultSymptoms");

let sessionId = null;
let currentQuestion = null;

async function api(path, opts) {
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

function showQuestion(q) {
  currentQuestion = q;
  questionText.textContent = q.question;
  questionCode.textContent = q.code;
  startBox.classList.add("hidden");
  resultBox.classList.add("hidden");
  qaBox.classList.remove("hidden");
  sessionIdEl.textContent = sessionId;
}

function showResult(result) {
  qaBox.classList.add("hidden");
  resultBox.classList.remove("hidden");

  if (!result.disease) {
    resultMain.innerHTML = `<div class="mt-2 text-rose-700 font-semibold">${result.note || "Tidak dapat mendiagnosis."}</div>`;
    resultSymptoms.innerHTML = "";
    return;
  }

  resultMain.innerHTML = `
    <div class="mt-2">
      <div class="text-sm text-slate-500">Diagnosa</div>
      <div class="text-xl font-bold">${result.disease.name} <span class="text-sm font-mono text-slate-500">(${result.disease.code})</span></div>
      <div class="mt-2 text-slate-700">${result.disease.description}</div>
      <div class="mt-3 text-sm">
        <span class="inline-flex items-center rounded-full bg-emerald-100 text-emerald-800 px-3 py-1">
          Keyakinan: ${result.confidence ?? "-"}%
        </span>
      </div>
    </div>
  `;

  const list = result.matched_symptoms || [];
  if (list.length === 0) {
    resultSymptoms.innerHTML = "";
  } else {
    resultSymptoms.innerHTML = `
      <div class="mt-4">
        <div class="text-sm text-slate-500">Gejala terpenuhi</div>
        <ul class="mt-2 list-disc pl-5">
          ${list.map(s => `<li><span class="font-mono text-xs text-slate-500">${s.code}</span> ${s.question}</li>`).join("")}
        </ul>
      </div>
    `;
  }
}

async function start() {
  const data = await api("/api/diagnosis/start", { method: "POST" });
  sessionId = data.session_id;
  if (data.status === "asking" && data.question) showQuestion(data.question);
  else showResult({ disease: null, note: "Sesi selesai tanpa pertanyaan." });
}

async function answer(val) {
  if (!sessionId || !currentQuestion) return;
  const payload = { symptom_code: currentQuestion.code, answer: val };
  const data = await api(`/api/diagnosis/${sessionId}/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (data.status === "asking" && data.question) showQuestion(data.question);
  else showResult(data.result);
}

function reset() {
  sessionId = null;
  currentQuestion = null;
  qaBox.classList.add("hidden");
  resultBox.classList.add("hidden");
  startBox.classList.remove("hidden");
}

btnStart?.addEventListener("click", () => start().catch(e => alert(e.message)));
btnYes?.addEventListener("click", () => answer(true).catch(e => alert(e.message)));
btnNo?.addEventListener("click", () => answer(false).catch(e => alert(e.message)));
btnReset?.addEventListener("click", reset);
btnAgain?.addEventListener("click", reset);
