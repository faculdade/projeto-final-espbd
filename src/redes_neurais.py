# ERRO

import os
import sqlite3
import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'modelo_small.sqlite3')
file_path = os.path.join(BASE_DIR, 'output/redes_neurais.txt')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Carregar os dados do histórico de vendas
sql = 'SELECT * FROM vendas_normalizadas where produto_id = 242'
df = pd.read_sql_query(sql, conn)

# Converter a coluna 'data_venda' para o tipo datetime
df['data_venda'] = pd.to_datetime(df['data_venda'])

# Ordenar o DataFrame por data de venda
df = df.sort_values('data_venda')

# Calcular o número de dias desde a primeira venda
df['dias_desde_primeira_venda'] = (
    df['data_venda'] - df['data_venda'].min()).dt.days

# Criar o DataFrame com as colunas relevantes (dias desde a primeira venda e quantidade vendida)
df_produto = df[['dias_desde_primeira_venda', 'qtde_vendida']].copy()

# Normalizar os dados
scaler = MinMaxScaler(feature_range=(0, 1))
df_produto[['dias_desde_primeira_venda', 'qtde_vendida']] = scaler.fit_transform(
    df_produto[['dias_desde_primeira_venda', 'qtde_vendida']])

# Separar as features (dias desde a primeira venda) e o target (quantidade vendida)
X = df_produto['dias_desde_primeira_venda'].values.reshape(-1, 1)
y = df_produto['qtde_vendida'].values.ravel()

# Criar e treinar o modelo de rede neural
model = MLPRegressor(hidden_layer_sizes=(10, 10), random_state=42)
model.fit(X, y)

# Obter o número de dias desde a primeira venda para a nova data
nova_data = '2023-05-30'  # Definir a nova data desejada
nova_data = datetime.strptime(nova_data, '%Y-%m-%d')
dias_desde_primeira_venda_nova_data = (nova_data - df['data_venda'].min()).days

# Normalizar os dados da nova data
nova_data_normalizada = np.array([[dias_desde_primeira_venda_nova_data]])
nova_data_normalizada = scaler.transform(nova_data_normalizada)

# Fazer a previsão para a nova data
quantidade_vendas_prevista = model.predict(nova_data_normalizada)

# Desnormalizar a nova data
nova_data_desnormalizada = np.array([[dias_desde_primeira_venda_nova_data]])
nova_data_desnormalizada = scaler.inverse_transform(nova_data_desnormalizada)

# Desnormalizar a quantidade de vendas prevista
quantidade_vendas_prevista_desnormalizada = scaler.inverse_transform(
    quantidade_vendas_prevista.reshape(-1, 1))

# Imprimir a previsão de quantidade de vendas para a nova data
print(
    f'Previsão de quantidade de vendas para {nova_data}: {quantidade_vendas_prevista_desnormalizada[0][0]:.2f}')
