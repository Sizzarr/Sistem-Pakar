# Sistem Pakar Diagnosa Gangguan Tidur (FastAPI + MySQL Laragon)

Kamu minta nama tabelnya "Indonesia banget". Jadi iya: penyakit, gejala, aturan, solusi, diagnosa. Hidup jadi tenang.

## 1) Setup Database (Laragon)
1. Jalankan Laragon (Start All).
2. Buat database: `sistem_pakar_tidur`
3. Import `db_init.sql` (phpMyAdmin / HeidiSQL).

Tabel yang dipakai:
- `penyakit`
- `gejala`
- `aturan`
- `solusi` (kode S01, S02, ...)
- `sesi_diagnosa`
- `jawaban_diagnosa`
- `riwayat_diagnosa`

## 2) Setup Backend
Masuk folder `backend/`

### Windows (PowerShell)
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` kalau MySQL kamu pakai password / user beda.

### Run server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Buka:
- Website: http://127.0.0.1:8000
- Docs API: http://127.0.0.1:8000/docs

## 3) Alur Diagnosa (sesuai permintaan kamu)
1. Halaman diagnosa cuma tampil biodata.
2. Setelah biodata diisi, muncul pilihan penyakit yang mau dicek.
3. Sistem menanyakan gejala satu per satu (Ya/Tidak) sesuai aturan penyakit itu.
4. Hasil akhir menampilkan:
   - Biodata
   - Penyakit yang dicek + status (TERDETEKSI / TIDAK)
   - Pengertian, penyebab, solusi (S01, S02, dst)
5. Riwayat otomatis masuk `riwayat_diagnosa`.

Kalimat saat tidak memenuhi:
> "Berdasarkan jawaban kamu, gejala belum cukup untuk menyimpulkan penyakit yang dipilih. Sistem ini hanya memeriksa penyakit yang ada di basis pengetahuan. Kalau keluhan kamu mengganggu aktivitas atau makin berat, sebaiknya konsultasi tenaga kesehatan."

