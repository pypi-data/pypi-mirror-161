import pandas as pd

from itertools import product
from ipp_ds.variables.geo import UF_TO_REGIAO


def generate_all_odds(df, impute_cols):
    """
    Gera um dataset com todas as combinacoes possiveis para as chaves passadas
        Args:
            df (pd.DataFrame): dataframe a ser submetido ao processo
            impute_cols (list): lista de colunas a ter todos os valores possiveis gerados

        Returns:
            imputed_df (pd.DataFrame): dataset contendo todas as combinacoes possiveis de chave
    """
    base_sets = {}
    for col in impute_cols:
        base_sets[col] = df[col].unique()

    imputed_df = pd.DataFrame(
        product(*[base_sets[col] for col in impute_cols]), columns=impute_cols
    )

    return imputed_df


def add_col_suffix(df, suffix):
    """
    Função que adiciona sufixo ao final de todas as colunas em um DataFrame

    Args:
      df(pd.Dataframe): Dataset de entrada
      suffix (str): Sufixo a ser acrescido ao final

    Returns:
      df(pd.Dataframe): Dataset com colunas modificadas 
    """
    df.columns = df.columns + suffix
    return df


def add_regiao_column(df, uf_column="UF"):
    """
    Função que cria coluna com valores de REGIAO
    e MACRORREGIAO a partir da coluna de UF

    Args:
      df(pd.Dataframe): Dataset de entrada
      uf_column(str): Coluna de UF

    Returns:
      df(pd.Dataframe): Dataset com as colunas de REGIAO e MACRORREGIAO
    """
    df["REGIAO"] = df[uf_column].map(UF_TO_REGIAO)
    return df
