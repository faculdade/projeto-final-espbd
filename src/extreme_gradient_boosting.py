# OK
import os
import sqlite3
import pandas as pd

import xgboost as xgb

#  █████╗ ██╗  ████████╗███████╗██████╗  █████╗ ██████╗
# ██╔══██╗██║  ╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗
# ███████║██║     ██║   █████╗  ██████╔╝███████║██████╔╝
# ██╔══██║██║     ██║   ██╔══╝  ██╔══██╗██╔══██║██╔══██╗
# ██║  ██║███████╗██║   ███████╗██║  ██║██║  ██║██║  ██║
# ╚═╝  ╚═╝╚══════╝╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝

# Definir o ID do produto desejado
ID_PRODUTO_UNICO = None

# Definir a data para previsão
DATA_PARA_PREVISAO = '2023-06-15'

# Data inicial para alimentar o modelo
DATA_INICIAL_PARA_PREVISAO = '1000-01-01'

# Data final para alimentar o modelo
DATA_FINAL_PARA_PREVISAO = '2023-05-30'

# ███╗   ██╗ █████╗  ██████╗      █████╗ ███╗   ██╗████████╗███████╗██████╗  █████╗ ██████╗
# ████╗  ██║██╔══██╗██╔═══██╗    ██╔══██╗████╗  ██║╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗
# ██╔██╗ ██║███████║██║   ██║    ███████║██╔██╗ ██║   ██║   █████╗  ██████╔╝███████║██████╔╝
# ██║╚██╗██║██╔══██║██║   ██║    ██╔══██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗██╔══██║██╔══██╗
# ██║ ╚████║██║  ██║╚██████╔╝    ██║  ██║██║ ╚████║   ██║   ███████╗██║  ██║██║  ██║██║  ██║
# ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝     ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, '../modelo_small.sqlite3')
file_path = os.path.join(BASE_DIR, 'output/xgboost.txt')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

if ID_PRODUTO_UNICO is None:
    sql = f'SELECT * FROM vendas_normalizadas WHERE data_venda BETWEEN \'{DATA_INICIAL_PARA_PREVISAO}\' and \'{DATA_FINAL_PARA_PREVISAO}\''
else:
    sql = f'SELECT * FROM vendas_normalizadas where produto_id = {ID_PRODUTO_UNICO} AND data_venda BETWEEN \'{DATA_INICIAL_PARA_PREVISAO}\' and \'{DATA_FINAL_PARA_PREVISAO}\''

df = pd.read_sql_query(sql, conn)

# Criar um dicionário para armazenar as previsões
previsoes_por_produto = {}

# Converter a coluna de data para o tipo datetime
df['data_venda'] = pd.to_datetime(df['data_venda'])

# Extrair características da data
df['ano'] = df['data_venda'].dt.year
df['mes'] = df['data_venda'].dt.month
df['dia'] = df['data_venda'].dt.day

# Obter a lista de produtos únicos
produtos = df['produto_id'].unique()

for produto_id in produtos:
    # Filtrar os dados para o produto atual
    df_produto = df[df['produto_id'] == produto_id].copy()

    # Verificar o número de amostras do produto atual
    num_amostras = len(df_produto)

    if num_amostras > 1:
        # Separar as features (ano, mes, dia) e o target (qtde_vendida)
        x = df_produto[['ano', 'mes', 'dia']].values
        y = df_produto['qtde_vendida'].values

        # Criar e treinar o modelo XGBoost de regressão
        model = xgb.XGBRegressor()
        model.fit(x, y)

        # Fazer previsões com base nos dados de treinamento
        y_pred = model.predict(x)

        # Fazer previsão para uma nova data
        nova_data = pd.to_datetime(DATA_PARA_PREVISAO)

        nova_ano = nova_data.year
        nova_mes = nova_data.month
        nova_dia = nova_data.day

        nova_previsao = model.predict([[nova_ano, nova_mes, nova_dia]])

        # Armazenar a previsão no dicionário
        previsoes_por_produto[produto_id] = nova_previsao
    else:
        # Armazenar a previsão no dicionário
        previsoes_por_produto[produto_id] = [0.0]

# Imprimir as previsões
if ID_PRODUTO_UNICO is None:
    with open(file_path, 'w') as file:
        file.write(f'produto_id;xgboost\n')

        for produto_id, previsao in previsoes_por_produto.items():
            file.write(f'{produto_id};{previsao[0]}\n')

    print('Geração do arquivo finalizada com sucesso.')
else:
    for produto_id, previsao in previsoes_por_produto.items():
        print(f'Produto: {produto_id} -- Previsão: {previsao[0]}')
