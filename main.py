from scraping import scraper
from tqdm import tqdm
from constantes.configuracion import (
    FILES,
    DRIVER_PATH,
    URL,
    PATH_TO_SAVE_IMG,
    PATH_TO_SAVE_EXCEL,
    PATH_TO_INPUT_FILES
)

import pandas as pd


def read_csv(files):
    return pd.concat(
        [
            pd.read_csv(
                PATH_TO_INPUT_FILES + "{}.csv".format(f),
                sep="|",
                header=0,
                dtype={"COD_DOCUM": str},
                encoding="latin1",
            )
            for f in files
        ],
        ignore_index=True,
    )


if __name__ == "__main__":

    # customers = read_csv(FILES)
    customers = pd.read_csv(
        filepath_or_buffer="data/clean/202402_clientes_2.csv",
        sep="|",
        header=0,
        dtype={"COD_DOCUM": str},
        encoding="latin1"
    )

    driver = scraper.session(DRIVER_PATH, URL)
    output = pd.DataFrame(columns=scraper.HEAD)

    for idx, row in tqdm(
            customers.iterrows(), total=len(customers), desc="Processing Scraping"
    ):
        #period = row["PERIODO"]
        period = "202402"
        document_type = row["TIP_DOCUM"]
        document_code = row["COD_DOCUM"]

        if document_type == "DNI" or (
                document_type == "RUC" and str(document_code).startswith("10")
        ):
            content = scraper.run_scraper(
                driver, URL, PATH_TO_SAVE_IMG, period, document_type, document_code
            )
            if not content.empty:
                output = pd.concat([output, content])

    output.to_excel(PATH_TO_SAVE_EXCEL, index=False)

    driver.close()
    driver.quit()
