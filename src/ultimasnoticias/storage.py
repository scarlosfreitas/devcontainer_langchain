# locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
import datetime as dt
import os
import sqlite3
from pathlib import Path


class Storage:
    DB_PATH = Path(os.getenv("PATH_DATA")) / os.getenv("PATH_DB_NOTICIAS")
    DB_NAME = "banco_noticias.db"
    DB_STRING = DB_PATH / DB_NAME

    def __init__(self, db_string=None, verbose=False):
        if db_string is not None:
            self.DB_STRING = Path(db_string)
            self.DB_PATH = self.DB_STRING.parent
            self.DB_NAME = self.DB_STRING.name

        if verbose:
            print("Storage inicializado:", self.DB_STRING)

    def create(self, db_string=None, verbose=False):
        if db_string is not None:
            self.DB_STRING = Path(db_string)
            self.DB_PATH = self.DB_STRING.parent
            self.DB_NAME = self.DB_STRING.name

        # Conecta (ou cria) o banco de dados
        os.makedirs(self.DB_PATH, exist_ok=True)
        conn = sqlite3.connect(self.DB_STRING)
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

        if verbose:
            print("Banco Criado: {}".format(self.DB_STRING))

        return self

    def insert(self, record, fonte="gran", verbose=False):
        # Conecta ao banco
        conn = sqlite3.connect(self.DB_STRING)
        cursor = conn.cursor()

        if "fcc" in fonte:
            texto_insert = "INSERT INTO {} (hashid, sefaz, txcompleto, url, tsatualizacao) VALUES (?, ?, ?, ?, ?)".format(
                fonte
            )
            tupla_dados = (
                record["hashid"],
                record["sefaz"],
                record["txcompleto"],
                record["url"],
                record["tsatualizacao"].isoformat(),
            )
        elif "cebraspe_novos" == fonte:
            texto_insert = "INSERT INTO {} (hashid, txcompleto, url, tsatualizacao) VALUES (?, ?, ?, ?)".format(
                fonte
            )
            tupla_dados = (
                record["hashid"],
                record["txcompleto"],
                record["url"],
                record["tsatualizacao"].isoformat(),
            )
        else:
            if fonte == "gran":
                fonte = "gran_noticias"
            texto_insert = """
            INSERT INTO {} (hashid, sefaz, dtnoticia, dsnoticia, txcompleto, url, tsatualizacao) VALUES (?, ?, ?, ?, ?, ?, ?)
            """.format(fonte)
            tupla_dados = (
                record["hashid"],
                record["sefaz"],
                record["dtnoticia"].isoformat(),
                record["dsnoticia"],
                record["txcompleto"],
                record["url"],
                record["tsatualizacao"].isoformat(),
            )

        # Inserção segura usando placeholders
        # print(texto_insert, tupla_dados)
        cursor.execute(texto_insert, tupla_dados)

        conn.commit()
        conn.close()

        if verbose:
            print("Registro inserido com sucesso!")

    def set_envio(self, hashid, flag=1, fonte="gran", verbose=False):
        # Conecta ao banco
        conn = sqlite3.connect(self.DB_STRING)
        cursor = conn.cursor()

        if fonte == "gran":
            fonte = "gran_noticias"
        texto_update = "UPDATE {} SET enviada = ? WHERE hashid = ? ".format(fonte)

        # Inserção segura usando placeholders
        cursor.execute(texto_update, (flag, hashid))

        conn.commit()
        conn.close()

        if verbose:
            print("Flag envio atualizada")

    def set_tsatualizacao(
        self,
        fonte="gran_noticias",
        uf=None,
        tsatualizacao=dt.datetime.now(),
        verbose=False,
    ):
        # Conecta ao banco
        conn = sqlite3.connect(self.DB_STRING)
        cursor = conn.cursor()

        if fonte == "gran":
            fonte = "gran_noticias"
        texto_update = (
            """UPDATE {} SET tsatualizacao = '{}' where sefaz = '{}'""".format(
                fonte, tsatualizacao.strftime("%Y-%m-%d %H:%M:%S"), uf
            )
        )

        # Inserção segura usando placeholders
        cursor.execute(texto_update)

        conn.commit()
        conn.close()

        if verbose:
            print("TS atualizado")

    def read(self, hashid, fonte="gran", verbose=False):
        # Conecta ao banco
        conn = sqlite3.connect(self.DB_STRING)
        cursor = conn.cursor()

        # Monta a consulta
        if fonte == "gran":
            fonte = "gran_noticias"
        query = "SELECT * FROM {} WHERE hashid = '{}'".format(fonte, hashid)
        if verbose:
            print("query", query)

        # Executa passando a lista como parâmetros
        cursor.execute(query)

        # Busca os resultados
        resultados = cursor.fetchall()

        conn.close()

        if verbose:
            print("Registro obtido")

        return resultados

    def last(self, days=5, fonte="gran", verbose=False):
        # Conecta ao banco
        conn = sqlite3.connect(self.DB_STRING)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        data_limite = (dt.datetime.now() - dt.timedelta(days=days)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # Formato compatível com SQLite

        if ("fcc" in fonte) or ("cebraspe_novos" == fonte):
            coluna = "tsatualizacao"
        else:
            coluna = "dtnoticia"

        if fonte == "gran":
            fonte = "gran_noticias"

        query = "SELECT * FROM {} WHERE {} >= ? order by {} desc".format(
            fonte, coluna, coluna
        )

        # Consulta records com data posterior a uma semana atrás
        cursor.execute(query, (data_limite,))

        resultados = cursor.fetchall()

        conn.close()

        if verbose:
            for row in resultados:
                if fonte == "cebraspe_novos":
                    print(
                        "CEBRASPE Novos", row["txcompleto"]
                    )  # Acessa pelo nome da coluna
                else:
                    print(
                        row["sefaz"].upper(), row["txcompleto"]
                    )  # Acessa pelo nome da coluna

                # print(row["email"])

        return resultados
