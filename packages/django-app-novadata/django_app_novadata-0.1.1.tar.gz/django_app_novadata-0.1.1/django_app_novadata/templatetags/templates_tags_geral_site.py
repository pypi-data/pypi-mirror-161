from django import template
register = template.Library()
from ..models import ConfiguracaoAutenticacao


@register.simple_tag()
def configuracao_autenticacao_geral():
    
    return ConfiguracaoAutenticacao.objects.filter(local='Geral - Site').last()