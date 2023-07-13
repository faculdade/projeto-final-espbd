import os
import sqlite3
import warnings
import pandas as pd

from sklearn.neural_network import MLPRegressor
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)

#  █████╗ ██╗  ████████╗███████╗██████╗  █████╗ ██████╗
# ██╔══██╗██║  ╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗
# ███████║██║     ██║   █████╗  ██████╔╝███████║██████╔╝
# ██╔══██║██║     ██║   ██╔══╝  ██╔══██╗██╔══██║██╔══██╗
# ██║  ██║███████╗██║   ███████╗██║  ██║██║  ██║██║  ██║
# ╚═╝  ╚═╝╚══════╝╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝

# Define the ID of the desired product
ID_PRODUTO_UNICO = None

# Define the date for prediction
DATA_PARA_PREVISAO = '2023-06-15'

# Data initial to feed the model
DATA_INICIAL_PARA_PREVISAO = '1000-01-01'

# Data final to feed the model
DATA_FINAL_PARA_PREVISAO = '2023-05-30'

# ███╗   ██╗ █████╗  ██████╗      █████╗ ███╗   ██╗████████╗███████╗██████╗  █████╗ ██████╗
# ████╗  ██║██╔══██╗██╔═══██╗    ██╔══██╗████╗  ██║╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗
# ██╔██╗ ██║███████║██║   ██║    ███████║██╔██╗ ██║   ██║   █████╗  ██████╔╝███████║██████╔╝
# ██║╚██╗██║██╔══██║██║   ██║    ██╔══██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗██╔══██║██╔══██╗
# ██║ ╚████║██║  ██║╚██████╔╝    ██║  ██║██║ ╚████║   ██║   ███████╗██║  ██║██║  ██║██║  ██║
# ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝     ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, '../modelo_small.sqlite3')
file_path = os.path.join(BASE_DIR, 'output/redes_neurais.txt')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

if ID_PRODUTO_UNICO is None:
    sql = f'SELECT * FROM vendas_normalizadas WHERE data_venda BETWEEN \'{DATA_INICIAL_PARA_PREVISAO}\' and \'{DATA_FINAL_PARA_PREVISAO}\''
else:
    sql = f'SELECT * FROM vendas_normalizadas where produto_id = {ID_PRODUTO_UNICO} AND data_venda BETWEEN \'{DATA_INICIAL_PARA_PREVISAO}\' and \'{DATA_FINAL_PARA_PREVISAO}\''

df = pd.read_sql_query(sql, conn)

# Create a dictionary to store the predictions
previsoes_por_produto = {}

# Get the list of unique products
produtos_unicos = df['produto_id'].unique()

# Iterate over each product
for produto_id in produtos_unicos:
    # Filter the data for the desired product and create an explicit copy
    df_produto = df[df['produto_id'] == produto_id].copy()

    # Convert the date column to datetime type
    df_produto['data_venda'] = pd.to_datetime(df_produto['data_venda'])

    # Extract date features
    df_produto['ano'] = df_produto['data_venda'].dt.year
    df_produto['mes'] = df_produto['data_venda'].dt.month
    df_produto['dia'] = df_produto['data_venda'].dt.day

    # Separate the features (ano, mes, dia) and the target (qtde_vendida)
    X = df_produto[['ano', 'mes', 'dia']].values
    y = df_produto['qtde_vendida'].values

    # Create and train the neural network model
    model = MLPRegressor(hidden_layer_sizes=(
        10, 10), max_iter=1000, random_state=42)
    model.fit(X, y)

    # Make a prediction for a new date
    nova_data = pd.to_datetime(DATA_PARA_PREVISAO)
    nova_ano = nova_data.year
    nova_mes = nova_data.month
    nova_dia = nova_data.day
    nova_previsao = model.predict([[nova_ano, nova_mes, nova_dia]])

    # Store the prediction in the dictionary
    previsoes_por_produto[produto_id] = nova_previsao

# Print the predictions
if ID_PRODUTO_UNICO is None:
    with open(file_path, 'w') as file:
        file.write(f'produto_id;redes_neurais\n')

        for produto_id, previsao in previsoes_por_produto.items():
            file.write(f'{produto_id};{previsao[0]}\n')

    print('Generation of the file completed successfully.')
else:
    for produto_id, previsao in previsoes_por_produto.items():
        print(f'Product: {produto_id} -- Prediction: {previsao[0]}')
