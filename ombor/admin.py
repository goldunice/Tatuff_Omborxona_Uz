import xlsxwriter
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_otp.admin import OTPAdminSite
from rangefilter.filters import DateRangeQuickSelectListFilterBuilder
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from django.urls import reverse
from django.http import HttpResponse
from django.utils.timezone import localtime
from datetime import datetime
from .models import CustomUser
from .models import Mahsulot, MahsulotBalans, MahsulotBalansTarix, KirdiChiqdi, KirdiChiqdiForm, OlchovBirligi

admin.site.__class__ = OTPAdminSite


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('profile_image',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('profile_image',)}),
    )
    # Customizing list display to include image preview
    list_display = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active',
                    'profile_image_preview']
    list_display_links = ['id', 'username']

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width: 100px; height: 100px;" />', obj.profile_image.url)
        return "No Image"

    profile_image_preview.short_description = 'Profile Image'


def oylik_hisobot(modeladmin, request, queryset):
    model_name = modeladmin.model.__name__
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Oylik_hisobot_{model_name}.xlsx'

    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet("Hisobot")

    # Define formats
    header_format = workbook.add_format(
        {'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
    text_format = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
    number_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
    bold_center_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})

    # Get current month and year
    now = datetime.now()
    current_year = now.year
    current_month = now.strftime('%B')  # Oyni matn ko'rinishida olish (masalan, "Dekabr")

    # Write the title
    worksheet.merge_range('A1:D1',
                          f'TATU Farg‘ona filiali omboridan {current_year} yil {current_month.lower()} oyida berilgan mahsulotlar haqida',
                          bold_center_format)
    worksheet.merge_range('A2:D2', 'M A L U M O T', bold_center_format)

    # Write headers
    headers = ["T/R", "Berilgan mahsulotlar nomi", "O‘lchov birligi", "Miqdori"]
    for col_num, header in enumerate(headers):
        worksheet.write(3, col_num, header, header_format)

    # Adjust column widths
    worksheet.set_column(0, 0, 5)  # T/R
    worksheet.set_column(1, 1, 40)  # Mahsulot nomi
    worksheet.set_column(2, 2, 15)  # O‘lchov birligi
    worksheet.set_column(3, 3, 10)  # Miqdori

    # Write data rows
    for row_num, obj in enumerate(queryset, start=4):
        worksheet.write(row_num, 0, row_num - 3, text_format)  # T/R

        # Mahsulot nomini olish
        mahsulot_nomi = getattr(obj, 'mahsulot_nomi', None)
        if mahsulot_nomi:
            mahsulot_nomi = str(mahsulot_nomi)  # Mahsulot nomini to'g'ri formatlash
        else:
            mahsulot_nomi = 'Noma’lum'

        worksheet.write(row_num, 1, mahsulot_nomi, text_format)  # Mahsulot nomi

        # O‘lchov birligini olish
        olchov_birligi = getattr(obj, 'get_olchov_birligi', None)
        if olchov_birligi:
            olchov_birligi_value = getattr(olchov_birligi, 'olchov_birligi',
                                           'Noma’lum')  # Ensure we access the correct field
        else:
            olchov_birligi_value = 'Noma’lum'

        worksheet.write(row_num, 2, olchov_birligi_value, text_format)  # O‘lchov birligi

        # Miqdorini olish
        miqdor = getattr(obj, 'miqdor', 'Noma’lum')
        worksheet.write(row_num, 3, miqdor, number_format)  # Miqdori

    workbook.close()
    return response


oylik_hisobot.short_description = "Oylik hisobotni Excel faylida yuklab olish"


