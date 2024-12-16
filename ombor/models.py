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
# Bu model miqdor turini saqlash uchun ishlatiladi.
class OlchovBirligi(models.Model):
    olchov_birligi = models.CharField(max_length=255, unique=True, verbose_name="O'lchov birligi")  # Miqdor turi

    class Meta:
        verbose_name = "O'lchov Birlig"
        verbose_name_plural = "O'lchov Birliglar"

    def clean(self):

        # O'lchov birligi faqat harflardan iboratligini tekshirish
        if not re.fullmatch(r"^[a-zA-Zа-яА-ЯёЁ']+$", self.olchov_birligi):
            raise ValidationError(
                "O'lchov birligi faqat harflardan iborat bo'lishi kerak! Maxsus belgilar yoki raqamlar kiritish mumkin emas.")

        # O'lchov birligini tekshirish: mavjudligini aniqlash
        if OlchovBirligi.objects.filter(olchov_birligi__iexact=self.olchov_birligi).exclude(pk=self.pk).exists():
            raise ValidationError(f"'{self.olchov_birligi}' nomli o'lchov birligi bazada allaqachon mavjud!")

    def save(self, *args, **kwargs):
        # Ma'lumotni formatlash: birinchi harf katta, qolganlari kichik
        if self.olchov_birligi:
            self.olchov_birligi = self.olchov_birligi.capitalize()
        # Avval clean() chaqiriladi, keyin saqlash amalga oshiriladi
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.olchov_birligi  # Admin panelda miqdor turi ko'rsatadi


# === Mahsulot Modeli ===
# Bu model mahsulot nomini saqlash uchun ishlatiladi.
class Mahsulot(models.Model):
    mahsulot_nomi = models.CharField(max_length=255, unique=True, verbose_name="Mahsulot nomi")  # Mahsulot nomi
    olchov_birligi = models.ForeignKey(OlchovBirligi, on_delete=models.PROTECT,
                                       verbose_name="O'lchov birligi")  # O'lchov birligi

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def clean(self):
        # Mahsulot nomi faqat harflardan iboratligini tekshirish
        if not re.fullmatch(r"^[a-zA-Zа-яА-ЯёЁ']+$", self.mahsulot_nomi):
            raise ValidationError(
                "Mahsulot nomi faqat harflardan iborat bo'lishi kerak! Maxsus belgilar yoki raqamlar kiritish mumkin emas.")

        # Mahsulot nomining unikal ekanligini tekshirish
        if Mahsulot.objects.filter(mahsulot_nomi__iexact=self.mahsulot_nomi).exclude(pk=self.pk).exists():
            raise ValidationError(f"'{self.mahsulot_nomi}' nomli mahsulot bazada allaqachon mavjud!")

        # Mahsulot o'lchov birligini tekshirish
        if Mahsulot.objects.filter(mahsulot_nomi=self.mahsulot_nomi, olchov_birligi=self.olchov_birligi).exists():
            raise ValidationError(
                f"{self.mahsulot_nomi} mahsuloti uchun {self.olchov_birligi} o'lchov birligi allaqachon mavjud!")

    def save(self, *args, **kwargs):
        # Mahsulot nomini formatlash: birinchi harf katta, qolganlari kichik
        if self.mahsulot_nomi:
            self.mahsulot_nomi = self.mahsulot_nomi.capitalize()
        # Avval clean() chaqiriladi, keyin saqlash amalga oshiriladi
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.mahsulot_nomi  # Admin panelda mahsulot nomini ko'rsatadi


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


# === Kirdi Chiqdi Modeli ===
# Bu model mahsulotlarning kirim va chiqim operatsiyalarini boshqarish uchun ishlatiladi.
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

    class Meta:
        verbose_name = "Kirdi Chiqdi"
        verbose_name_plural = "Kirdi Chiqdi"

    def save(self, *args, **kwargs):
        # Asl save metodini chaqirish
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
                    amaliyot_turi="Kirdi" if self.amaliyot_turi == "Kirdi" else "Chiqdi"
                )
            else:
                # Ombor balansini yangilash
                if self.amaliyot_turi == "Kirdi":
                    yangi_qoldiq = mahsulot_tarix.qoldiq + self.miqdor
                elif self.amaliyot_turi == "Chiqdi":
                    yangi_qoldiq = mahsulot_tarix.qoldiq - self.miqdor
                    if yangi_qoldiq < 0:  # Omborda mahsulot yetarli emas
                        raise ValidationError("Omborda mahsulot yetarli emas.")

                # Yangi tarix yozuvini qo'shish
                MahsulotBalansTarix.objects.create(
                    mahsulot_nomi=self.mahsulot_nomi,
                    miqdor=self.miqdor,
                    qoldiq=yangi_qoldiq,
                    sana=self.sana,
                    amaliyot_turi="Kirdi" if self.amaliyot_turi == "Kirdi" else "Chiqdi"
                )

    def __str__(self):
        return f"{self.mahsulot_nomi} {self.miqdor} {self.sana} {self.amaliyot_turi}"


# === Kirdi Chiqdi Form ===
class KirdiChiqdiForm(forms.ModelForm):
    class Meta:
        model = KirdiChiqdi
        fields = "__all__"  # Barcha maydonlarni formaga qo'shish

    def clean(self):
        cleaned_data = super().clean()
        mahsulot_nomi = cleaned_data.get("mahsulot_nomi")
        miqdor = cleaned_data.get("miqdor")
        amaliyot_turi = cleaned_data.get("amaliyot_turi")

        # 1. Har bir maydonning qiymati kiritilganligini tekshirish
        if not mahsulot_nomi:
            raise ValidationError({"mahsulot_nomi": "Mahsulot nomi kiritilishi shart!"})
        if miqdor is None or miqdor <= 0:
            raise ValidationError({"miqdor": "Mahsulot miqdori nol yoki manfiy bo'lishi mumkin emas!"})

        # 2. Ombordagi mahsulot balansini tekshirish
        if amaliyot_turi == "Chiqdi":
            mahsulot_balans = MahsulotBalans.objects.filter(mahsulot_nomi=mahsulot_nomi).first()
            if not mahsulot_balans:
                raise ValidationError({"mahsulot_nomi_id": "Bu mahsulot omborda mavjud emas!"})
            if miqdor > mahsulot_balans.qoldiq:
                raise ValidationError({"miqdor": "Omborda yetarli mahsulot mavjud emas!"})

        return cleaned_data
