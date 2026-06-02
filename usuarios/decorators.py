from django.shortcuts import redirect
from functools import wraps

def rol_requerido(*roles):

    def decorator(view_func):

        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect('login')

            try:

                if request.user.perfil.rol not in roles:
                    return redirect('login')

            except:
                return redirect('login')

            return view_func(
                request,
                *args,
                **kwargs
            )

        return _wrapped_view

    return decorator

#def rol_requerido(roles):
 #   def decorator(view_func):
  #      def wrapper(request, *args, **kwargs):
   #         if not request.user.is_authenticated:
    #            return redirect('login')
#
 #           perfil = Perfil.objects.get(user=request.user)
  #          if perfil.rol not in roles:
   #             return redirect('home')
#
 #           return view_func(request, *args, **kwargs)
  #      return wrapper
   # return decorator

