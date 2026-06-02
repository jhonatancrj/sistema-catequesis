from django import forms

from sacramentos.models import RegistroSacramental
from sacramentos.models import Sacramento
from django import forms

from usuarios.models import Perfil

from .models import RegistroSacramental
from .models import Sacramento

class RegistroSacramentalForm(forms.ModelForm):

    class Meta:

        model = RegistroSacramental

        fields = [

            'fecha_sacramento',

            'lugar_sacramento',

            'parroco',

            'fecha_bautizo',

            'nombre_padre',

            'nombre_madre',

            'padrino',

            'madrina',
        ]

        widgets = {

            'fecha_sacramento': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'fecha_bautizo': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }



class RegistroSacramentalAdminForm(forms.ModelForm):

    participante = forms.ModelChoiceField(

        queryset=Perfil.objects.filter(
            rol='PARTICIPANTE'
        ),

        required=False,

        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )

    sacramento = forms.ModelChoiceField(

        queryset=Sacramento.objects.all(),

        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )

    class Meta:

        model = RegistroSacramental

        fields = [

            'participante',

            'nombre_manual',

            'apellido_manual',

            'sacramento',

            'fecha_sacramento',

            'lugar_sacramento',

            'parroco',

            'fecha_bautizo',

            'nombre_padre',

            'nombre_madre',

            'padrino',

            'madrina',
        ]

        widgets = {

            'nombre_manual': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'apellido_manual': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'fecha_sacramento': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'lugar_sacramento': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'parroco': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'fecha_bautizo': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),

            'nombre_padre': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'nombre_madre': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'padrino': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'madrina': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }