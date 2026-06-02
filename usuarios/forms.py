from django import forms
from django.contrib.auth.models import User
from .models import Perfil

class RegistroForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput
    )

    # 🔹 CAMPOS NUEVOS (Perfil)
    genero = forms.ChoiceField(
        choices=[
            ('', 'Seleccione género'),
            ('M', 'Masculino'),
            ('F', 'Femenino'),
            ('N', 'Prefiero no decirlo')
        ],
        required=False
    )
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Fecha de nacimiento'
    )
    telefono = forms.CharField(required=False)
    pais = forms.CharField(required=False)
    departamento = forms.CharField(required=False)
    ciudad = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado')
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return p2
    

class EditarAdministradorForm(forms.ModelForm):

    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput
    )

    class Meta:

        model = Perfil

        fields = [

            'telefono',
            'pais',
            'departamento',
            'ciudad',
            'fecha_nacimiento',
            'genero',
            'rol'

        ]

        widgets = {

            'fecha_nacimiento': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            )

        }

    def __init__(self, *args, **kwargs):

        self.user_instance = kwargs.pop(
            'user_instance',
            None
        )

        super().__init__(*args, **kwargs)

        if self.user_instance:

            self.fields['username'].initial = self.user_instance.username

            self.fields['first_name'].initial = self.user_instance.first_name

            self.fields['last_name'].initial = self.user_instance.last_name

            self.fields['email'].initial = self.user_instance.email

    def save(self, commit=True):

        perfil = super().save(commit=False)

        user = perfil.user

        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        password = self.cleaned_data.get('password')

        if password:
            user.set_password(password)

        if commit:
            user.save()
            perfil.save()

        return perfil


class EditarMiPerfilForm(forms.ModelForm):
    """Formulario para que los usuarios editen su propio perfil"""
    
    first_name = forms.CharField(
        label='Nombre',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido'
        })
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
    )
    password = forms.CharField(
        label='Nueva contraseña (opcional)',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dejar en blanco para no cambiar'
        })
    )
    password_confirm = forms.CharField(
        label='Confirmar contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })
    )

    class Meta:
        model = Perfil
        fields = [
            'telefono',
            'fecha_nacimiento',
            'genero',
            'pais',
            'departamento',
            'ciudad'
        ]
        widgets = {
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu teléfono'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-select'
            }),
            'pais': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'País'
            }),
            'departamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Departamento/Provincia'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        
        if self.user_instance:
            self.fields['first_name'].initial = self.user_instance.first_name
            self.fields['last_name'].initial = self.user_instance.last_name
            self.fields['email'].initial = self.user_instance.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user_instance and email != self.user_instance.email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('Este correo ya está registrado')
        return email

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        if password and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden')
        return password_confirm

    def save(self, commit=True):
        perfil = super().save(commit=False)
        user = perfil.user
        
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
            perfil.save()
        
        return perfil