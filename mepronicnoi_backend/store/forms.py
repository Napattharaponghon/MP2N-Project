from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'note']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ชื่อ-นามสกุล'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'อีเมล'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'เบอร์โทรศัพท์'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3,
                                              'placeholder': 'บ้านเลขที่ ถนน แขวง เขต จังหวัด รหัสไปรษณีย์'}),
            'note': forms.Textarea(attrs={'class': 'form-input', 'rows': 2,
                                           'placeholder': 'หมายเหตุเพิ่มเติม (ถ้ามี)'}),
        }
        labels = {
            'full_name': 'ชื่อ-นามสกุล',
            'email': 'อีเมล',
            'phone': 'เบอร์โทรศัพท์',
            'address': 'ที่อยู่จัดส่ง',
            'note': 'หมายเหตุ',
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True,
                              widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'อีเมล'}))
    first_name = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ชื่อ'}))
    last_name = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'นามสกุล'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ชื่อผู้ใช้'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'รหัสผ่าน'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'ยืนยันรหัสผ่าน'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user
