#!/usr/bin/env python3

import sqlite3
import psycopg2
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'modelo_small.sqlite3')

conn_sqlite = sqlite3.connect(db_path)
cursor_sqlite = conn_sqlite.cursor()

conn_postgres = psycopg2.connect(
    database="soinjecao", host="localhost", user="postgres", password="mtprmeaie!", port="5432")
cursor_postgres = conn_postgres.cursor()


def main():
    # migrar_empresas()
    # migrar_clientes()
    # migrar_produtos()
    # atualizar_produto()
    migrar_vendas()
    #migrar_venda_item()


def migrar_empresas():
    sql_eorbis = "SELECT cnpj,inscricao_estadual, nome_fantasia, razao_social, numero, complemento, logradouro, cep, bairro, municipio, uf, 'BRASIL' FROM empresa"
    sql_sqlite = "INSERT INTO empresas (cnpj, inscricao_estadual, nome_fantasia, razao_social, end_numero, end_complemento, end_logradouro, end_cep, end_bairro, end_cidade, end_estado, end_pais) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "

    cursor_postgres.execute(sql_eorbis)
    results = cursor_postgres.fetchall()

    for l in results:
        try:
            cursor_sqlite.execute(
                sql_sqlite, (l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8], l[9], l[10], l[11]))
        except Exception as err:
            print(l)
            print(err)
            pass

    conn_sqlite.commit()


def migrar_clientes():
    sql_eorbis = "SELECT p.alias_nome_fantasia, p.nome, p.cpf_cnpj, p.inscricao_estadual, p.inscricao_municipal, p.tipo, c.desde, 1, e.numero, e.complemento, e.logradouro, e.cep, e.bairro, e.cidade, e.uf, e.pais, p.id FROM cliente c INNER JOIN pessoa p ON (c.id_pessoa = p.id) INNER JOIN endereco e ON (e.id_pessoa = p.id)"
    sql_sqlite = "INSERT INTO clientes (nome, razao_social, cpf_cnpj, inscricao_estadual, inscricao_municipal, tipo, data_cadastro, empresa_id, end_numero, end_complemento, end_logradouro, end_cep, end_bairro, end_cidade, end_estado, end_pais, pessoa_eorbis_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    cursor_postgres.execute(sql_eorbis)
    results = cursor_postgres.fetchall()

    for l in results:
        try:
            cursor_sqlite.execute(sql_sqlite, (l[0], l[1], l[2], l[3], l[4], l[5],
                                  l[6], l[7], l[8], l[9], l[10], l[11], l[12], l[13], l[14], l[15], l[16]))
        except Exception as err:
            print(l)
            print(err)
            pass

    conn_sqlite.commit()


def migrar_produtos():
    sql_eorbis = "SELECT p.codigo_catalogo, p.codigo_interno, p.descricao, p.gtin, p.nome, p.quantidade_estoque::float, m.nome, sgp.nome, up.descricao, n.ncm_completo, p.codigo_original, p.quantidade_embalagem::float, 0, 0, p.id FROM produto p INNER JOIN marca_produto m ON (p.id_marca_produto = m.id) INNER JOIN sub_grupo_produto sgp ON (p.id_sub_grupo = sgp.id) INNER JOIN unidade_produto up ON (p.id_unidade = up.id) INNER JOIN ncm n ON (p.ncm_id = n.id)"
    sql_sqlite = "INSERT INTO produtos (codigo_catalogo, codigo_interno, descricao, codigo_barra, nome, quantidade_estoque, marca, grupo, unidade, ncm, codigo_original, quantidade_embalagem, preco_compra, qtde_min_venda, produto_eorbis_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    cursor_postgres.execute(sql_eorbis)
    results = cursor_postgres.fetchall()

    for l in results:
        try:
            cursor_sqlite.execute(sql_sqlite, (l[0], l[1], l[2], l[3], l[4],
                                  l[5], l[6], l[7], l[8], l[9], l[10], l[11], l[12], l[13], l[14]))
        except Exception as err:
            print(l)
            print(err)
            pass

    conn_sqlite.commit()


