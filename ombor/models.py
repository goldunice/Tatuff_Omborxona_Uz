import re

from django import forms
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


# === Foydalanuvchi Modeli ===
# Bu model foydalanuvchi uchun rasm o'rnatish uchun kerak
class CustomUser(AbstractUser):
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
        verbose_name='Foydalanuvchi rasmi'
    )

    def __str__(self):
        return self.username


# === O'lchov birligi Modeli ===
class OlchovBirligi(models.Model):
    olchov_birligi = models.CharField(max_length=255, unique=True, verbose_name="O'lchov birligi")

    class Meta:
        verbose_name = "O'lchov Birlig"
        verbose_name_plural = "O'lchov Birliglar"

    def clean(self):
        # O'lchov birligidagi ortiqcha bo'shliqlarni olib tashlash
        if self.olchov_birligi:
            self.olchov_birligi = re.sub(r'\s+', ' ', self.olchov_birligi.strip())

        # O'lchov birligi faqat harf, raqam, bo'shliq va bir tirnoqdan iboratligini tekshirish
        if not re.fullmatch(r"^[a-zA-Zа-яА-ЯёЁ0-9\s']+$", self.olchov_birligi):
            raise ValidationError(
                "O'lchov birligi faqat harflar, raqamlar, bo'shliqlar va bir tirnoqdan iborat bo'lishi kerak! Maxsus belgilar kiritish mumkin emas."
            )

        # O'lchov birligini unikal ekanligini tekshirish
        if OlchovBirligi.objects.filter(olchov_birligi__iexact=self.olchov_birligi).exclude(pk=self.pk).exists():
            raise ValidationError(f"'{self.olchov_birligi}' nomli o'lchov birligi bazada allaqachon mavjud!")

    def save(self, *args, **kwargs):
        # O'lchov birligini formatlash: bosh harf faqat so'zlarning boshida bo'lishi kerak
        if self.olchov_birligi:
            def format_word(word):
                if word.startswith("'"):
                    # Agar so'z bir tirnoq bilan boshlangan bo'lsa, faqat tirnoqdan keyingi qismni katta harf bilan formatlash
                    return "'" + word[1:].capitalize()
                else:
                    # Oddiy so'zlarni bosh harfni katta qilish
                    return word.capitalize()

            self.olchov_birligi = ' '.join(map(format_word, self.olchov_birligi.split(' ')))
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.olchov_birligi


# === Mahsulot Modeli ===
class Mahsulot(models.Model):
    mahsulot_nomi = models.CharField(max_length=255, unique=True, verbose_name="Mahsulot nomi")
    olchov_birligi = models.ForeignKey('OlchovBirligi', on_delete=models.PROTECT, blank=False, null=False,
                                       verbose_name="O'lchov birligi")

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def clean(self):
        # Mahsulot nomidagi ortiqcha bo'shliqlarni olib tashlash
        if self.mahsulot_nomi:
            self.mahsulot_nomi = re.sub(r'\s+', ' ', self.mahsulot_nomi.strip())

        # Mahsulot nomi faqat harf, raqam, bo'shliq va bir tirnoqdan iboratligini tekshirish
        if not re.fullmatch(r"^[a-zA-Zа-яА-ЯёЁ0-9\s']+$", self.mahsulot_nomi):
            raise ValidationError(
                "Mahsulot nomi faqat harflar, raqamlar, bo'shliqlar va bir tirnoqdan iborat bo'lishi kerak! Maxsus belgilar kiritish mumkin emas."
            )

        # Mahsulot nomining unikal ekanligini tekshirish
        if Mahsulot.objects.filter(mahsulot_nomi__iexact=self.mahsulot_nomi).exclude(pk=self.pk).exists():
            raise ValidationError(f"'{self.mahsulot_nomi}' nomli mahsulot bazada allaqachon mavjud!")

        # Mahsulot o'lchov birligi kiritilganligini tekshirish
        if not self.olchov_birligi:
            raise ValidationError("Mahsulot uchun o'lchov birligi kiritilishi shart!")

        # Mahsulot nomi va o'lchov birligi kombinatsiyasining unikal ekanligini tekshirish
        if Mahsulot.objects.filter(
                mahsulot_nomi=self.mahsulot_nomi, olchov_birligi=self.olchov_birligi
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                f"{self.mahsulot_nomi} mahsuloti uchun {self.olchov_birligi} o'lchov birligi allaqachon mavjud!"
            )

    def save(self, *args, **kwargs):
        # Mahsulot nomini formatlash: so'zlarning bosh harfi katta
        if self.mahsulot_nomi:
            def format_word(word):
                if word.startswith("'"):
                    # Agar so'z bir tirnoq bilan boshlangan bo'lsa, faqat tirnoqdan keyingi qismni katta harf bilan formatlash
                    return "'" + word[1:].capitalize()
                else:
                    # Oddiy so'zlarni bosh harfni katta qilish
                    return word.capitalize()

            self.mahsulot_nomi = ' '.join(map(format_word, self.mahsulot_nomi.split(' ')))
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.mahsulot_nomi


