import os
import numpy as np
import pandas as pd
import cv2
import re
import pytesseract
import time

from PIL import Image
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    UnexpectedAlertPresentException
)
from constantes.configuracion import PATH_PYTESSERACT, tessdata_dir_config

pytesseract.pytesseract.tesseract_cmd = PATH_PYTESSERACT

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


def get_txt_captcha(path, scale=150):

    if os.path.exists(path):
        image = Image.open(path).convert("RGB")
        os.remove(path)
        image_array = np.array(image)
        image_array = image_array[:, :, ::-1].copy()
        image_array = cv2.bitwise_not(image_array)

        # Cambiar el tamaño a 150%
        width = int(image_array.shape[1] * scale / 100)
        height = int(image_array.shape[0] * scale / 100)
        dim = (width, height)
        image_array = cv2.resize(image_array, dim, interpolation=cv2.INTER_AREA)

        # Convertir a blanco y negro
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(image_array, 127, 255, cv2.THRESH_BINARY)
        txt = pytesseract.image_to_string(thresh, config=tessdata_dir_config)
        txt = re.sub(r"[^a-zA-Z0-9]", "", txt)
        if len(txt) > 1:
            return txt
    return None


def screenshop(driver, path_to_save, ubicacion=(57.5, 310, 175, 355)):
    try:
        driver.save_screenshot(path_to_save)
        img = Image.open(path_to_save)
        img = img.crop(ubicacion)
        img.save(path_to_save)
        return True
    except UnexpectedAlertPresentException:
        return False
    except Exception as e:
        print(f"Error: {e}", end="\n")
        return False


def path_exist(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
        return True
    except NoSuchElementException:
        return False


def buscador(
    driver,
    xpath_nro_documento,
    cod_documento,
    xpath_txt_captcha,
    txt_captcha,
    xpath_btn_consultar,
    xpath_resultado,
):
    try:
        driver.find_element(By.XPATH, xpath_nro_documento).send_keys(cod_documento)
        driver.find_element(By.XPATH, xpath_txt_captcha).send_keys(txt_captcha)
        driver.find_element(By.XPATH, xpath_btn_consultar).click()
        time.sleep(2)
        if path_exist(driver, xpath_resultado):
            return True
        return False
    except UnexpectedAlertPresentException:
        return False
    except Exception as e:
        print(f"Error: {e}", end="\n")
        return False


def get_content_by_rows(
    driver, xpath_resultado, cod_documento, tipo_documento, periodo
):
    try:
        content = []
        tabla_elemento = driver.find_element(By.XPATH, xpath_resultado)
        filas = tabla_elemento.find_elements(By.TAG_NAME, "tr")
        for idx, fila in enumerate(filas):
            if idx > 0:
                tds = fila.find_elements(By.TAG_NAME, "td")
                th = fila.find_element(By.TAG_NAME, "th").text
                datos_fila = [td.text for td in tds]
                datos_fila.insert(0, th)
                datos_fila.insert(0, cod_documento)
                datos_fila.insert(0, tipo_documento)
                datos_fila.insert(0, periodo)
                content.append(datos_fila)

        return pd.DataFrame(content, columns=HEAD)
    except Exception as e:
        print(f"Error: {e}", end=" ")
        return pd.DataFrame(columns=HEAD)

