pertanyaan pertama:
saya melampirkan file sistem dan file laporan skripsi saya analisis keduanya.
saya bertanya:
1. pada subbab 3.5.4 skenario eksperimen apakah sudah betul? jika salah bagaimana yang betul? dan jika salah apakah sistem saya juga salah pada bagian tersebut?
2. pada subbab 4.3.1 hasil pencarian k optimal, apakah sudah betul struktur tabel nya? dan apakah seharusnya saya melampirkan perplexity di tabel tersebut? jika salah bagaimana yang betul? dan jika salah apakah sistem saya juga salah?
3. pada subbab 4.6.3 Ringkasan Perbandingan LDA dan NMF, apakah sudah struktur tabel nya begitu? dan apakah seharusnya saya mencampur semuanya jadi 1 tabel begitu? karena kalo dari saya sendiri mending di bikin tabel indikator utama dan tabel indikator tambahan tapi jika anda punya saran lain juga tidak apa apa.
4. kesalahan utama nya apakah karena saya memaksakan log-perplexity sebagai pengukuran utama lda dan nmf akhirnya semua berantakan?
5. sebetulnya apa sih pengukuran utama saya? dan apakah saya konsistem pada konsep pengukuran tersebut? jika tidak konsisten saya harus ubah di bagian mana saja?

jawaban pertanyaan pertama:
Let's look at cell 18 (K optimal search) and cell 24 (evaluation & comparison) in full, since these directly relate to the perplexity/NMF computation.Saya sudah baca kedua file (skripsi + notebook). Sebelum masuk ke jawaban satu-satu, ini temuan kunci yang mendasari hampir semua masalah di 5 pertanyaan Anda: **notebook Anda (sel 18, 22, 24, 34) benar-benar menghitung "Log-Perplexity NMF"** — sebuah metrik buatan (`-log(reconstruction_error/n_elemen)`) yang diberi nama seolah setara dengan Perplexity LDA, padahal NMF bukan model probabilistik dan secara matematis **tidak punya perplexity**. Ini akar dari semua inkonsistensi di bawah.

## 1. Subbab 3.5.4 — Skenario Eksperimen

**Narasi teksnya sudah benar**: "*khusus pada metode LDA juga dihitung nilai Perplexity (PP)*" — ini tepat, karena PP memang cuma valid untuk model probabilistik seperti LDA.

**Tapi Tabel 3.7 kontradiksi dengan narasi itu sendiri.** Kolom "Parameter Evaluasi" untuk baris NMF (baris 3 & 4) tetap mencantumkan "Perplexity (PP)" — padahal kalimat tepat di atasnya bilang PP itu "khusus LDA". Jadi tabel dan paragraf saling bertentangan dalam dokumen yang sama.

**Apakah sistem Anda juga salah di bagian ini? Ya.** Sel 18 dan 22 di notebook memang menghitung `nmf_logperp_k` / `log_perplexity_nmf` — jadi sistem konsisten dengan tabel yang salah, bukan dengan narasi yang benar.

**Perbaikan:** Baris NMF di Tabel 3.7 seharusnya hanya berisi *Topic Coherence (Cv), waktu komputasi, interpretabilitas topik* — tanpa PP. Kalau ingin tetap melaporkan sesuatu tentang kualitas rekonstruksi NMF, sebut eksplisit "Reconstruction Error (Frobenius norm)", bukan "Perplexity (PP)".

## 2. Subbab 4.3.1 — Tabel 4.6 (K optimal)

Ada dua masalah:

**a) Judul tabel tidak cocok isinya.** Judul "*Nilai Topic Coherence NMF dan Perplexity LDA (PP)*" hanya menyebut coherence-NMF dan perplexity-LDA, padahal isi tabel punya 4 kolom data (Cv LDA, Cv NMF, Log-Perplexity LDA, Log-Perplexity NMF).

**b) Kolom "Log-Perplexity NMF" seharusnya tidak ada di tabel ini**, dengan alasan yang sama seperti poin 1: itu bukan perplexity dalam pengertian yang valid, dan meletakkannya sejajar dengan kolom LDA membuat pembaca (termasuk penguji) mengira kedua nilai itu bisa dibandingkan langsung — padahal skalanya beda total (7,4–7,7 vs 13,27–13,31) justru karena rumusnya beda, bukan karena performanya beda.

