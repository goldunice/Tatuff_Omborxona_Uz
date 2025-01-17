# forms.py
from django import forms

class KirdiChiqdiUploadForm(forms.Form):
    file = forms.FileField(label="Excel faylni yuklang", required=True)
