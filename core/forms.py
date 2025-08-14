from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Shift

# Formular für Benutzer-Registrierung
class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, label="Rolle")

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data['role']
        user.role = role

        if role == 'admin':
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False

        if commit:
            user.save()
        return user


# Formular für Schicht-Erstellung
class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


# Formular nur für Tagesplanung (ohne Uhrzeiten)
class DayPlanForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
