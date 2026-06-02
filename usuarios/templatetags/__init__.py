from django import template

register = template.Library()

@register.filter
def get_iniciales(user):
    """Obtiene las iniciales del usuario basadas en nombre y apellido"""
    if hasattr(user, 'first_name'):
        first_name = user.first_name.strip()
        last_name = user.last_name.strip() if hasattr(user, 'last_name') else ''
    else:
        return user[0].upper() if user else '?'
    
    if first_name and last_name:
        iniciales = (first_name[0] + last_name[0]).upper()
    elif first_name:
        iniciales = first_name[0].upper()
    elif last_name:
        iniciales = last_name[0].upper()
    else:
        iniciales = user.username[0].upper() if hasattr(user, 'username') else '?'
    
    return iniciales
