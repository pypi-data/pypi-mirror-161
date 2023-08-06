import pandas as pd
import holidays

from datetime import datetime, timedelta
from itertools import product
from dateutil.relativedelta import relativedelta


def impute_dates(
        base_df, impute_cols, date_col, required_col, zero_fill=None,
        limit=7):
    """Completa um dataset com linhas nas datas que faltam

    Args:
        base_df (DataFrame): dataset a ser completado
        impute_cols (list): colunas de agrupamento do dataset resultado
        date_col (str): coluna de data
        required_col (str, optional): coluna necessaria para dropna de todos os valores
        que estiverem acima do limite do ffill. Só funciona quando dropna é True.
        zero_fill (str, optional): coluna a ser completada com zeros. Default: None.
        limit (int, optional): numero de dias limites para completar linhas nulas.
        Default: 7.

    Returns:
        DataFrame: dataset com datas completadas
    """
    base_sets = {}
    for col in impute_cols:
        base_sets[col] = base_df[col].unique()

    min_date = base_df[date_col].min()
    max_date = base_df[date_col].max()
    dates_set = pd.date_range(start=min_date, end=max_date)
    base_sets[date_col] = dates_set

    all_cols = impute_cols + [date_col]
    imputed_df = pd.DataFrame(
        product(*[base_sets[col] for col in all_cols]), columns=all_cols
    )
    imputed_df = imputed_df.merge(base_df, on=all_cols, how="left")
    imputed_df = imputed_df.set_index(all_cols).sort_index()
    if zero_fill:
        imputed_df[zero_fill + "_ZF"] = imputed_df[zero_fill].fillna(0)

    imputed_df = imputed_df.groupby(impute_cols).ffill(limit=limit).reset_index()

    imputed_df = imputed_df.dropna(subset={required_col})
    return imputed_df


def is_last_month(ref_date, last_month=datetime.now()-relativedelta(months=1)):
    """
    Checa se uma data faz parte do mes passado

    Args:
        ref_date (str): data no formato YYYY-MM-DD
        today (datetime): data atual

    Returns:
        bool: True se a data faz parte do mes atual, False caso contrario
    """
    year, month, _ = [int(v) for v in ref_date.split("-")]
    exact_month = year == last_month.year and month == last_month.month
    return exact_month


def is_current_month(ref_date):
    """
    Checa se uma data faz parte do mes atual

    Args:
        ref_date (str): data no formato YYYY-MM-DD

    Returns:
        bool: True se a data faz parte do mes atual, False caso contrario
    """
    year, month, _ = [int(v) for v in ref_date.split("-")]
    today = datetime.today()
    exact_month = year == today.year and month == today.month
    return exact_month


def just_finished_month(ref_date):
    """
    Checa se uma data esta no comeco do mes atual (primeira metade)

    Args:
        ref_date (str): data no formato YYYY-MM-DD

    Returns:
        bool: True se a data faz parte do comeco do mes atual, False caso contrario
    """
    year, month, _ = [int(v) for v in ref_date.split("-")]
    today = datetime.today()
    last_date = today - timedelta(days=15)
    month_beginning = year == last_date.year and month == last_date.month
    return month_beginning


def is_holiday(date):
    """Retorna se a data eh um feriado

    Args:
        date (datetime.date): data a ser testada

    Returns:
        bool: True se a data passada eh feriado
    """
    return date in holidays.Brazil()


def is_weekend(date, include_friday=False):
    """
    Retorna uma resposta se o dia especificado eh fim de semana

    Args:
        date (datetime.date): data a ser testada
        include_friday (bool): True para incluir sexta no teste logico

    Returns:
        bool: True se a data passada esta no final de semana
    """
    if include_friday:
        weekend = [4, 5, 6]
    else:
        weekend = [5, 6]

    return date.weekday() in weekend


def week_to_date_row(week, ref=pd.to_datetime("1989-12-31")):
    """
    Função que retorna a data do primeiro dia da semana
    Para nós, o primeiro dia é sempre domingo

    Args:
       week (str): Entidade com os números da semana
       ref (str): Data referencia de inicio

    Returns:
       str: Data acrescida dos números da semana
    """

    return ref + datetime.timedelta(days=week * 7)


def week_to_date_column(week_column, ref=pd.to_datetime("1989-12-31")):
    """
    Função que retorna série com a data do primeiro dia da semana.
    Para nós, o primeiro dia é sempre domingo

    Args:
       week_column (pd.Series): Coluna com os números da semana
       ref (str): Data referencia de inicio

    Returns:
       pd.Series: Coluna com o primeiro dia da semana
    """
    return pd.to_timedelta(week_column * 7, 'd') + ref

def date_to_components(date, format='%Y-%m-%d'):

    """
    Função que dado uma data retorna ano, mes e dia separados por string e preenchidos com zero a esquerda.
    Args:
        date (str/datetime): Data
        format (str): Formato de data
    Returns:
        ano (str): Ano da data
        mes (str): Mes da data com zero a esquerda
        dia (str): Dia data com zero a esquerda
    """

    date = pd.to_datetime(date, format=format)

    ano = str(date.year)
    mes = str(date.month).zfill(2)
    dia = str(date.day).zfill(2)

    return ano, mes, dia
