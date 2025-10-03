from django import forms
from django.forms.widgets import ClearableFileInput
from .models import User, Profile, OtpCode, Address
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField

messages = {
    'required': 'لطفا این فیلد را پر کنید',
    'invalid': 'لطفا ایمیل معتبر را وارد کنید',
    'min_length': 'تعداد کاراکترهای ورودی کمتر از حدمجاز است',
    'max_length': 'تعداد کاراکترهای ورودی بیشتر از حدمجاز است',

}

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] and cd['password2'] and cd['password1'] != cd['password2']:
            raise ValidationError('پسورد ها یکی نیستند')
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        help_text='you can change password using <a href="../password/">this form</a>.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'last_login']

class UserRegisterationForm(forms.Form):
    username = forms.CharField(label='username', widget=forms.TextInput(attrs={'class': 'input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input'}))
    phone_number = forms.CharField(label='phone', max_length=11, widget=forms.TextInput(
        attrs={'type': 'tel', 'class': 'input'}))
    password1 = forms.CharField(label='password', widget=forms.PasswordInput(
        attrs={'type': 'password', 'class': 'input'}))
    password2 = forms.CharField(label='confirm password', widget=forms.PasswordInput(
        attrs={'type': 'password', 'class': 'input'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).exists()
        if user:
            raise ValidationError('این ایمیل از قبل وجود دارد')
        OtpCode.objects.filter(email=email).delete()
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        user = User.objects.filter(phone_number=phone_number).exists()
        if user:
            raise ValidationError('این شماره تماس از قبل وجود دارد')
        return phone_number

    def clean_username(self):
        username = self.cleaned_data['username']
        user = User.objects.filter(username=username).exists()
        if user:
            raise ValidationError('این نام کاربری از قبل وجود دارد')
        return username

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] and cd['password2'] and cd['password1'] != cd['password2']:
            raise ValidationError('پسورد ها یکی نیستند!')
        return cd['password2']

class UserLoginForm(forms.Form):
    email = forms.EmailField(label='email', widget=forms.EmailInput(
        attrs={'class': 'input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'type': 'password', 'class': 'input'}))

class CustomClearableFileInput(ClearableFileInput):
    template_name = 'accounts/custom_clearable_file_input.html'

class EditUserForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'input'}))
    phone_number = forms.CharField(label='phone', max_length=11, widget=forms.TextInput(
        attrs={'type': 'tel', 'class': 'input'}))
    username = forms.CharField(label='username', widget=forms.TextInput(attrs={'class': 'input'}))
    remove_image = forms.BooleanField(required=False, label='remove image')

    class Meta:
        model = Profile
        fields = ['age', 'image', 'full_name']
        widgets = {'image': CustomClearableFileInput()}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['phone_number'].initial = self.user.phone_number
            self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.user.pk).filter(email=email).exists():
            raise forms.ValidationError('این ایمیل از قبل استفاده شده است')
        return email

    def clean_phone(self):
        phone_number = self.cleaned_data['phone_number']
        if User.objects.exclude(pk=self.user.pk).filter(phone_number=phone_number).exists():
            raise forms.ValidationError('این شماره تلفن از قبل استفاده شده است')
        return phone_number

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(pk=self.user.pk).filter(username=username).exists():
            raise forms.ValidationError('این نام کاربری از قبل استفاده شده است')
        return username

    def save(self, commit=True):
        profile = super().save(commit=False)

        self.user.email = self.cleaned_data['email']
        self.user.username = self.cleaned_data['username']
        self.user.phone_number = self.cleaned_data['phone_number']

        if commit:
            self.user.save()
            profile.user = self.user
            profile.save()
        return profile

class VerifyCodeForm(forms.Form):
    code = forms.IntegerField()

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address', 'postal_code']
