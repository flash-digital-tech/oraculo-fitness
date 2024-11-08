import httpx
from configuracao import ASAAS_API_KEY, BASE_URL


# Configura o cabeçalho com a chave de API
HEADERS = {'access_token': ASAAS_API_KEY}


async def get_clientes():
    return await make_request('page_cliente')


async def create_cobranca(data):
    return await make_request('page_cobranca', method='POST', data=data)


async def split_pagamento(data):
    return await make_request('page_split', method='POST', data=data)


async def get_financeiro():
    return await make_request('page_financeiro')


async def make_request(endpoint, method='GET', data=None):
    url = f"{BASE_URL}/{endpoint}"

    async with httpx.AsyncClient() as client:
        try:
            if method == 'GET':
                response = await client.get(url, headers=HEADERS)
            elif method == 'POST':
                response = await client.post(url, headers=HEADERS, json=data)
            elif method == 'PUT':
                response = await client.put(url, headers=HEADERS, json=data)
            elif method == 'DELETE':
                response = await client.delete(url, headers=HEADERS)
            else:
                raise ValueError("Método HTTP não suportado.")

            # Verifica se a resposta foi bem-sucedida
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            print(f"Erro ao fazer a requisição: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}")
            return None

