import base64
from gerencianet import Gerencianet
from credenciais import CREDENTIALS

gn = Gerencianet(CREDENTIALS)

def gerar_pix(valor, id):
    body = {
        'calendario': {
            'expiracao': 3600
        },
        'devedor': {
            'cpf': '77829181721',
            'nome': 'Joseph Vabulck'
        },
        'valor': {
            'original': f'{valor}'
        },
        'chave': 'SUA CHAVE ALEATORIA',
        'solicitacaoPagador': f'Recarga de saldo para a carteira: {id} - SmsBot'
    }

    response = gn.pix_create_immediate_charge(body=body)
    print(response)
    txid = response["txid"]
    params = {
        'id': response["loc"]["id"]
    }
    location_id = response["loc"]["id"]
    response =  gn.pix_generate_QRCode(params=params)
    copia_cola = response["qrcode"]
    link_pag = response["linkVisualizacao"]
    response_all = {"locationId": location_id, "code": copia_cola, "link": link_pag, "txid": txid}
    return response_all