**Apakah perlu melampirkan perplexity di tabel ini?** Ya — **untuk LDA saja**, itu sudah benar dan berguna sebagai metrik sekunder (indikasi generalisasi model). **Untuk NMF, tidak** — jangan dipaksakan.

**Struktur yang benar:**

| K | Cv (LDA) | Cv (NMF) | Log-Perplexity (LDA) | Keterangan |
|---|---|---|---|---|
| 2 | 0,4484 | 0,6971 | 7,7355 | – |
| ... | ... | ... | ... | ... |

Kalau reconstruction error NMF ingin ditampilkan juga, taruh di kolom/tabel terpisah dengan judul sendiri, dan jangan disebut "Log-Perplexity".

**Sistem Anda juga salah di bagian ini** — sel 18 menghasilkan `nmf_logperp_k` yang langsung dipakai untuk mengisi kolom itu dan untuk grafik 4.3.2 (yang bahkan dianalisis seolah ada tren bermakna: "*Log-Perplexity NMF relatif stabil pada rentang 13,2757–13,3062*" — padahal itu cuma efek samping rumus, bukan temuan substantif).

## 3. Subbab 4.6.3 — Tabel 4.13 (Ringkasan Perbandingan)

Struktur saat ini salah karena mencampur **tiga jenis informasi yang seharusnya dipisah**:
1. Metrik kuantitatif yang benar-benar comparable (Cv rata-rata, Cv per topik, waktu komputasi)
2. Metrik yang **secara eksplisit Anda sendiri nyatakan tidak comparable** (Perplexity, Log-Perplexity, Reconstruction Error — paragraf di bawah tabel bahkan bilang "*nilai tersebut tidak digunakan sebagai dasar utama perbandingan*")
3. Penilaian kualitatif/kesimpulan (ketajaman batas topik, unggul pada topik, rekomendasi akhir)

Menaruh baris yang Anda sendiri akui "tidak bisa dibandingkan langsung" di dalam tabel berjudul "Ringkasan Perbandingan" adalah kontradiksi langsung.

**Ide Anda (pisah jadi tabel indikator utama + tambahan) sudah tepat arah.** Saran konkret:

**Tabel A — Indikator Utama (kuantitatif, comparable):**
| Indikator | LDA | NMF |
|---|---|---|
| Rata-rata Coherence (Cv) | 0,4830 | 0,7645 |
| Coherence Topik Politik | 0,4430 | 0,6087 |
| Coherence Topik Olahraga | 0,5945 | 0,9130 |
| Coherence Topik Teknologi | 0,3663 | 0,9860 |
| Coherence Topik Ekonomi | 0,5284 | 0,5503 |
| Waktu Komputasi | 63,96 detik | 0,22 detik |

**Tabel B — Indikator Tambahan/Kualitatif:**
| Indikator | LDA | NMF |
|---|---|---|
| Ketajaman batas topik | Sedang | Tinggi |
| Unggul pada topik | 1 dari 4 | 3 dari 4 |
| Rekomendasi akhir | Cukup Baik | Terbaik |

**Perplexity/Log-Perplexity/Reconstruction Error → keluarkan dari kedua tabel ini.** Kalau ingin tetap dilaporkan, taruh sebagai catatan tambahan di subbab 4.4 (bagian hasil LDA saja) sebagai bukti pendukung fit model LDA — bukan sebagai baris "perbandingan" LDA vs NMF.

## 4. Apakah akar masalahnya karena memaksakan log-perplexity sebagai pengukuran utama?

Sedikit koreksi presisi di sini: **teks Anda sebenarnya sudah menyatakan Cv sebagai metrik utama** ("*kualitas topik lebih tepat dievaluasi menggunakan Topic Coherence (Cv)*" — ini benar). Jadi bukan log-perplexity yang dipakai sebagai metrik utama secara eksplisit.