# === Mahsulot Balans Modeli ===
# Bu model mahsulotning ombordagi qolgan miqdorini saqlash uchun ishlatiladi.
class MahsulotBalans(models.Model):
    mahsulot_nomi = models.ForeignKey(Mahsulot, on_delete=models.PROTECT,
                                      verbose_name="Mahsulot nomi")  # Mahsulotga bog'langan
    qoldiq = models.PositiveIntegerField(default=0, verbose_name="Qoldiq")  # Ombordagi qolgan mahsulot miqdori

    class Meta:
        verbose_name = "Mahsulot Joriy Balansi"
        verbose_name_plural = "Mahsulot Joriy Balansi"

    def __str__(self):
        return f"{self.mahsulot_nomi} {self.qoldiq}"  # Admin panelda mahsulot va miqdorini ko'rsatadi


# === Mahsulot Balans Tarix Modeli ===
# Bu model mahsulot balansi tarixini saqlash uchun ishlatiladi.
class MahsulotBalansTarix(models.Model):
    mahsulot_nomi = models.ForeignKey(Mahsulot, on_delete=models.PROTECT,
                                      verbose_name="Mahsulot nomi")  # Mahsulotga bog'langan
    miqdor = models.PositiveIntegerField(verbose_name="Miqdor")  # Mahsulot miqdori
    qoldiq = models.PositiveIntegerField(verbose_name="Qoldiq")  # Qolgan mahsulot miqdori
    sana = models.DateTimeField(verbose_name="Sana")  # O'zgarish sanasi
    amaliyot_turi = models.CharField(max_length=5,
                                     verbose_name="Amaliyot turi")  # Operatsiya turi ("Kirdi" yoki "Chiqdi")

    kimga = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Kimga"
    )
    qayerga = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Qayerga"
    )

    class Meta:
        verbose_name = "Mahsulot Balans Tarixi"
        verbose_name_plural = "Mahsulot Balans Tarixi"

    def save(self, *args, **kwargs):
        # Asl save metodini chaqirish
        super().save(*args, **kwargs)

        # MahsulotBalans modelini yangilash
        if self.mahsulot_nomi:
            # Mahsulot uchun MahsulotBalans ma'lumotini olish yoki yaratish
            mahsulot_balans, yaratilgan = MahsulotBalans.objects.get_or_create(
                mahsulot_nomi=self.mahsulot_nomi,
                defaults={'qoldiq': self.qoldiq}
            )
            # Oxirgi qolgan miqdorni yangilash
            mahsulot_balans.qoldiq = self.qoldiq
            mahsulot_balans.save()

    def __str__(self):
        return f"{self.mahsulot_nomi} {self.miqdor} {self.qoldiq}  {self.sana} {self.amaliyot_turi}"


