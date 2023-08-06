import unicodedata


def strip_accents(text):
    """
    Função que devolve um texto sem acentos

    Args:
        text (str): texto com acento

    Returns:
        str: texto sem acento
    """
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def type_conversion(df, old_types="float64", new_type="float32"):
    """
    Função que converte todas as colunas de um tipo para outro

    Args:
      df(pd.Dataframe): Dataset de entrada
      old_type (datatype): tipo do dado de entrada
      new_type (datatype): tipo do dado de saida

    Returns:
      df(pd.Dataframe): Dataset com tipos modificados
    """
    cols = df.select_dtypes(old_types).columns
    df.loc[:, cols] = df.loc[:, cols].astype(new_type)
    return df
