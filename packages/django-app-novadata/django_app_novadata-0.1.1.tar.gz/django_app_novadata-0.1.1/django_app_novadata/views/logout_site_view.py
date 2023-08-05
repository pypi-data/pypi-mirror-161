from django.contrib.auth.views import LogoutView
from ..models import ConfiguracaoAutenticacao

class LogoutSiteView(LogoutView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        

        context['config_site'] = ConfiguracaoAutenticacao.objects.filter(local='Logout - Site').last()

        return context