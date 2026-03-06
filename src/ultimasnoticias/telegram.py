# locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
import os

import requests

from .storage import Storage


class Telegram:
    TOKEN = os.getenv("TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    def __init__(self, db=None, verbose=False):
        if db is None:
            self.db = Storage()
        else:
            self.db = db

        if verbose:
            print("Telegram inicializado")

    def envia_mensagem(self, mensagem, verbose=False):
        url = f"https://api.telegram.org/bot{self.TOKEN}/sendMessage"
        payload = {"chat_id": self.CHAT_ID, "text": mensagem}

        res = requests.post(url, data=payload)

        if res.status_code == 200:
            if verbose:
                print("Mensagem enviada com sucesso!")
        else:
            print("Erro ao enviar:", res.text)

    def envia_resultados(self, resultados, fonte, verbose=False):
        for resultado in reversed(resultados):
            # print(resultado['txcompleto'])

            if resultado["enviada"] == 0:
                if "sefaz" in resultado.keys():
                    uf = resultado["sefaz"].upper()
                else:
                    uf = "NOVOS"

                texto_mensagem = """[{}][{}] {} {}
                """.format(
                    uf,
                    fonte.upper(),
                    resultado["txcompleto"],
                    resultado["url"],
                )

                self.envia_mensagem(texto_mensagem, verbose=verbose)
                self.db.set_envio(resultado["hashid"], fonte=fonte)

                if verbose:
                    print("Mensagem enviada: {}".format(texto_mensagem))
