import ipaddress
import math


def get_client_ip(request):
    """Retorna o IP real do cliente, respeitando X-Forwarded-For se houver proxy."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def ip_in_ranges(ip, ranges):
    """Verifica se `ip` pertence a pelo menos uma das redes em `ranges` (lista de CIDRs)."""
    if not ip:
        return False
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        return False
    for cidr in ranges:
        cidr = cidr.strip()
        if not cidr:
            continue
        try:
            if ip_obj in ipaddress.ip_network(cidr, strict=False):
                return True
        except ValueError:
            continue
    return False


def haversine_m(lat1, lng1, lat2, lng2):
    """Distância em metros entre dois pontos geográficos (fórmula de Haversine)."""
    R = 6371000  # raio da Terra em metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
