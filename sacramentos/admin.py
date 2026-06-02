from django.contrib import admin

from .models import (
    Sacramento,
    RegistroSacramental
)


# ===================================
# SACRAMENTOS
# ===================================

@admin.register(Sacramento)

class SacramentoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nombre'
    )

    search_fields = (
        'nombre',
    )


# ===================================
# REGISTRO SACRAMENTAL
# ===================================

@admin.register(RegistroSacramental)

class RegistroSacramentalAdmin(admin.ModelAdmin):

    list_display = (

        'id',

        'obtener_participante',

        'sacramento',

        'fecha_sacramento',

        'lugar_sacramento',

        'parroco',

        'fecha_registro'
    )

    search_fields = (

        'participante__user__first_name',

        'participante__user__last_name',

        'nombre_manual',

        'apellido_manual',

        'parroco',

        'lugar_sacramento'
    )

    list_filter = (

        'sacramento',

        'fecha_sacramento',

        'fecha_registro'
    )

    readonly_fields = (
        'fecha_registro',
    )

    fieldsets = (

        (
            'Participante',
            {
                'fields': (
                    'participante',
                )
            }
        ),

        (
            'Datos Manuales',
            {
                'fields': (
                    'nombre_manual',
                    'apellido_manual'
                )
            }
        ),

        (
            'Sacramento',
            {
                'fields': (
                    'sacramento',
                )
            }
        ),

        (
            'Datos Sacramentales',
            {
                'fields': (

                    'fecha_sacramento',

                    'lugar_sacramento',

                    'parroco'
                )
            }
        ),

        (
            'Bautizo',
            {
                'fields': (
                    'fecha_bautizo',
                )
            }
        ),

        (
            'Padres',
            {
                'fields': (

                    'nombre_padre',

                    'nombre_madre'
                )
            }
        ),

        (
            'Padrinos',
            {
                'fields': (

                    'padrino',

                    'madrina'
                )
            }
        ),

        (
            'Registro',
            {
                'fields': (
                    'fecha_registro',
                )
            }
        )
    )

    def obtener_participante(self, obj):

        if obj.participante:

            return (

                f"{obj.participante.user.first_name} "
                f"{obj.participante.user.last_name}"
            )

        return (

            f"{obj.nombre_manual} "
            f"{obj.apellido_manual}"
        )

    obtener_participante.short_description = 'Participante'