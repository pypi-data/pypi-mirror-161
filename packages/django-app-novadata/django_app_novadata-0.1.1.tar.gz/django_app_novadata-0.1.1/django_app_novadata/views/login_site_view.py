from django.contrib.auth.views import LoginView
from ..models import ConfiguracaoAutenticacao

class LoginSiteView(LoginView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        

        context['config_site'] = ConfiguracaoAutenticacao.objects.filter(local='Login - Site').last()

        return context