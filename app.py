import datetime
from collections import namedtuple
from flask import Flask, request
from flask_restful import Resource, Api
import json

app = Flask(__name__)
api = Api(app)


def calcular_tempo_com_sobreposicao(startA, startB, endA, endB):
    Range = namedtuple('Range', ['start', 'end'])
    r1 = Range(start=startA, end=endA)
    r2 = Range(start=startB, end=endB)
    latest_start = min(r1.start, r2.start)
    earliest_end = max(r1.end, r2.end)
    delta = (earliest_end - latest_start).days
    overlap = max(0, delta)
    return overlap


def calcular_tempo(lista: list):
    tempo = 0
    for x in lista:
        z = 0
        for y in lista:
            if x['start'] <= y['end'] and x['end'] >= y['start'] and x != y and y['somado'] is False:
                lista[lista.index(x)]['somado'] = True
                lista[lista.index(y)]['somado'] = True

                tempo_sobre = calcular_tempo_com_sobreposicao(
                    startA=x['start'],
                    endA=x['end'],
                    startB=y['start'],
                    endB=y['end'])
                if tempo_sobre > z:
                    z = tempo_sobre

        tempo += z
        if x['somado'] is False:
            delta = x['end'] - x['start']
            tempo += max(0, delta.days)
            lista[lista.index(x)]['somado'] = True
    return tempo


class Freelancer(Resource):
    def get(self):
        dados = {}
        with open('orama/examples/freelancer.json', 'r') as outfile:
            data = json.load(outfile)
            # Vamos carregar as informações do freelances
            for x in data['freelance']['professionalExperiences']:
                if x['id'] not in dados:
                    dados[x['id']] = {'skills': {}}
                for y in x['skills']:
                    if y['name'] not in dados[x['id']]['skills']:
                        dados[x['id']]['skills'][y['name']] = []
                    dados[x['id']]['skills'][y['name']].append({
                        'start': datetime.datetime.strptime(x['startDate'], '%Y-%m-%dT%H:%M:%S%z'),
                        'end': datetime.datetime.strptime(x['endDate'], '%Y-%m-%dT%H:%M:%S%z'),
                        'somado': False
                    })

            for id, value in dados.items():
                for skill, dates in value['skills'].items():
                    print(calcular_tempo(dates))
            return data


api.add_resource(Freelancer, '/')
if __name__ == '__main__':
    app.run(debug=True)
