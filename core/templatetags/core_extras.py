from django import template

from core.feriados import nome_feriado

register = template.Library()


@register.filter(name='feriado')
def feriado_filter(d):
    return nome_feriado(d) or ''


@register.simple_tag(takes_context=True)
def querystring_without_page(context):
    request = context['request']
    params = request.GET.copy()
    params.pop('page', None)
    encoded = params.urlencode()
    return f'&{encoded}' if encoded else ''
