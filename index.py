from datetime import datetime
from collections import namedtuple


def sobreposicao(startA, startB, endA, endB):
    Range = namedtuple('Range', ['start', 'end'])
    r1 = Range(start=startA, end=endA)
    r2 = Range(start=startB, end=endB)
    latest_start = min(r1.start, r2.start)
    earliest_end = max(r1.end, r2.end)
    delta = (earliest_end - latest_start).days
    overlap = max(0, delta)
    return overlap


lista = [
    {
        'start': datetime(2012, 1, 1),
        'end': datetime(2012, 7, 1),
        's': False
    },
    {
        'start': datetime(2012, 2, 1),
        'end': datetime(2012, 3, 1),
        's': False
    },
    {
        'start': datetime(2012, 6, 1),
        'end': datetime(2012, 8, 1),
        's': False
    },
    {
        'start': datetime(2018, 1, 1),
        'end': datetime(2018, 7, 1),
        's': False
    },
]
tempo = 0

for x in lista:
    z = 0
    for y in lista:
        if x['start'] <= y['end'] and x['end'] >= y['start'] and x != y and y['s'] is False:
            lista[lista.index(x)]['s'] = True
            lista[lista.index(y)]['s'] = True

            tempo_sobre = sobreposicao(startA=x['start'], endA=x['end'], startB=y['start'], endB=y['end'])
            if tempo_sobre > z:
                z = tempo_sobre

    tempo += z
    if x['s'] is False:
        delta = x['end'] - x['start']
        tempo += max(0, delta.days)
        lista[lista.index(x)]['s'] = True
print(tempo)
