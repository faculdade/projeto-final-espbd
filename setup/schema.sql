CREATE TABLE "empresas" (
	"id"	INTEGER NOT NULL,
	"cnpj"	TEXT,
	"inscricao_estadual"	TEXT,
	"nome_fantasia"	TEXT,
	"razao_social"	TEXT,
	"end_numero"	TEXT,
	"end_complemento"	TEXT,
	"end_logradouro"	TEXT,
	"end_cep"	TEXT,
	"end_bairro"	TEXT,
	"end_cidade"	TEXT,
	"end_estado"	TEXT,
	"end_pais"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "clientes" (
	"id"	INTEGER NOT NULL,
	"nome"	TEXT,
	"razao_social"	TEXT,
	"cpf_cnpj"	TEXT,
	"inscricao_estadual"	TEXT,
	"inscricao_municipal"	TEXT,
	"tipo"	INTEGER,
	"data_cadastro"	TEXT,
	"empresa_id"	INTEGER NOT NULL,
	"pessoa_eorbis_id"	INTEGER NOT NULL,
	"end_numero"	TEXT,
	"end_complemento"	TEXT,
	"end_logradouro"	TEXT,
	"end_cep"	TEXT,
	"end_bairro"	TEXT,
	"end_cidade"	TEXT,
	"end_estado"	TEXT,
	"end_pais"	TEXT,
	FOREIGN KEY("empresa_id") REFERENCES "empresas"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "produtos" (
	"id"	INTEGER NOT NULL,
	"produto_eorbis_id"	INTEGER NOT NULL,
	"codigo_catalogo"	TEXT,
	"codigo_interno"	TEXT,
	"descricao"	TEXT,
	"codigo_barra"	TEXT,
	"nome"	TEXT,
	"quantidade_estoque"	REAL,
	"marca"	TEXT,
	"grupo"	TEXT,
	"unidade"	TEXT,
	"ncm"	TEXT,
	"codigo_original"	TEXT,
	"quantidade_embalagem"	REAL,
	"preco_compra"	REAL,
	"qtde_min_venda"	REAL,
	PRIMARY KEY("id" AUTOINCREMENT)
);


CREATE TABLE "vendas" (
	"id"	INTEGER NOT NULL,
	"venda_eorbis_id"	INTEGER NOT NULL,
	"data_abertura"	TEXT,
	"cliente_id"	INTEGER,
	"valor_total"	REAL,
	"lucro"	REAL,
	"rentabilidade"	REAL,
	FOREIGN KEY("cliente_id") REFERENCES "clientes"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "venda_item" (
	"id"	INTEGER NOT NULL,
	"quantidade"	REAL,
	"valor_unitario"	REAL,
	"produto_id"	INTEGER,
	"venda_id"	INTEGER,
	"valor_total"	REAL,
	"valor_lucro"	REAL,
	"rentabilidade"	REAL,
	FOREIGN KEY("venda_id") REFERENCES "vendas"("id"),
	FOREIGN KEY("produto_id") REFERENCES "produtos"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

