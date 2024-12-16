# Tatuff_Omborxona_Uz - Django Warehouse Management System

Tatuff_Omborxona_Uz — bu Django asosida ishlab chiqilgan omborxona boshqaruvi tizimi. Ushbu tizim mahsulotlarni boshqarish, balanslarni kuzatish va mahsulot tranzaksiyalarini qayd etish uchun mo'ljallangan. Loyihada foydalanuvchilarga mahsulotlar balansini yangilash, mahsulotlar tarixini kuzatish va ma'lumotlar bazasiga kirish imkoniyatlari taqdim etiladi.

## Asosiy Xususiyatlar

1. **Mahsulotlarni boshqarish**:
   - Mahsulot qo'shish, o'zgartirish va o'chirish imkoniyatlari.
   - Mahsulotlar haqida batafsil ma'lumotlarni ko'rish.
   
2. **Mahsulot Balansini Kuzatish**:
   - Har bir mahsulot uchun mavjud balansni ko'rish va yangilash.
   - Mahsulotlar bo'yicha qoldiq miqdorini ko'rsatish.

3. **Tranzaksiya Tarixi**:
   - Mahsulotlar bilan bog'liq tranzaksiyalarni kuzatish.
   - Tranzaksiya turini (kiritish yoki chiqarish) va sanasini ko'rsatish.

4. **Admin Paneli**:
   - Django admin paneli orqali tizimni boshqarish.
   - Mahsulotlar va tranzaksiyalarni admin panelidan qulay tarzda boshqarish.

5. **Xavfsizlik**:
   - Foydalanuvchi autentifikatsiyasi va ruxsatnoma tizimi.
   - Admin panelga faqat ishonchli foydalanuvchilar kirishi mumkin.

## O'rnatish

Tizimni o'rnatish uchun quyidagi qadamlarni bajaring:

### 1. Repozitoriyani klonlash
Loyihani GitHub-dan klonlab oling:
```bash
git clone https://github.com/username/Tatuff_Omborxona.git
cd Tatuff_Omborxona
