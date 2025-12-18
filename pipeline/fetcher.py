import pandas as pd
import geopandas as gpd

def load_crimes(path, sheet):
    return pd.read_excel(path, sheet_name=sheet)


def load_population(path):
    xls = pd.ExcelFile(path)
    for sheet in xls.sheet_names:
        if "Estimation" in sheet or "2023" in sheet:
            df = pd.read_excel(xls, sheet_name=sheet, header=None)
            return df
    return pd.DataFrame()

def load_geo(path):
    return gpd.read_file(path)

