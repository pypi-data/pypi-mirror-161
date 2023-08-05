from django import template
register = template.Library()
from ..models import ConteudoCustom


@register.simple_tag()
def customizados_style_admin():
    
    customizados = []
    for conteudo in ConteudoCustom.objects.filter(local='Style - Admin'):
        customizados.append(conteudo.conteudo)
    
    return customizados

@register.simple_tag()
def customizados_head_admin():
    
    customizados = []
    for conteudo in ConteudoCustom.objects.filter(local='Head - Admin'):
        customizados.append(conteudo.conteudo)
    
    return customizados

@register.simple_tag()
def customizados_script_admin():
    
    customizados = []
    for conteudo in ConteudoCustom.objects.filter(local='Script - Admin'):
        customizados.append(conteudo.conteudo)
    
    return customizados

@register.simple_tag()
def customizados_logo_admin():

    customizado_logo = ConteudoCustom.objects.filter(local='Logo - Admin').last()
    
    return customizado_logo