from django import forms
from .models import Tarea


class TareaForm(forms.ModelForm):

    class Meta:

        model = Tarea

        fields = [

            'titulo',
            'descripcion',

            'fecha_entrega',

            'permitir_tardia',
            'fecha_limite_tardia',

            'clase'

        ]

        widgets = {

            'titulo': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5
                }
            ),

            'fecha_entrega': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),

            'fecha_limite_tardia': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),

            'permitir_tardia': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),

            'clase': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            )

        }