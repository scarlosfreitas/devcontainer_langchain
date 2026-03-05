from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class RankingParser:
    @staticmethod
    def page_info(olhonavaga):
        div_paginador = olhonavaga.driver.find_element(
            By.XPATH, '//div[@id="form:tabView:dataTable0_paginator_top"]'
        )

        num_insert = int(
            div_paginador.find_element(
                By.XPATH, './/span[@class="ui-paginator-current"]'
            )
            .text.split()[0]
            .replace(".", "")
        )
        num_pages = num_insert // 50 + 1
        current_page = int(
            div_paginador.find_element(
                By.XPATH, './/a[contains(@class,"ui-state-active")]'
            ).text
        )

        return num_insert, current_page, num_pages

    @staticmethod
    def thead(olhonavaga):
        e_thead = olhonavaga.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//thead[@id="form:tabView:dataTable0_head"]')
            )
        )

        return e_thead

    @staticmethod
    def tbody(olhonavaga):
        e_thead = olhonavaga.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//tbody[@id="form:tabView:dataTable0_data"]')
            )
        )
        return e_thead

    @staticmethod
    def lines(e_tbody):
        e_lines = e_tbody.find_elements(By.XPATH, ".//tr[@data-ri]")

        return e_lines

    @staticmethod
    def cols(e_line):
        e_cols = e_line.find_elements(By.TAG_NAME, "td")

        return e_cols

    @staticmethod
    def parse_row(e_line, col_names):
        # Pega todas as células da linha
        e_cols = RankingParser.cols(e_line)

        if not e_cols:
            # Pula se for a linha do cabeçalho (que pode ter <th>)
            return None, None, None, None, None

        # Cria dicionario para cada tipo de informação
        registro = {
            "posicao": e_cols[0].text,
            "usuario": e_cols[1].text,
        }
        registro_pontos = registro.copy()
        registro_acertos = registro.copy()
        registro_erros = registro.copy()
        registro_brancos = registro.copy()
        registro_percentual = registro.copy()

        n_cols = len(col_names) - 2

        for n_col in range(n_cols):
            col_name = col_names[n_col + 2]

            lista_valores = e_cols[n_col + 2].text.replace("|", "").split()

            # Valores normais de disciplina sem brancos
            if len(lista_valores) >= 4:
                pontos, acertos, erros = lista_valores[0:3]
                percentual = lista_valores[-1]

            # Valores normais de disciplina com brancos
            if len(lista_valores) > 4:
                brancos = lista_valores[-2]
            else:
                brancos = 0

            # Valores normais de disciplina com brancos
            if len(lista_valores) == 0:
                pontos = 0
                percentual = "0%"
            elif len(lista_valores) < 4:
                pontos = lista_valores[0]
                percentual = lista_valores[-1]

            # Dicionários
            registro_pontos[col_name] = pontos
            registro_percentual[col_name] = percentual

            if len(lista_valores) >= 4:
                registro_acertos[col_name] = acertos
                registro_erros[col_name] = erros
                registro_brancos[col_name] = brancos

        return (
            registro_pontos,
            registro_percentual,
            registro_acertos,
            registro_erros,
            registro_brancos,
        )

    @staticmethod
    def parse_page(olhonavaga):
        # thead_usuario = driver.find_elements(By.XPATH, '//thead[@id="form:dataUser_head"]')
        # tbody_usuario = driver.find_elements(By.XPATH, '//tbody[@id="form:dataUser_data"]')

        e_hbody = RankingParser.thead(olhonavaga)
        e_tbody = RankingParser.tbody(olhonavaga)

        # Seleciona linhas
        col_names = RankingParser.get_col_names(
            e_hbody.find_elements(By.TAG_NAME, "th")
        )
        e_lines = RankingParser.lines(e_tbody)
        print("Quantidade de linhas:", len(e_lines), end="")

        lista_pontos = []
        lista_acertos = []
        lista_erros = []
        lista_brancos = []
        lista_percentual = []

        for e_line in e_lines:
            pontos, acertos, erros, brancos, percentual = RankingParser.parse_row(
                e_line, col_names
            )

            if pontos is None:
                # Pula se for a linha do cabeçalho (que pode ter <th>)
                continue
            else:
                lista_pontos.append(pontos)
                lista_acertos.append(acertos)
                lista_erros.append(erros)
                lista_brancos.append(brancos)
                lista_percentual.append(percentual)

            print(".", end="")

        return lista_pontos, lista_acertos, lista_erros, lista_brancos, lista_percentual

    def get_col_names(element_th):
        col_names = []
        for coluna in element_th:
            texto = coluna.text.replace(".", "")

            if texto == "#":
                texto = "posicao"

            if texto != "":
                col_names.append(texto)

        # trata colunas com nomes repetido
        for coluna in col_names:
            indices_repetido = [i for i, c in enumerate(col_names) if c == coluna]
            if len(indices_repetido) > 1:
                for i in range(len(indices_repetido)):
                    col_names[indices_repetido[i]] = (
                        col_names[indices_repetido[i]] + "_" + str(i + 1)
                    )

        # len(col_names)
        return col_names
