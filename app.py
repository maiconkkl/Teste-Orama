import datetime
from collections import namedtuple
from flask import Flask
from flask_restx import Resource, Api, reqparse, fields
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


parser = reqparse.RequestParser()
parser.add_argument('id', type=int, default=0)
parser.add_argument('status', type=str, default='seeking')
parser.add_argument('startDate', type=str, default='2018-07-14T09:31:21+02:00')
parser.add_argument('retributionWished', type=int, default=0)
parser.add_argument('durationInDays', type=int, default=0)
parser.add_argument('expertise_id', type=int, default=0)
parser.add_argument('expertise_name', type=str, default='')
parser.add_argument('skills', type=list, default=[])


@api.route('/freelance')
class Freelancer(Resource):
    @api.expect(parser, validate=True)
    def post(self):
        print(parser.parse_args())
        try:
            with open('examples/freelancer.json', 'r') as outfile:
                data = {}
                data_json = json.load(outfile)
                # Vamos carregar as informações do freelances
                for x in data_json['freelance']['professionalExperiences']:
                    if x['id'] not in data:
                        data[x['id']] = {'skills': {}}
                    # Vamos coletar todas as habilidades
                    for y in x['skills']:
                        # Verificando se essa habilidade ja foi coletada
                        if y['id'] not in data[x['id']]['skills']:
                            data[x['id']]['skills'][y['id']] = {
                                'id': y['id'],
                                'name': y['name'],
                                'dates': []
                            }

                        # Coletando o tempo de serviço dessa habilidade
                        data[x['id']]['skills'][y['id']]['dates'].append({
                            'start': datetime.datetime.strptime(x['startDate'], '%Y-%m-%dT%H:%M:%S%z'),
                            'end': datetime.datetime.strptime(x['endDate'], '%Y-%m-%dT%H:%M:%S%z'),
                            'somado': False
                        })

                # Vamos prepara os dados de retorno
                data_return = {
                    "freelance": []
                }
                for id, value in data.items():
                    freelance = {
                        'id': id,
                        "computedSkills": []
                    }

                    # Antes de prosseguir, vamos calcular o tempo de serviço
                    for skill_id, value_skill in value['skills'].items():
                        skill_return = {
                            "id": value_skill['id'],
                            "name": value_skill['name'],
                            "durationInMonths": int(calcular_tempo(value_skill['dates']) / 30)
                        }
                        freelance['computedSkills'].append(skill_return)

                    data_return['freelance'].append(freelance)

                return data_return
        except:
            content = {'error': 'payload is invalid'}
            return content, 422


if __name__ == '__main__':
    app.run(debug=True)
