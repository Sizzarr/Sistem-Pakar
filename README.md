# Sistem Pakar Diagnosa Gangguan Tidur (FastAPI + MySQL/Laragon + Tailwind)

Ini versi **website** dari program CLI kamu (backward chaining goal-driven).
Knowledge base (penyakit, gejala, rules) di-seed dari data yang kamu kirim.

## Fitur
- Diagnosa **tanpa login** (guest).
- Backward chaining via sesi: `/api/diagnosis/start` lalu `/api/diagnosis/{session_id}/answer`.
- CRUD (Admin, pakai login JWT):
  - Penyakit
  - Gejala
  - Rules (relasi penyakit-gejala)

## Setup cepat (Windows + Laragon)
1. Buat database di phpMyAdmin/Laragon:
   - Nama: `sistem_pakar_tidur`
2. Copy `.env.example` jadi `.env` dan sesuaikan:
   - `DATABASE_URL` (default Laragon biasanya user `root` tanpa password)
   - `JWT_SECRET` ganti yang unik
   - (opsional) set `FIRST_ADMIN_EMAIL` + `FIRST_ADMIN_PASSWORD`
3. Install dependency:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Jalankan server:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Buka:
   - Website: http://127.0.0.1:8000
   - Swagger: http://127.0.0.1:8000/docs

## Login Admin (opsional)
- Kalau tabel `users` masih kosong dan kamu set `FIRST_ADMIN_EMAIL/PASSWORD`,
  sistem akan auto-create 1 admin saat startup.
- Login: `POST /api/auth/login` (lihat di Swagger).
- Untuk CRUD, klik "Authorize" di Swagger pakai `Bearer <token>`.

## Catatan
- Tailwind dipakai via CDN.
- Ini aplikasi edukasi, bukan pengganti dokter.
