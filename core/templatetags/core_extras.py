from django import template

from core.feriados import nome_feriado

register = template.Library()


@register.filter(name='feriado')
def feriado_filter(d):
    """Retorna o nome do feriado se `d` for feriado nacional, senão string vazia."""
    return nome_feriado(d) or ''


@register.simple_tag(takes_context=True)
def querystring_without_page(context):
    """Retorna a querystring atual sem o parâmetro `page`, pronta para concatenar."""
    request = context['request']
    params = request.GET.copy()
    params.pop('page', None)
    encoded = params.urlencode()
    return f'&{encoded}' if encoded else ''