class KirdiChiqdi(models.Model):
    # Kirim va chiqim turini belgilash
    Kirdi_Chiqdi = (
        ("Kirdi", "Kirdi"),  # Kirim
        ("Chiqdi", "Chiqdi")  # Chiqim
    )
    mahsulot_nomi = models.ForeignKey(Mahsulot, on_delete=models.PROTECT, default=1,
                                      verbose_name="Mahsulot nomi")  # Mahsulotga bog'langan
    miqdor = models.PositiveIntegerField(default=0, verbose_name="Miqdor")  # Mahsulot miqdori
    sana = models.DateTimeField(auto_now_add=True, verbose_name="Sana")  # Operatsiya sanasi
    amaliyot_turi = models.CharField(max_length=15, choices=Kirdi_Chiqdi,
                                     verbose_name="Amaliyot turi")  # Operatsiya turi ("Kirdi" yoki "Chiqdi")
    kimga = models.CharField(
        max_length=255,
        blank=True,  # "Chiqdi" uchun kerak bo'lgani uchun model darajasida majburiy emas
        null=True,
        verbose_name="Kimga"
    )
    qayerga = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Qayerga"
    )

    class Meta:
        verbose_name = "Kirdi Chiqdi"
        verbose_name_plural = "Kirdi Chiqdi"

    def clean(self):
        # Ortiqcha bo'shliqlarni olib tashlash va tekshiruvlar
        if self.kimga:
            self.kimga = re.sub(r'\s+', ' ', self.kimga.strip()).title()
            if not re.fullmatch(r"^[a-zA-Zа-яА-ЯёЁ\s']+$", self.kimga):
                raise ValidationError({"kimga": "Kimga maydoni faqat harflar va bo'shliqlardan iborat bo'lishi kerak!"})

        if self.qayerga:
            self.qayerga = re.sub(r'\s+', ' ', self.qayerga.strip()).upper()
            if not re.fullmatch(r"^[a-zA-Zа-яА-ЯёЁ\s0-9]+$", self.qayerga):
                raise ValidationError(
                    {"qayerga": "Qayerga maydoni faqat harflar, raqamlar va bo'shliqlardan iborat bo'lishi kerak!"})

        # "Chiqdi" amaliyoti uchun majburiy tekshiruvlar
        if self.amaliyot_turi == "Chiqdi":
            if not self.kimga:
                raise ValidationError({"kimga": "Chiqdi operatsiyasi uchun 'Kimga' maydoni kiritilishi shart!"})
            if not self.qayerga:
                raise ValidationError({"qayerga": "Chiqdi operatsiyasi uchun 'Qayerga' maydoni kiritilishi shart!"})

        # Ombordagi balansni tekshirish
        if self.amaliyot_turi == "Chiqdi":
            mahsulot_balans = MahsulotBalans.objects.filter(mahsulot_nomi=self.mahsulot_nomi).first()
            if not mahsulot_balans:
                raise ValidationError("Bu mahsulot omborda mavjud emas!")
            if self.miqdor > mahsulot_balans.qoldiq:
                raise ValidationError("Omborda yetarli mahsulot mavjud emas!")

    def save(self, *args, **kwargs):
        # Avval clean() chaqiriladi
        self.clean()
        super().save(*args, **kwargs)
        # MahsulotBalansTarix uchun yozuv qo'shish yoki yangilash
        if self.mahsulot_nomi:
            mahsulot_tarix = MahsulotBalansTarix.objects.filter(mahsulot_nomi=self.mahsulot_nomi).last()

            if mahsulot_tarix is None:
                # Mahsulot uchun tarix mavjud bo'lmasa, yangi yozuv yaratish
                MahsulotBalansTarix.objects.create(
                    mahsulot_nomi=self.mahsulot_nomi,
                    miqdor=self.miqdor,
                    qoldiq=self.miqdor,
                    sana=self.sana,
                    amaliyot_turi="Kirdi" if self.amaliyot_turi == "Kirdi" else "Chiqdi",
                    kimga=self.kimga,
                    qayerga=self.qayerga
                )
            else:
                # Ombor balansini yangilash
                if self.amaliyot_turi == "Kirdi":
                    yangi_qoldiq = mahsulot_tarix.qoldiq + self.miqdor
                elif self.amaliyot_turi == "Chiqdi":
                    yangi_qoldiq = mahsulot_tarix.qoldiq - self.miqdor
                    if yangi_qoldiq < 0:
                        raise ValidationError("Omborda mahsulot yetarli emas.")

                # Yangi tarix yozuvini qo'shish
                MahsulotBalansTarix.objects.create(
                    mahsulot_nomi=self.mahsulot_nomi,
                    miqdor=self.miqdor,
                    qoldiq=yangi_qoldiq,
                    sana=self.sana,
                    amaliyot_turi="Kirdi" if self.amaliyot_turi == "Kirdi" else "Chiqdi",
                    kimga=self.kimga,
                    qayerga=self.qayerga
                )

    def __str__(self):
        return f"{self.mahsulot_nomi} {self.miqdor} {self.sana} {self.amaliyot_turi}"


class KirdiChiqdiForm(forms.ModelForm):
    class Meta:
        model = KirdiChiqdi
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        amaliyot_turi = cleaned_data.get("amaliyot_turi")
        kimga = cleaned_data.get("kimga")
        qayerga = cleaned_data.get("qayerga")

        # "Chiqdi" amaliyoti uchun qo'shimcha maydonlar
        if amaliyot_turi == "Chiqdi":
            if not kimga:
                self.add_error("kimga", "Chiqdi operatsiyasi uchun 'Kimga' maydoni kiritilishi shart!")
            if not qayerga:
                self.add_error("qayerga", "Chiqdi operatsiyasi uchun 'Qayerga' maydoni kiritilishi shart!")

        return cleaned_data
