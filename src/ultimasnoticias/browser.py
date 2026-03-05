import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait


def get_uc_driver(headless=False):
    """Inicia a sessão do navegador ao instanciar a classe."""
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless")

    options.add_argument("--no-sandbox")  # Permite rodar como root/container
    options.add_argument(
        "--disable-dev-shm-usage"
    )  # Evita crash por falta de memória RAM compartilhada
    options.add_argument(
        "--disable-gpu"
    )  # Opcional: economiza recursos em servidores sem placa de vídeo

    print("Sessão iniciada com sucesso.")
    driver = uc.Chrome(options=options, version_main=145)
    wait = WebDriverWait(driver, 10)
    return driver, wait
