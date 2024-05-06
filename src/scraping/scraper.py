import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from utils import helpers

XPATH_NRO_DOC = "//input[@id='txtNroDoc']"
XPATH_TXT_CAPTCHA = "//input[@id='txtCaptcha']"
XPATH_BTN_CONSULTAR = "//input[@id='btnConsultar']"
XPATH_RESULTADO = "//div[@id='divResultado']/descendant::table/tbody"

HEAD = [
    "PERÍODO",
    "TIPO DOCUMENTO",
    "CÓDIGO DOCUMENTO",
    "NOMBRE DE IAFAS",
    "REGIMEN",
    "FECHA DE INICIO",
    "FECHA DE FIN",
    "TIPO DE PLAN DE SALUD",
    "ESTADO",
]


def session(path_driver: str, url: str):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Ejecuta Chrome sin interfaz gráfica.
    # options.add_argument("--no-sandbox") # Útil cuando se ejecuta en un contenedor Docker.
    options.add_argument("--start-maximized")  # Inicia chrome maximizado.
    options.add_argument(
        "--disable-notifications"
    )  # Desactiva las notificaciones del navegador.
    # options.add_argument("--disable-gpu") # Útil en máquina virtual o Docker.
    options.add_argument(
        "--allow-running-insecure-content"
    )  # Permite contenido http en páginas https.
    options.add_argument(
        "user-agent=[user-agent string]"
    )  # Establece un user agent customizado.
    options.add_argument(
        "executable_path=" + path_driver
    )  # Ruta al ejecutable del chromedriver.
    # options.add_argument("--remote-debugging-port=9222") # Establece el puerto para depuración remota.
    # options.add_argument("--page-load-timeout=60") # Tiempo para la carga de la página.
    # options.add_experimental_option("excludeSwitches", ["enable-logging"]) # No imprimir los logs internos de Chrome en la terminal.
    # options.add_experimental_option("detach", True) # Desacopla el proceso de Chrome del hilo de Python. Útil cuando se desean hacer pruebas manuales después de la automatización.
    options.add_experimental_option(
        "useAutomationExtension", False
    )  # Evita la instalación automática de esta extensión. Hace que Chrome sea invisible en sitios que bloquean la automatización. El contra es perder acceso a algunas APIs útiles para automatización.
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.get(url)
    return driver


def run_scraper(
    driver,
    url,
    path_to_save_img,
    period,
    document_type,
    document_code,
    max_attempt=15,
):
    attempt = 1
    while attempt <= max_attempt:
        try:
            driver.get(url)
            time.sleep(1)

            if any(
                [
                    not helpers.path_exist(driver, XPATH_NRO_DOC),
                    not helpers.path_exist(driver, XPATH_TXT_CAPTCHA),
                    not helpers.path_exist(driver, XPATH_BTN_CONSULTAR),
                    not helpers.screenshop(driver, path_to_save_img),
                ]
            ):
                continue

            txt_captcha = helpers.get_txt_captcha(path_to_save_img)

            if txt_captcha:
                new_document_code = document_code
                if document_type == "RUC":
                    new_document_code = new_document_code[2:10]

                search = helpers.buscador(
                    driver,
                    XPATH_NRO_DOC,
                    new_document_code,
                    XPATH_TXT_CAPTCHA,
                    txt_captcha,
                    XPATH_BTN_CONSULTAR,
                    XPATH_RESULTADO,
                )

                if search:
                    return helpers.get_content_by_rows(
                        driver, XPATH_RESULTADO, document_code, document_type, period
                    )
        except Exception as e:
            print(f"Error: {e}")
        finally:
            attempt += 1
    return pd.DataFrame()
