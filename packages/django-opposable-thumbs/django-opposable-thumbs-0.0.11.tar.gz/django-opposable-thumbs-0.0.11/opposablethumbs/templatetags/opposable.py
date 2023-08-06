from django import template
from django.conf import settings
from urllib.parse import parse_qs, urlparse, urlencode

register = template.Library()

@register.simple_tag
def opposable(s):
    qs = parse_qs(s)
    if 'uri' in qs:
        for key in qs:
            qs[key] = qs[key][0]
        uri = urlparse(qs['uri'])
        domain_key = get_domain(f"{uri.scheme}://{uri.netloc}")
        if domain_key is not None:
            qs['domain'] = domain_key
            qs['uri'] = uri.path
            return urlencode(qs)

    # fallback: no change
    return s

def get_domain(url):
    if 'DOMAINS' in settings.OPPOSABLE_THUMBS and url in settings.OPPOSABLE_THUMBS['DOMAINS'].values():
        return list(settings.OPPOSABLE_THUMBS['DOMAINS'].keys())[list(settings.OPPOSABLE_THUMBS['DOMAINS'].values()).index(url)]
    return None