def download_excel(modeladmin, request, queryset):
    model_name = modeladmin.model.__name__
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={model_name}.xlsx'
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Define formats
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
    kirdi_format = workbook.add_format({'font_color': 'green', 'bold': True})
    chiqdi_format = workbook.add_format({'font_color': 'red', 'bold': True})
    sana_format = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss', 'border': 1})  # Date format

    # Write headers
    headers = ["T/r"] + [field.verbose_name for field in modeladmin.model._meta.fields]
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header, header_format)

    # Auto-adjust column widths
    for col_num, field in enumerate(headers):
        if field == "T/r":
            max_len = 5  # "T/r" uchun qo'lda kenglikni belgilang
        else:
            max_len = max(
                [len(str(getattr(obj, field))) for obj in queryset if hasattr(obj, field)] + [len(field)]
            )
        worksheet.set_column(col_num, col_num, max_len + 2)

    # Write data rows
    for row_num, obj in enumerate(queryset, 1):
        worksheet.write(row_num, 0, row_num)
        for col_num, field in enumerate(modeladmin.model._meta.fields, 1):
            value = str(getattr(obj, field.name))

            # Vaqtni formatlash
            if isinstance(getattr(obj, field.name), datetime):
                value = localtime(getattr(obj, field.name)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                getattr(obj, field.name)

            # Amaliyot turiga rang kiritish
            if field.name == "amaliyot_turi":
                if value == "Kirdi":
                    worksheet.write(row_num, col_num, value, kirdi_format)
                elif value == "Chiqdi":
                    worksheet.write(row_num, col_num, value, chiqdi_format)
                else:
                    worksheet.write(row_num, col_num, value)
            else:
                worksheet.write(row_num, col_num, value)

    workbook.close()
    return response


download_excel.short_description = "Tanlangan maydonlarni Excel fayl sifatida yuklab olish"


def download_pdf(self, request, queryset):
    model_name = self.model.__name__
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={model_name}.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setTitle('PDF Report')

    ordered_queryset = queryset.order_by('-id')

    headers = ["T/r"] + [field.verbose_name for field in self.model._meta.fields]
    data = [headers]

    for index, obj in enumerate(ordered_queryset, 1):
        data_row = [index]
        data_row += [localtime(getattr(obj, field.name)).strftime('%Y-%m-%d %H:%M:%S')
                     if isinstance(getattr(obj, field.name), datetime) else getattr(obj, field.name)
                     for field in self.model._meta.fields]
        data.append(data_row)

    table = Table(data)
    style = TableStyle(
        [
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),  # Header background
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Table grid
        ]
    )

    # Add color formatting for "Kirdi" and "Chiqdi"
    for row_num, row_data in enumerate(data[1:], start=1):  # Skip header
        if "Kirdi" in row_data:
            style.add('TEXTCOLOR', (row_data.index("Kirdi"), row_num), (row_data.index("Kirdi"), row_num), colors.green)
        elif "Chiqdi" in row_data:
            style.add('TEXTCOLOR', (row_data.index("Chiqdi"), row_num), (row_data.index("Chiqdi"), row_num), colors.red)

    table.setStyle(style)

    canvas_width = 550
    canvas_height = 750
    table.wrapOn(pdf, canvas_width, canvas_height)
    table.drawOn(pdf, 20, canvas_height - (len(data) * 20))  # Adjust placement

    pdf.save()
    return response


download_pdf.short_description = 'Tanlangan maydonlarni PDF fayl sifatda yuklash'


# === O'lchov birligi Admin ===
# Bu bo'lim o'lchov birliklarini boshqarish uchun.
@admin.register(OlchovBirligi)
class OlchovBirligiAdmin(admin.ModelAdmin):
    list_display = ('id', 'olchov_birligi')  # O'lchov birligini ko'rsatish
    list_display_links = ('id', 'olchov_birligi')  # ID va nomga bosilganda ko'rsatilgan o'lchovga o'tish
    search_fields = ('olchov_birligi',)  # O'lchov birligi bo'yicha qidiruv
    ordering = ('-id',)  # O'lchov birligi ID bo'yicha tartibda ko'rsatish
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni


# === Custom Filter ===
class OlchovBirligiFilter(admin.SimpleListFilter):
    title = _('O‘lchov birligi')  # Admin paneldagi filter nomi
    parameter_name = 'olchov_birligi'

    def lookups(self, request, model_admin):
        """
        Filterda faqat `KirdiChiqdi` modelida mavjud o'lchov birliklari ko'rinadi.
        """
        # KirdiChiqdi modelida ishlatilgan o'lchov birliklarini oling
        olchov_birliklar = (
            KirdiChiqdi.objects.values_list('mahsulot_nomi__olchov_birligi__id',
                                            'mahsulot_nomi__olchov_birligi__olchov_birligi')
            .distinct()
        )
        return [(ob[0], ob[1]) for ob in olchov_birliklar]

    def queryset(self, request, queryset):
        """
        Foydalanuvchi filterni tanlaganda, mos yozuvlarni qaytaradi.
        """
        if self.value():
            return queryset.filter(mahsulot_nomi__olchov_birligi__id=self.value())
        return queryset


