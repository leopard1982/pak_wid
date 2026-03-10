from django import forms
from .models import MasterCustomer, HeaderPeminjaman

class FormCustomer(forms.ModelForm):
    class Meta:
        model = MasterCustomer
        fields = "__all__"

class FormHeaderPinjam(forms.ModelForm):
    customer = FormCustomer()

    class Meta:
        model = HeaderPeminjaman
        fields = "__all__"

        widgets = {
            "customer": forms.Select(
                attrs={
                    'class':'form-select',
                    'required':'required',
                    'placeholder':'Judul Dataset...'
                }
            )
        }