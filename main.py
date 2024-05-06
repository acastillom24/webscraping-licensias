"""Module providing a function to create pandas dataframe."""

import pandas as pd

from src import DRIVER_PATH, URL, run_scraper, session

# from tqdm import tqdm


PATH_TO_SAVE_IMG = r"./output/captcha.jpg"
licencias_df = pd.DataFrame(columns={"TIPO DOCUMENTO": str, "COD DOCUMENTO": str})
driver = session(DRIVER_PATH, URL)

if __name__ == "__main__":
    type_docum = "DNI"
    cod_docum = ""

    if type_docum == "DNI" or (type_docum == "RUC" and cod_docum.startswith("10")):
        if content := run_scraper(driver, URL, PATH_TO_SAVE_IMG, type_docum, cod_docum):
            licencias_df = pd.concat([licencias_df, content])

    licencias_df.to_csv("./output/licencias.csv", sep="|", index=False)

    driver.close()
    driver.quit()
