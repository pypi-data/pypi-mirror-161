from django.contrib.auth.views import PasswordChangeDoneView
from django.http import Http404
from ..models import ConfiguracaoAutenticacao

class PasswordChangeDoneSiteView(PasswordChangeDoneView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        configuracao_geral = ConfiguracaoAutenticacao.objects.filter(local='Geral - Site').last()
        if not configuracao_geral.possui_troca_senha:
            raise Http404()

        context['config_site'] = ConfiguracaoAutenticacao.objects.filter(local='Password Change Done - Site').last()

        return context