# === Mahsulot Admin ===
# Bu bo'lim mahsulotlarni admin panelida boshqarish uchun.
@admin.register(Mahsulot)
class MahsulotAdmin(admin.ModelAdmin):
    list_display = ('id', 'mahsulot_nomi', 'olchov_birligi')  # Admin panelda ko'rsatish uchun maydonlar
    list_display_links = ('id', 'mahsulot_nomi')  # Ushbu maydonlarga bosilsa, tegishli mahsulotga o'tadi
    search_fields = ('mahsulot_nomi',)  # Mahsulot nomi bo'yicha qidiruv imkoniyati
    ordering = ('-id',)  # Mahsulotlarni id bo'yicha tartibda ko'rsatish
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni


# === MahsulotBalans Admin ===
# Bu bo'lim mahsulot balansi (ombordagi miqdor)ni boshqarish uchun.
@admin.register(MahsulotBalans)
class MahsulotBalansAdmin(admin.ModelAdmin):
    list_display = ('id', 'mahsulot_nomi', 'get_olchov_birligi', 'qoldiq')  # Ko'rinadigan ustunlar
    list_display_links = ('id', 'mahsulot_nomi')  # Mahsulotga bosilganda uning balansi ko'rsatiladi
    search_fields = ('mahsulot_nomi__mahsulot_nomi',)  # Mahsulot nomi bo'yicha qidiruv
    list_filter = (OlchovBirligiFilter,)  # Custom filterni qo'shish
    ordering = ('-id',)  # ID bo'yicha tartib
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni
    actions = [oylik_hisobot,download_excel,
               download_pdf]  # Mahsulotning joriy balansi haqida malumot olish uchun fayl sifatida yuklab olish xizmati

    def get_olchov_birligi(self, obj):
        """Displays the 'olchov_birligi' of the related 'Mahsulot'."""
        return obj.mahsulot_nomi.olchov_birligi if obj.mahsulot_nomi else None

    get_olchov_birligi.short_description = "O'lchov Birligi"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "mahsulot_nomi__olchov_birligi":
            # Faqat `KirdiChiqdi` orqali kiritilgan `OlchovBirligi`larni ko'rsatish
            kwargs["queryset"] = OlchovBirligi.objects.filter(
                id__in=KirdiChiqdi.objects.values('mahsulot_nomi__olchov_birligi'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Foydalanuvchining o'zi mahsulot uchun balance ni o'zgartira olmasligi zarur
    def has_add_permission(self, request):
        return False  # Mahsulot balansi qo'shish huquqi yo'q


# === MahsulotBalansTarix Admin ===
# Bu bo'lim mahsulot balansi tarixini boshqarish uchun.
@admin.register(MahsulotBalansTarix)
class MahsulotBalansTarixAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'mahsulot_nomi', 'miqdor', 'get_olchov_birligi', 'qoldiq', 'sana',
        'colored_amaliyot_turi', 'kimga', 'qayerga')  # Ko'rinadigan ustunlar
    # search_fields = ("mahsulot_nomi__mahsulot_nomi",)
    list_filter = (("sana", DateRangeQuickSelectListFilterBuilder()),)
    date_hierarchy = 'sana'  # Sanalar bo'yicha navigatsiya
    ordering = ('-id',)  # Teskari tartibda ko'rsatish
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni
    actions = [download_excel, download_pdf,
               oylik_hisobot]  # Tarixni Excel fayl qilib yuklab olish xizmati

    def colored_amaliyot_turi(self, obj):
        """Amaliyot turini rangli qilib ko‘rsatadi."""
        if obj.amaliyot_turi == "Kirdi":
            return format_html('<span style="color: green;">{}</span>', obj.amaliyot_turi)
        elif obj.amaliyot_turi == "Chiqdi":
            return format_html('<span style="color: red;">{}</span>', obj.amaliyot_turi)
        return obj.amaliyot_turi

    colored_amaliyot_turi.short_description = "Amaliyot Turi"

    def get_olchov_birligi(self, obj):
        """Displays the 'olchov_birligi' of the related 'Mahsulot'."""
        return obj.mahsulot_nomi.olchov_birligi if obj.mahsulot_nomi else None

    get_olchov_birligi.short_description = "O'lchov Birligi"

    # Foydalanuvchining o'zi tarix yarata olmasligi kerak
    def has_add_permission(self, request):
        return False  # Tarixga yangi yozuv qo'shish huquqi yo'q

    # Foydalanuvchining kirdi Chiqdi tarixi uchun o'zgartirish huquqini cheklash
    def has_change_permission(self, request, obj=None):
        return False  # Kirdi Chiqdi o'zgartirish huquqi yo'q


# === KirdiChiqdi Admin ===
# Bu bo'lim kirim-chiqim operatsiyalarini boshqarish uchun.
@admin.register(KirdiChiqdi)
class KirdiChiqdiAdmin(admin.ModelAdmin):
    form = KirdiChiqdiForm  # Maxsus forma qo'llanadi
    list_display = (
        'id', 'mahsulot_nomi', 'miqdor', 'get_olchov_birligi', 'formatted_summa', 'sana',
        'colored_amaliyot_turi', 'kimga', 'qayerga')  # Ko'rinadigan ustunlar
    list_display_links = ('id', 'mahsulot_nomi')  # Mahsulotga bosilganda operatsiya ko'rsatiladi
    search_fields = ('mahsulot_nomi__mahsulot_nomi', 'amaliyot_turi')  # Mahsulot nomi va turiga qidiruv
    list_filter = ('amaliyot_turi', 'sana')  # Operatsiya turi va sanasi bo'yicha filter
    date_hierarchy = 'sana'  # Sanalar bo'yicha navigatsiya
    ordering = ('-sana',)  # Teskari tartibda tartib ko'rsatish
    list_per_page = 20  # Bir sahifada ko'rsatilgan elementlar soni
    actions = [download_excel, download_pdf, oylik_hisobot]
    change_list_template = "admin/kirdi_chiqdi_changelist.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['kirdi_upload_url'] = reverse('kirdi_upload')
        return super().changelist_view(request, extra_context=extra_context)

    def colored_amaliyot_turi(self, obj):
        """Amaliyot turini rangli qilib ko‘rsatadi."""
        if obj.amaliyot_turi == "Kirdi":
            return format_html('<span style="color: green;">{}</span>', obj.amaliyot_turi)
        elif obj.amaliyot_turi == "Chiqdi":
            return format_html('<span style="color: red;">{}</span>', obj.amaliyot_turi)
        return obj.amaliyot_turi

    colored_amaliyot_turi.short_description = "Amaliyot Turi"

    def get_olchov_birligi(self, obj):
        """Displays the 'olchov_birligi' of the related 'Mahsulot'."""
        return obj.mahsulot_nomi.olchov_birligi if obj.mahsulot_nomi else None

    get_olchov_birligi.short_description = "O'lchov Birligi"  # Header in the admin table

    def formatted_summa(self, obj):
        """Mahsulot summasini formatlangan holda ko'rsatadi."""
        if obj.amaliyot_turi == "Kirdi":
            return f"{obj.summa:,.2f}".replace(',', ' ')
        elif obj.amaliyot_turi == "Chiqdi":
            return f"{obj.summa:,.2f}".replace(',', ' ')
        return "0.00"

    formatted_summa.short_description = "Summa (so'm)"


# Qo'shimcha konfiguratsiya
# admin.site.site_header = "Tatuff Omborxona Boshqaruv Paneliga Xush Kelibsiz"  # Panelning bosh sarlavhasi
# admin.site.site_title = "Omborxona boshqaruvi administratori"  # Browser title
admin.site.index_title = "TATUFF Ombor"  # Tashrif sarlavhasi
