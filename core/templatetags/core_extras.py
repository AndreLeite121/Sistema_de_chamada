from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def querystring_without_page(context):
    """Retorna a querystring atual sem o parâmetro `page`, pronta para concatenar."""
    request = context['request']
    params = request.GET.copy()
    params.pop('page', None)
    encoded = params.urlencode()
    return f'&{encoded}' if encoded else ''
