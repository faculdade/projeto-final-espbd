import sqlite3
import os

from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, '../modelo_small.sqlite3')
file_path = os.path.join(BASE_DIR, 'output/eorbis.txt')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

sql_padrao = f'SELECT produto_id, AVG(qtde_vendida) AS media_aritmetica FROM vendas_normalizadas GROUP BY produto_id;'
cursor.execute(sql_padrao)
result = cursor.fetchall()

cursor.close()
conn.close()

with open(file_path, 'w') as file:
    file.write(f'produto_id;media_aritimetica\n')

    for line in result:
        file.write(f"{line[0]};{line[1]}\n")

print('Geração do arquivo finalizada com sucesso.')
