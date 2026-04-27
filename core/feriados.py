from datetime import date, timedelta


def pascoa(ano):
    # Computus, metodo de Meeus/Jones/Butcher
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    ll = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ll) // 451
    mes = (h + ll - 7 * m + 114) // 31
    dia = ((h + ll - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia)


def feriados_br(ano):
    easter = pascoa(ano)
    return {
        date(ano, 1, 1): 'Confraternização Universal',
        easter - timedelta(days=48): 'Carnaval (segunda)',
        easter - timedelta(days=47): 'Carnaval (terça)',
        easter - timedelta(days=2): 'Sexta-feira Santa',
        date(ano, 4, 21): 'Tiradentes',
        date(ano, 5, 1): 'Dia do Trabalho',
        easter + timedelta(days=60): 'Corpus Christi',
        date(ano, 9, 7): 'Independência do Brasil',
        date(ano, 10, 12): 'Nossa Senhora Aparecida',
        date(ano, 11, 2): 'Finados',
        date(ano, 11, 15): 'Proclamação da República',
        date(ano, 11, 20): 'Consciência Negra',
        date(ano, 12, 25): 'Natal',
    }


def nome_feriado(d):
    if not d:
        return None
    return feriados_br(d.year).get(d)
