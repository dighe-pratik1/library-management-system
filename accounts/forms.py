from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

def style_form(form):
    for field in form.fields.values():
        field.widget.attrs.setdefault("class", "form-control")
        field.widget.attrs.setdefault("placeholder", field.label)
    return form

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput,
                                validators=[validate_password])
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)

    def clean_username(self):
        value = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=value).exists():
            raise forms.ValidationError("This username is already in use.")
        return value

    def clean_email(self):
        value = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise forms.ValidationError("This email is already registered.")
        return value

    def clean(self):
        data = super().clean()
        if data.get("password1") and data.get("password2") and data["password1"] != data["password2"]:
            self.add_error("password2", "Passwords do not match.")
        return data

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Username", "autocomplete": "username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control", "placeholder": "Password", "autocomplete": "current-password"}))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class ResetPasswordForm(forms.Form):
    otp = forms.RegexField(regex=r"^\d{6}$", label="6-digit OTP")
    password1 = forms.CharField(label="New password", widget=forms.PasswordInput,
                                validators=[validate_password])
    password2 = forms.CharField(label="Confirm new password", widget=forms.PasswordInput)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)
    def clean(self):
        data = super().clean()
        if data.get("password1") and data.get("password2") and data["password1"] != data["password2"]:
            self.add_error("password2", "Passwords do not match.")
        return data

class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)