def atualizar_produto():
    sql_eorbis = "SELECT pe.produto_id, pc.preco_compra::float as preco_compra, pc.qtde_minima::float as qtde_minima_venda FROM produto_estoque pe INNER JOIN produto_custo pc on (pe.id = pc.produto_estoque_id) WHERE pe.empresa_id = 1 ORDER BY pe.produto_id"
    sql_sqlite = "UPDATE produtos SET preco_compra = ?, qtde_min_venda = ? WHERE produto_eorbis_id = ?"

    cursor_postgres.execute(sql_eorbis)
    results = cursor_postgres.fetchall()

    for l in results:
        try:
            cursor_sqlite.execute(sql_sqlite, (l[1], l[2], l[0]))
        except Exception as err:
            print(err)
            print(l)
            pass

    conn_sqlite.commit()


def migrar_vendas():
    sql_eorbis = "SELECT v.data_abertura, c.id_pessoa, 0 as valor_total, 0 as lucro, 0 as rentabilidade, v.id FROM venda v INNER JOIN cliente c ON (v.id_cliente = c.id)"
    sql_sqlite = "INSERT INTO vendas (data_abertura, cliente_id, valor_total, lucro, rentabilidade, venda_eorbis_id) VALUES (?, ?, ?, ?, ?, ?)"

    cursor_postgres.execute(sql_eorbis)
    results = cursor_postgres.fetchall()

    for l in results:
        try:
            cursor_sqlite.execute(
                "SELECT id FROM clientes WHERE pessoa_eorbis_id = ?", (l[1],))
            row = cursor_sqlite.fetchone()

            if len(row) > 0 and row[0] is not None:
                cursor_sqlite.execute(
                    sql_sqlite, (l[0], row[0], l[2], l[3], l[4], l[5]))

        except Exception as err:
            print(err)
            print(l)
            pass

    conn_sqlite.commit()


def migrar_venda_item():
    sql_eorbis = "SELECT vi.quantidade::float, vi.valor_unitario::float, pe.produto_id, vi.id_venda, vi.valor_total::float, vi.valor_lucro::float, vi.rentabilidade::float FROM   venda_item vi INNER JOIN produto_estoque pe ON (pe.id = vi.id_produto)"
    sql_sqlite = "INSERT INTO venda_item (quantidade, valor_unitario, produto_id, venda_id, valor_total, valor_lucro, rentabilidade) VALUES (?, ?, ?, ?, ?, ?, ?)"

    cursor_postgres.execute(sql_eorbis)
    results = cursor_postgres.fetchall()

    qtde_total = len(results)
    i = 0
    indice = 1
    for l in results:
        try:
            cursor_sqlite.execute(
                "SELECT id FROM produtos WHERE produto_eorbis_id = ?", (l[2],))
            produto = cursor_sqlite.fetchone()

            cursor_sqlite.execute(
                "SELECT id FROM vendas WHERE venda_eorbis_id = ?", (l[3],))
            venda = cursor_sqlite.fetchone()

            if (produto[0] is not None and len(produto) > 0) and (venda is not None and venda[0] is not None and len(venda) > 0):
                with open("venda_item.txt", "a+") as f:
                    string = f'{indice}, {l[0]}, {l[1]}, {produto[0]}, {venda[0]}, {l[4]}, {l[5]}, {l[6]} \n'
                    f.write(string)
                    indice = indice + 1

            if i == 1000:
                qtde_total = qtde_total - 1000
                print(qtde_total)
                i = 0
            else:
                i = i + 1

        except Exception as err:
            print(err)
            print(l)
            pass

    conn_sqlite.commit()


def close():
    # Fechando SQLite
    cursor_sqlite.close()
    conn_sqlite.close()

    # Fechando Postgres
    cursor_postgres.close()
    conn_postgres.close()


if __name__ == '__main__':
    main()
    close()
