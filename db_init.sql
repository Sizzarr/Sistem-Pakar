-- Database: sistem_pakar_tidur
-- Import lewat phpMyAdmin / HeidiSQL (Laragon)

SET NAMES utf8mb4;
SET time_zone = '+00:00';

DROP TABLE IF EXISTS jawaban_diagnosa;
DROP TABLE IF EXISTS sesi_diagnosa;
DROP TABLE IF EXISTS riwayat_diagnosa;
DROP TABLE IF EXISTS aturan;
DROP TABLE IF EXISTS solusi;
DROP TABLE IF EXISTS gejala;
DROP TABLE IF EXISTS penyakit;
DROP TABLE IF EXISTS admin;

CREATE TABLE admin (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_sha CHAR(64) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE penyakit (
  kode VARCHAR(3) PRIMARY KEY,
  nama VARCHAR(120) NOT NULL,
  pengertian TEXT NULL,
  penyebab TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed admin default
-- username: admin
-- password: admin123
INSERT INTO admin (username, password_sha) VALUES
('admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9');

CREATE TABLE gejala (
  kode VARCHAR(5) PRIMARY KEY,
	nama VARCHAR(255) NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE aturan (
  id INT AUTO_INCREMENT PRIMARY KEY,
  kode_penyakit VARCHAR(3) NOT NULL,
  kode_gejala VARCHAR(5) NOT NULL,
  urutan INT NOT NULL DEFAULT 0,
  CONSTRAINT fk_aturan_penyakit FOREIGN KEY (kode_penyakit) REFERENCES penyakit(kode) ON DELETE CASCADE,
  CONSTRAINT fk_aturan_gejala FOREIGN KEY (kode_gejala) REFERENCES gejala(kode) ON DELETE CASCADE,
  UNIQUE KEY uq_aturan (kode_penyakit, kode_gejala)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE solusi (
  kode VARCHAR(3) PRIMARY KEY,     -- S01, S02, ...
  kode_penyakit VARCHAR(3) NOT NULL,
  deskripsi TEXT NOT NULL,
  urutan INT NOT NULL DEFAULT 0,
  CONSTRAINT fk_solusi_penyakit FOREIGN KEY (kode_penyakit) REFERENCES penyakit(kode) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE sesi_diagnosa (
  id CHAR(36) PRIMARY KEY,
  nama VARCHAR(120) NOT NULL,
  umur INT NOT NULL,
  jk VARCHAR(20) NOT NULL,
  alamat TEXT NOT NULL,
  kode_penyakit VARCHAR(3) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'aktif', -- aktif|selesai|tidak_terpenuhi
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_sesi_penyakit FOREIGN KEY (kode_penyakit) REFERENCES penyakit(kode) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE jawaban_diagnosa (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sesi_id CHAR(36) NOT NULL,
  kode_gejala VARCHAR(5) NOT NULL,
  jawaban TINYINT(1) NOT NULL,
  ditanya_pada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_jawab_sesi FOREIGN KEY (sesi_id) REFERENCES sesi_diagnosa(id) ON DELETE CASCADE,
  CONSTRAINT fk_jawab_gejala FOREIGN KEY (kode_gejala) REFERENCES gejala(kode) ON DELETE CASCADE,
  UNIQUE KEY uq_sesi_gejala (sesi_id, kode_gejala)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE riwayat_diagnosa (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sesi_id CHAR(36) NOT NULL,
  nama VARCHAR(120) NOT NULL,
  umur INT NOT NULL,
  jk VARCHAR(20) NOT NULL,
  alamat TEXT NOT NULL,
  status VARCHAR(20) NOT NULL, -- selesai|tidak_terpenuhi
  kode_penyakit VARCHAR(3) NOT NULL,
  nama_penyakit VARCHAR(120) NOT NULL,
  pesan TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed penyakit (P01-P05)
INSERT INTO penyakit (kode, nama, pengertian, penyebab) VALUES
('P01','Insomnia','Gangguan tidur yang ditandai dengan kesulitan untuk memulai tidur, mempertahankan tidur, atau bangun terlalu awal.','Stres, kecemasan, pola tidur buruk'),
('P02','Sleep Apnea','Gangguan di mana saluran napas tersumbat sebagian atau seluruhnya selama tidur (henti napas).','Obstruksi saluran nafas, obesitas'),
('P03','Narcolepsy','Rasa kantuk berlebihan di siang hari dan serangan tidur mendadak.','Ketidakseimbangan neurokimia'),
('P04','Restless Leg Syndrome','Sensasi tidak nyaman pada kaki saat akan tidur yang membuat sulit tidur.','Genetis, kekurangan zat besi'),
('P05','Gangguan Tidur akibat Stres','Kesulitan tidur akibat tekanan psikologis, biasanya akibat stres akademis.','Tekanan psikologis/kecemasan');

-- Seed gejala (G-01..G-24)
INSERT INTO gejala (kode, nama) VALUES
('G-01','Sulit untuk tidur atau sering terbangun di malam hari'),
('G-02','Merasa kelelahan atau kurang energi di siang hari'),
('G-03','Sulit tidur di malam hari meskipun sangat lelah'),
('G-04','Terbangun dengan detak jantung yang cepat atau rasa cemas'),
('G-05','Tidak merasa segar meskipun telah tidur cukup lama'),
('G-06','Mendengkur keras atau sesak nafas saat tidur'),
('G-07','Merasa nafas tersengal-sengal saat bangun tidur'),
('G-08','Terbangun dengan rasa tersedak atau sesak nafas'),
('G-09','Mendengkur keras dengan jeda nafas panjang'),
('G-10','Merasa kantuk berlebihan di siang hari meskipun cukup tidur'),
('G-11','Tertidur mendadak tanpa disadari di siang hari'),
('G-12','Kesulitan untuk tetap terjaga saat melakukan aktivitas'),
('G-13','Mengalami gangguan penglihatan saat merasa kantuk'),
('G-14','Kelumpuhan tidur (tidak bisa bergerak saat bangun atau sebelum tidur)'),
('G-15','Mengalami sensasi tidak nyaman pada kaki saat tidur'),
('G-16','Merasa kesemutan atau ada dorongan untuk menggerakkan kaki saat tidur'),
('G-17','Sering merasa kaki pegal atau berat di malam hari'),
('G-18','Sering meregangkan kaki secara tidak sadar saat tidur'),
('G-19','Mengalami gangguan tidur karena kaki yang sering bergerak'),
('G-20','Sulit berkonsentrasi atau fokus di siang hari'),
('G-21','Mengalami perubahan suasana hati yang ekstrem di siang hari'),
('G-22','Sering merasa marah atau mudah tersinggung di siang hari'),
('G-23','Terbangun tiba-tiba dengan rasa cemas'),
('G-24','Merasa sulit tidur meskipun kondisi lingkungan mendukung');

-- Seed aturan (IF gejala THEN penyakit)
INSERT INTO aturan (kode_penyakit, kode_gejala, urutan) VALUES
('P01','G-01',1),('P01','G-02',2),('P01','G-03',3),('P01','G-04',4),('P01','G-05',5),
('P02','G-01',1),('P02','G-10',2),('P02','G-06',3),('P02','G-07',4),('P02','G-08',5),('P02','G-09',6),
('P03','G-01',1),('P03','G-10',2),('P03','G-11',3),('P03','G-12',4),('P03','G-13',5),('P03','G-14',6),
('P04','G-15',1),('P04','G-16',2),('P04','G-17',3),('P04','G-18',4),('P04','G-19',5),
('P05','G-20',1),('P05','G-21',2),('P05','G-22',3),('P05','G-23',4),('P05','G-24',5);

-- Seed solusi (S01-S21)
INSERT INTO solusi (kode, kode_penyakit, deskripsi, urutan) VALUES
('S01','P01','CBT-I (Terapi Perilaku Kognitif untuk Insomnia) untuk mengubah pola pikir & kebiasaan tidur',1),
('S02','P01','Obat tidur jangka pendek sesuai resep dokter (mis. zolpidem/eszopiclone)',2),
('S03','P01','Melatonin (terutama untuk gangguan ritme sirkadian)',3),
('S04','P01','Sleep hygiene: jadwal tidur konsisten, kamar gelap, kurangi noise',4),

('S05','P02','CPAP: alat bantu napas bertekanan untuk menjaga jalan napas tetap terbuka',1),
('S06','P02','Pembedahan (kasus tertentu) untuk memperlebar/menstabilkan jalan napas',2),
('S07','P02','MAD (Mandibular Advancement Device) untuk memajukan rahang bawah',3),
('S08','P02','Latihan otot pernapasan dan pengelolaan berat badan bila diperlukan',4),

('S09','P03','Stimulant (mis. modafinil) untuk mengurangi kantuk berlebihan di siang hari',1),
('S10','P03','Sodium oxybate (sesuai dokter) untuk meningkatkan kualitas tidur malam',2),
('S11','P03','Tidur siang terjadwal untuk membantu mengontrol kantuk',3),
('S12','P03','Terapi perilaku dan manajemen stres',4),

('S13','P04','Obat dopaminergik (mis. pramipexole/ropinirole) sesuai anjuran dokter',1),
('S14','P04','Suplemen zat besi bila terkait defisiensi zat besi',2),
('S15','P04','Antikonvulsan (mis. gabapentin/pregabalin) untuk meredakan gejala',3),
('S16','P04','Kompres hangat/dingin dan peregangan ringan sebelum tidur',4),

('S17','P05','CBT-I/CBT untuk mengelola stres dan pikiran yang mengganggu tidur',1),
('S18','P05','Kebersihan tidur: batasi kafein, kurangi layar sebelum tidur, rutinitas relaksasi',2),
('S19','P05','Terapi kecemasan/depresi (mis. SSRI) sesuai evaluasi tenaga kesehatan',3),
('S20','P05','Obat penenang ringan dosis rendah (mis. doxepin) sesuai dokter, hindari ketergantungan',4),
('S21','P05','Relaksasi/meditasi: pernapasan dalam atau mindfulness',5);
