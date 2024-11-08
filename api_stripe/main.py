# create_main.py
from app import criar_assinatura, listar_assinaturas, cancelar_assinatura, criar_plano
from app import Plano  # Importa o modelo Plano

if __name__ == "__main__":
    # Criar um plano
    plano_data = {
        "nome": "Plano Básico",
        "valor": 1000,  # Valor em centavos
        "intervalo": "month",
        "moeda": "usd"
    }
    plano = criar_plano(Plano(**plano_data))  # Cria um objeto Plano e passa para a função

    # Verifica se o plano foi criado com sucesso
    if 'id' in plano:
        print(f"Plano criado com sucesso: {plano['id']}")

        # Criar uma assinatura (substitua 'cliente_id' pelo valor real)
        cliente_id = "cliente_id_exemplo"  # Substitua pelo ID real do cliente
        assinatura = criar_assinatura(cliente_id, plano['id'])

        # Verifica se a assinatura foi criada com sucesso
        if 'id' in assinatura:
            print(f"Assinatura criada com sucesso: {assinatura['id']}")

            # Listar assinaturas de um cliente
            assinaturas = listar_assinaturas(cliente_id)
            for a in assinaturas:
                print(f"Assinatura: {a['id']}, Status: {a['status']}")

            # Cancelar uma assinatura (substitua 'assinatura['id']' pelo ID real)
            resultado_cancelar = cancelar_assinatura(assinatura['id'])
            if 'message' in resultado_cancelar:
                print(resultado_cancelar['message'])
            else:
                print("Erro ao cancelar assinatura: " + resultado_cancelar.get('detail', 'Erro desconhecido'))
        else:
            print("Erro ao criar assinatura: " + assinatura.get('detail', 'Erro desconhecido'))
    else:
        print("Erro ao criar plano: " + plano.get('detail', 'Erro desconhecido'))
