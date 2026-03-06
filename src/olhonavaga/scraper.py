import os
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from .browser import get_uc_driver
from .parser import RankingParser as rp


class OlhoNaVaga:
    """Entra na pagina do ranking"""

    RANKINGS = {
        "sefaz-pi": {"link": "https://olhonavaga.com.br/rankings/ranking?id=80578"},
        "sefaz-pr": {"link": "https://olhonavaga.com.br/rankings/ranking?id=79110"},
        "sefaz-pe": {"link": "https://olhonavaga.com.br/rankings/ranking?id=49551"},
        "sefaz-mg": {"link": "https://olhonavaga.com.br/rankings/ranking?id=47050"},
        "sefaz-mt": {"link": "https://olhonavaga.com.br/rankings/ranking?id=52584"},
        "sefaz-sp": {"link": "https://olhonavaga.com.br/rankings/ranking?id=86896"},
    }

    def __init__(self, headless=False):
        self.driver, self.wait = get_uc_driver(headless)

    def login(self, email, password):
        """Acessa a página e realiza o login."""
        self.driver.get("https://olhonavaga.com.br/login")
        self.driver.maximize_window()

        # Exemplo de seletores (ajuste conforme o site real)
        self.wait.until(
            EC.presence_of_element_located((By.NAME, "form:email"))
        ).send_keys(email)
        self.driver.find_element(By.NAME, "form:password").send_keys(password)

        # self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print("Login executado.")

    def select_rank(self, rank):
        self.rank = rank
        self.rank_link = self.RANKINGS[rank]["link"]

        self.driver.get(self.rank_link)

        # Espera resposta
        self.wait_load()

        # Cria a ação de pressionar e soltar a tecla ESC
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

        # Obtem informações de navegação
        self.num_insert, self.current_page, self.num_pages = rp.page_info(self)

        print("Ranking Selecionado")

    # Funções Navegação
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(Exception),
    )
    def page_action(self, tp_navegacao):
        div_paginador = self.driver.find_element(
            By.XPATH, '//div[@id="form:tabView:dataTable0_paginator_top"]'
        )

        div_paginador.find_element(
            By.XPATH, './/a[contains(@class, "ui-paginator-' + tp_navegacao + '")]'
        ).click()

        print("Navegação do tipo: " + tp_navegacao)

    # Tenta 5 vezes, esperando 2 segundos entre elas,
    # se ocorrer qualquer erro (como elementos não encontrados)
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(Exception),
    )
    def get_ranking_page(self):
        return rp.parse_page(self)

    def get_ranking_pages(self, read_pages=None):
        if read_pages is None:
            read_pages = self.num_pages

        # Começa da primeira pagina
        if self.current_page != 1:
            self.page_action("first")
            self.wait_load()

        # Atualiza a pagina corrent
        # self.num_insert, self.current_page, self.num_pages = self.page_info()

        print(
            "Fisco: {} Inserções: {} Pagina: {}/{}".format(
                self.rank.upper(), self.num_insert, self.current_page, self.num_pages
            )
        )

        lista_pontos = []
        lista_acertos = []
        lista_erros = []
        lista_brancos = []
        lista_percentual = []

        for i in range(1, read_pages + 1):
            print("Pagina {}/{}".format(self.current_page, read_pages))

            l_pontos, l_acertos, l_erros, l_brancos, l_percentual = (
                self.get_ranking_page()
            )

            lista_pontos = lista_pontos + l_pontos
            lista_acertos = lista_acertos + l_acertos
            lista_erros = lista_erros + l_erros
            lista_brancos = lista_brancos + l_brancos
            lista_percentual = lista_percentual + l_percentual

            print("")

            if self.current_page != read_pages:
                self.page_action("next")
                self.wait_load()

                self.num_insert, self.current_page, self.num_pages = rp.page_info(self)
                print(self.num_insert, self.current_page, self.num_pages)
                # self.num_insert, self.current_page, self.num_pages = self.page_info()
            else:
                print("Fim do loop")
                break

        # Transforma DataFrames
        self.df_pontos = pd.DataFrame(lista_pontos, dtype="string")
        self.df_acertos = pd.DataFrame(lista_acertos, dtype="string")
        self.df_erros = pd.DataFrame(lista_erros, dtype="string")
        self.df_brancos = pd.DataFrame(lista_brancos, dtype="string")
        self.df_percentual = pd.DataFrame(lista_percentual, dtype="string")

    def save(self, path_data=None):
        # Constroi pasta destino
        string_data = datetime.now().strftime("%Y-%m-%d")
        string_hora = datetime.now().strftime("%H-%M")

        if path_data is None:
            path_data = Path("../../data/") / self.rank / string_data
        else:
            path_data = Path(path_data) / self.rank / string_data

        print("Cria diretorio data: {}".format(path_data))
        os.makedirs(path_data, exist_ok=True)

        self.df_pontos.to_parquet(
            path_data / "df_pontos_{}_{}.parquet".format(string_data, string_hora),
            compression="snappy",
        )
        self.df_acertos.to_parquet(
            path_data / "df_acertos_{}_{}.parquet".format(string_data, string_hora),
            compression="snappy",
        )
        self.df_erros.to_parquet(
            path_data / "df_erros_{}_{}.parquet".format(string_data, string_hora),
            compression="snappy",
        )
        self.df_brancos.to_parquet(
            path_data / "df_brancos_{}_{}.parquet".format(string_data, string_hora),
            compression="snappy",
        )
        self.df_percentual.to_parquet(
            path_data / "df_percentual_{}_{}.parquet".format(string_data, string_hora),
            compression="snappy",
        )

    # Espera resposta
    def wait_load(self, timeout=20):
        last_count = -1
        start_time = time.time()
        retry_timeout = 0.5

        # Pode ser parametro da função
        selector = "table tr"

        while True:
            page_state = self.driver.execute_script("return document.readyState;")
            if page_state == "complete":
                break
            time.sleep(retry_timeout)

        while time.time() - start_time < timeout:
            current_count = len(self.driver.find_elements(By.CSS_SELECTOR, selector))
            if current_count > 0 and current_count == last_count:
                print(
                    "Pagina Estabilizada. [readyState]: {} [count elements]: {}".format(
                        page_state, current_count
                    )
                )
                return True  # O número de elementos estabilizou
            last_count = current_count
            time.sleep(retry_timeout)

        print("Ocorreu Timeout e os elementos não estabilizaram.")

        return False

    # Conclusão
    def fechar(self):
        """Encerra o navegador."""
        self.driver.quit()
        print("Sessão encerrada.")
