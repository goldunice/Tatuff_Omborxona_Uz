# Tatuff_Omborxona_Uz

Tatuff_Omborxona_Uz - bu oson, samarali va zamonaviy omborxona boshqaruvi tizimi. Ushbu loyiha mahsulotlarning kirim-chiqimini boshqarish, qoldiqni hisoblash, va mahsulot balansi tarixini kuzatish imkoniyatini beradi. Django asosida ishlab chiqilgan loyiha ombor faoliyatlarini avtomatlashtirish va boshqarishni soddalashtirish uchun yaratilgan.

---

## 🚀 Xususiyatlar

- **Mahsulot boshqaruvi:** Ombordagi barcha mahsulotlarni kuzatish.
- **Kirim-chiqim boshqaruvi:** Mahsulotlar harakatini (kirdi/chiqdi) nazorat qilish.
- **Balans kuzatuvi:** Har bir mahsulotning qoldiq miqdorini real vaqtda hisoblash.
- **Tarix va hisobotlar:** Kirim-chiqim tarixini PDF yoki Excel fayllari ko'rinishida yuklab olish.
- **Rolga asoslangan kirish:** Foydalanuvchilarni rollariga qarab kirish huquqlari bilan boshqarish.
- **Rangli interfeys:** Kirim va chiqim turlari uchun rangli indikatorlar (masalan, yashil va qizil ranglar).

---

## 🛠 Texnologiyalar

- **Backend:** Django, Python
- **Frontend:** Django Templates, HTML, CSS
- **Database:** PostgreSQL
- **Hisobotlar:** xlsxwriter, ReportLab
- **Autentifikatsiya:** Django OTP (Ikki faktorli autentifikatsiya)
- **Filtrlar:** Django RangeFilter

---

## 📂 Tizim tuzilishi

- **Mahsulotlar:**
  - Omborda saqlanayotgan barcha mahsulotlar.
- **Mahsulot balansi:**
  - Har bir mahsulotning mavjud miqdori va qoldiq holati.
- **Kirim-chiqim:**
  - Mahsulotning kirishi yoki chiqishini boshqarish.
- **Tarix:**
  - Mahsulotlar bo'yicha barcha amaliyotlar tarixi.
- **O'lchov birliklari:**
  - Mahsulotlar o'lchov birliklarini boshqarish (masalan, kg, dona).

---

## 🔧 O'rnatish

1. **Loyihani yuklab oling:**
   ```bash
   git clone https://github.com/username/Tatuff_Omborxona_Uz.git
   cd Tatuff_Omborxona_Uz
   ```

2. **Virtual muhitni yaratish va faollashtirish:**
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. **Talablarni o'rnating:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ma'lumotlar bazasini sozlash:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Superuser yaratish:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Serverni ishga tushirish:**
   ```bash
   python manage.py runserver
   ```

7. **Admin panelga kirish:**
   Brauzerda `http://127.0.0.1:8000/admin/` manzilini oching.

---

## 🎨 Foydalanuvchi interfeysi

Tatuff_Omborxona_Uz oddiy va qulay interfeysga ega bo'lib, quyidagilarni ta'minlaydi:

- Kirim va chiqim amaliyotlarini oson boshqarish.
- Sanalarga asoslangan qidiruv va filtrlar.
- Rangli indikatorlar bilan foydalanuvchiga tushunarli ma'lumot taqdim etish.

---

## 📊 Hisobotlar

- **PDF Hisobot:** Kirim-chiqim yoki mahsulot tarixi bo'yicha ma'lumotni PDF fayl sifatida yuklab olish imkoniyati.
- **Excel Hisobot:** Excel faylida statistik ma'lumotlarni saqlash va ulardan foydalanish.

---

## 📄 License

Bu loyiha [MIT License](LICENSE) ostida taqdim etiladi.

---

## 🤝 Hissa qo'shish

Hissa qo'shishni istaysizmi? Quyidagi qadamlarni bajaring:

1. Ushbu repozitoriyani fork qiling.
2. O'zingizning o'zgartirishlaringizni kiriting.
3. O'zgartirishlaringizni pull request sifatida yuboring.

---

## 👨‍💻 Loyihaning muallifi

**Tatuff Team**  
Biz haqimizda ko'proq ma'lumot uchun bog'laning: example@email.com

---

## 🌟 Ko'mak va fikr-mulohazalar

Agar muammoga duch kelsangiz yoki fikr-mulohazalaringiz bo'lsa, [Issues](https://github.com/username/Tatuff_Omborxona_Uz/issues) bo'limiga yozishingiz mumkin.

