# locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
import datetime as dt
import os
import sqlite3


def cria_banco(string_banco):
    # pasta_banco = 'sqlite'
    # banco_nome = 'banco_noticias.db'
    # string_banco = pasta_banco + '/' + banco_nome

    # Conecta (ou cria) o banco de dados
    os.makedirs(pasta_banco, exist_ok=True)
    conn = sqlite3.connect(string_banco)
    cursor = conn.cursor()

    # Cria a tabela se não existir
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gran_noticias (
        hashid TEXT PRIMARY KEY,      -- chave primária baseada em hash
        sefaz TEXT NOT NULL,
        dtnoticia TEXT NOT NULL,
        dsnoticia TEXT NOT NULL,
        txcompleto TEXT NOT NULL,
        url TEXT,
        enviada  INTEGER NOT NULL DEFAULT 0,
        tsatualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Cria a tabela se não existir
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fcc_linkarquivo (
        hashid TEXT PRIMARY KEY,      -- chave primária baseada em hash
        sefaz TEXT NOT NULL,
        txcompleto TEXT NOT NULL,
        url TEXT,
        enviada  INTEGER NOT NULL DEFAULT 0,
        tsatualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Cria a tabela se não existir
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fcc_publicacao (
        hashid TEXT PRIMARY KEY,      -- chave primária baseada em hash
        sefaz TEXT NOT NULL,
        txcompleto TEXT NOT NULL,
        url TEXT,
        enviada  INTEGER NOT NULL DEFAULT 0,
        tsatualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Cria a tabela se não existir
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cebraspe (
        hashid TEXT PRIMARY KEY,      -- chave primária baseada em hash
        sefaz TEXT NOT NULL,
        dtnoticia TEXT NOT NULL,
        dsnoticia TEXT NOT NULL,
        txcompleto TEXT NOT NULL,
        url TEXT,
        enviada  INTEGER NOT NULL DEFAULT 0,
        tsatualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Cria a tabela se não existir
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cebraspe_novos (
        hashid TEXT PRIMARY KEY,      -- chave primária baseada em hash
        txcompleto TEXT NOT NULL,
        url TEXT,
        enviada  INTEGER NOT NULL DEFAULT 0,
        tsatualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()


def insere_registro(registro, string_banco, fonte="gran_noticias"):
    # Conecta ao banco
    conn = sqlite3.connect(string_banco)
    cursor = conn.cursor()

    if "fcc" in fonte:
        texto_insert = "INSERT INTO {} (hashid, sefaz, txcompleto, url, tsatualizacao) VALUES (?, ?, ?, ?, ?)".format(
            fonte
        )
        tupla_dados = (
            registro["hashid"],
            registro["sefaz"],
            registro["txcompleto"],
            registro["url"],
            registro["tsatualizacao"].isoformat(),
        )
    elif "cebraspe_novos" == fonte:
        texto_insert = "INSERT INTO {} (hashid, txcompleto, url, tsatualizacao) VALUES (?, ?, ?, ?)".format(
            fonte
        )
        tupla_dados = (
            registro["hashid"],
            registro["txcompleto"],
            registro["url"],
            registro["tsatualizacao"].isoformat(),
        )
    else:
        texto_insert = """
        INSERT INTO {} (hashid, sefaz, dtnoticia, dsnoticia, txcompleto, url, tsatualizacao) VALUES (?, ?, ?, ?, ?, ?, ?)
        """.format(fonte)
        tupla_dados = (
            registro["hashid"],
            registro["sefaz"],
            registro["dtnoticia"].isoformat(),
            registro["dsnoticia"],
            registro["txcompleto"],
            registro["url"],
            registro["tsatualizacao"].isoformat(),
        )

    # Inserção segura usando placeholders
    # print(texto_insert, tupla_dados)
    cursor.execute(texto_insert, tupla_dados)

    # Salva a transação
    conn.commit()

    # Fecha a conexão
    conn.close()

    print("Registro inserido com sucesso!")


def seta_envio(hashid, string_banco, flag=1, fonte="gran_noticias"):
    # Conecta ao banco
    conn = sqlite3.connect(string_banco)
    cursor = conn.cursor()

    texto_update = "UPDATE {} SET enviada = ? WHERE hashid = ? ".format(fonte)

    # Inserção segura usando placeholders
    cursor.execute(texto_update, (flag, hashid))

    # Salva a transação
    conn.commit()

    # Fecha a conexão
    conn.close()

    print("Update com sucesso!")


def seta_tsatualizacao(
    string_banco, fonte="gran_noticias", sefaz=None, tsatualizacao=dt.datetime.now()
):
    # Conecta ao banco
    conn = sqlite3.connect(string_banco)
    cursor = conn.cursor()

    texto_update = """UPDATE {} SET tsatualizacao = '{}' where sefaz = '{}'""".format(
        fonte, tsatualizacao.strftime("%Y-%m-%d %H:%M:%S"), sefaz
    )

    # Inserção segura usando placeholders
    cursor.execute(texto_update)

    # Salva a transação
    conn.commit()

    # Fecha a conexão
    conn.close()

    print("Update com sucesso!")


def get_registro(hashid, string_banco, fonte="gran_noticias"):
    # Conecta ao banco
    conn = sqlite3.connect(string_banco)
    cursor = conn.cursor()

    # Monta a consulta
    query = "SELECT * FROM {} WHERE hashid = '{}'".format(fonte, hashid)

    # Executa passando a lista como parâmetros
    cursor.execute(query)

    # Busca os resultados
    resultados = cursor.fetchall()

    conn.close()

    return resultados


def get_ultimas_noticias(
    dias=5, string_banco="", fonte="gran_noticias", modo_silencioso=False
):
    # Conecta ao banco
    conn = sqlite3.connect(string_banco)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    data_limite = (dt.datetime.now() - dt.timedelta(days=dias)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )  # Formato compatível com SQLite
    if ("fcc" in fonte) or ("cebraspe_novos" == fonte):
        coluna = "tsatualizacao"
    else:
        coluna = "dtnoticia"

    query = "SELECT * FROM {} WHERE {} >= ? order by {} desc".format(
        fonte, coluna, coluna
    )

    # Consulta registros com data posterior a uma semana atrás
    cursor.execute(query, (data_limite,))

    resultados = cursor.fetchall()

    if not modo_silencioso:
        for row in resultados:
            if fonte == "cebraspe_novos":
                print("CEBRASPE Novos", row["txcompleto"])  # Acessa pelo nome da coluna
            else:
                print(
                    row["sefaz"].upper(), row["txcompleto"]
                )  # Acessa pelo nome da coluna

            # print(row["email"])

    conn.close()

    return resultados