**Masalah sebenarnya lebih spesifik:** Anda memaksakan agar NMF punya *padanan* metrik perplexity supaya tabelnya terlihat "simetris" dengan LDA — padahal metrik itu tidak valid untuk NMF. Begitu metrik buatan ini eksis (di kode maupun di tabel), ia otomatis muncul di tiga tempat (Tabel 3.7, 4.6, 4.13) berdampingan dengan Cv, sehingga:
- Pembaca melihat 2 "sistem penilaian" berjalan paralel (Cv dan PP) tanpa penjelasan mana yang benar-benar dipakai untuk kesimpulan.
- Anda sendiri harus menambahkan disclaimer berulang kali ("tidak dapat dibandingkan langsung") — tanda bahwa metrik ini seharusnya dari awal tidak ditaruh sejajar.
- Analisis naratif (4.3.2) jadi membahas tren pada angka yang sebenarnya tidak informatif.

Jadi ya, **hipotesis Anda benar secara substansi**: penyebab utama kekacauan adalah memaksakan eksistensi "Log-Perplexity NMF", bukan salah memilih metrik utama.

## 5. Apa pengukuran utama Anda, dan apakah konsisten?

**Pengukuran utama = Topic Coherence (Cv).** Ini didukung oleh:
- Pernyataan eksplisit di 4.6.3
- Cv adalah satu-satunya metrik yang benar-benar dihitung dengan formula yang sama & valid untuk kedua metode (LDA lewat `CoherenceModel(model=lda_k, ...)`, NMF lewat `CoherenceModel(topics=nmf_topics_k, ...)` — keduanya `c_v` dari gensim, jadi apple-to-apple).

**Konsistensi:** Secara keputusan akhir (NMF menang karena Cv lebih tinggi), Anda konsisten. Tapi ada 3 titik yang perlu diperbaiki agar konsisten menyeluruh:

1. **Tabel 3.7 (Bab 3):** baris NMF masih mencantumkan PP → hapus, sesuai poin 1.
2. **Tabel 4.6 & narasi 4.3.2 (Bab 4):** kolom/analisis "Log-Perplexity NMF" masih ada → hapus atau reposisi, sesuai poin 2.
3. **Pemilihan K = 4:** Anda memilih K=4 bukan karena puncak Cv (puncak Cv LDA di K=5, NMF di K=3), tapi karena kesesuaian dengan 4 kategori dataset. Ini keputusan yang wajar dan bisa dipertahankan (interpretability/domain-alignment di atas skor mentah adalah praktik umum), **tapi perlu kalimat penghubung eksplisit** di 4.3.1/4.3.2 semacam: "*meskipun K optimal berdasarkan Cv berbeda untuk LDA dan NMF, penelitian ini memprioritaskan keselarasan struktural dengan kategori dataset; Cv tetap menjadi metrik utama untuk seluruh evaluasi kualitas topik setelah K ditetapkan*" — supaya tidak terkesan Anda "lompat" dari klaim "Cv itu metrik utama" ke keputusan K yang tidak mengikuti Cv tanpa penjelasan.

**Ringkasan perbaikan (checklist):**
- [ ] Tabel 3.7: hapus "Perplexity (PP)" dari baris NMF
- [ ] Tabel 4.6: hapus kolom "Log-Perplexity NMF"; perbaiki judul tabel
- [ ] Narasi 4.3.2: hapus/reframe paragraf yang menganalisis tren Log-Perplexity NMF
- [ ] Tabel 4.13: pecah jadi Tabel Indikator Utama + Tabel Indikator Tambahan; keluarkan baris Perplexity/Log-Perplexity/Reconstruction Error dari keduanya
- [ ] Notebook sel 18, 22, 24, 34: hapus/relabel variabel `nmf_logperp_k`, `log_perplexity_nmf` — kalau reconstruction error tetap mau disimpan, beri nama variabel & print statement yang tidak menyebut "perplexity"
- [ ] Tambahkan 1-2 kalimat penghubung di 4.3.1 soal alasan K=4 vs Cv-optimal per metode

Kalau Anda mau, saya bisa langsung bantu edit XML dokumen Word (tabel + paragraf terkait) dan/atau revisi sel-sel notebook yang saya sebutkan di atas.