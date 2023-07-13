# OK
import os
import sqlite3
import pandas as pd

from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression

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
file_path = os.path.join(BASE_DIR, 'output/media_movel.txt')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

if ID_PRODUTO_UNICO is None:
    sql = f'SELECT * FROM vendas_normalizadas WHERE data_venda BETWEEN \'{DATA_INICIAL_PARA_PREVISAO}\' and \'{DATA_FINAL_PARA_PREVISAO}\''
else:
    sql = f'SELECT * FROM vendas_normalizadas where produto_id = {ID_PRODUTO_UNICO} AND data_venda BETWEEN \'{DATA_INICIAL_PARA_PREVISAO}\' and \'{DATA_FINAL_PARA_PREVISAO}\''

df = pd.read_sql_query(sql, conn)

# Criar um dicionário para armazenar as previsões
previsoes_por_produto = {}

# Iterar sobre os diferentes valores de produto_id
for produto_id in df['produto_id'].unique():
    # Filtrar os dados para o produto atual
    df_produto = df[df['produto_id'] == produto_id].copy()

    # Converter a coluna de data para o tipo datetime
    df_produto['data_venda'] = pd.to_datetime(df_produto['data_venda'])

    # Ordenar os dados pela data
    df_produto.sort_values('data_venda', inplace=True)

    # Extrair características da data
    df_produto['ano'] = df_produto['data_venda'].dt.year
    df_produto['mes'] = df_produto['data_venda'].dt.month
    df_produto['dia'] = df_produto['data_venda'].dt.day

    # Separar as features (ano, mes, dia) e o target (qtde_vendida)
    X = df_produto[['ano', 'mes', 'dia']].values
    y = df_produto['qtde_vendida'].values

    # Dividir os dados em conjunto de treinamento e teste
    train_size = int(0.8 * len(df_produto))
    X_train = X[:train_size]
    y_train = y[:train_size]
    X_test = X[train_size:]
    y_test = y[train_size:]

    # Verificar se há dados suficientes para treinamento
    if len(X_train) > 0:
        # Criar e treinar o modelo de regressão linear
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Fazer previsões com base nos dados de teste
        y_pred = model.predict(X_test)

        # Fazer previsão para uma nova data
        nova_data = pd.to_datetime(DATA_PARA_PREVISAO)

        nova_ano = nova_data.year
        nova_mes = nova_data.month
        nova_dia = nova_data.day

        nova_previsao = model.predict(
            [[nova_ano, nova_mes, nova_dia]])  # type: ignore

        # Armazenar a previsão no dicionário
        previsoes_por_produto[produto_id] = nova_previsao

    else:
        previsoes_por_produto[produto_id] = [0.0]

# Imprimir as previsões
if ID_PRODUTO_UNICO is None:
    with open(file_path, 'w') as file:
        file.write(f'produto_id;media_movel\n')

        for produto_id, previsao in previsoes_por_produto.items():
            file.write(f'{produto_id};{previsao[0]}\n')

    print('Geração do arquivo finalizada com sucesso.')
else:
    for produto_id, previsao in previsoes_por_produto.items():
        print(f'Produto: {produto_id} -- Previsão: {previsao[0]}')
