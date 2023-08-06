import logging
import numpy as np
import pandas as pd
import re

from ipp_ds.io import io
from ipp_ds.data_cleaning.dates_holidays import is_current_month, just_finished_month
from ipp_ds.data_cleaning.path import get_date_from_names
from ipp_ds.data_cleaning.parallelism import applyParallel

logger = logging.getLogger(__name__)


def should_reprocess_date(ref_date):
    """
    Checa se uma data deve ser reprocessada, mesmo se ja existir o arquivo de output

    Args:
        ref_date (str): data para ser checada

    Returns:
        bool: True se a data deve ser reprocessada, False caso contrario
    """

    return is_current_month(ref_date) or just_finished_month(ref_date)


def should_run(output_uri, reprocess_date=None, date="2000-01-01", min_date="1999-01-01"):
    """
    Checa se deve processar um output

    Args:
        output_uri (str): path do output a ser criado
        reprocess_date (str): data de reprocessamento.
        date (str, optional): Data de referencia do output a ser criado.
        Defaults to "2000-01-01".
        min_date (str, optional): Data minima para um output ser criado.
        Defaults to "1999-01-01".

    Returns:
        bool: True se o arquivo deve ser processado, False caso contrario
    """
    # checa o reprocessamento forcado
    if reprocess_date is not None and date >= reprocess_date:
        return True
    # checa se a data esta no mes atual ou final do mes passado
    elif should_reprocess_date(date):
        return True
    # checa se o output ja foi calculado
    elif io.file_exists(output_uri):
        logger.debug("Already calculated output: {}".format(output_uri))
        return False
    # checa se a data eh maior que a data minima de processamento
    elif date < min_date:
        return False
    return True


def load_history(
    glob, initial_date='2019-01-01', sep="-", _format='parquet', columns=None, occ = -1
):
    """Le o dataset de cada mes entre a data inicial e hj e junta em um unico arquivo

    Args:
        initial_date (str): Data minima para estar no output. Default: None
        ext (str): Tipo de extensao do arquivo. Default: parquet
    """

    all_files = np.array(io.glob(glob))
    all_dates = get_date_from_names(all_files, sep=sep, occ = occ)

    index = all_dates >= initial_date
    files_to_load = all_files[index]

    if _format == 'parquet':
        all_df = pd.concat(
            [io.read_parquet(f, columns=columns) for f in files_to_load],
            sort=True,
        )
    elif _format == 'csv':
        all_df = pd.concat(
            [io.read_csv(f, sep=';', decimal=',') for f in files_to_load],
            sort=True,
        )
    else:
        all_df = pd.concat([io.read_excel(f) for f in files_to_load], sort=True)
    return all_df


def read_whole_path(uri, columns=None):
    """ Le todos os arquivos de um path """
    final_df = pd.DataFrame()
    for i in io.glob(uri):
        df = io.read_parquet(i, columns=columns)
        final_df = final_df.append(df)

    return final_df


def load_last_file(glob, _format='parquet'):
    """Le o ultimo arquivo de um historico de arquivos

    Args:
        glob (str): path
        ext (str): Tipo de extensao do arquivo. Default: .parquet
    """
    file_to_load = io.glob(glob)[-1]

    if _format == 'parquet':
        df = io.read_parquet(file_to_load)
    elif _format == 'csv':
        df = io.read_csv(file_to_load, sep=';', decimal=',')
    else:
        df = io.read_excel(file_to_load)
    return df


def extract_file(x,
                 file_format,
                 verbose=0,
                 file_func=lambda x: x,
                 keep_origin_col=False,
                 errors = 'raise',
                 mode = 'read',
                 **kwargs):

    if verbose > 0:
        if mode == 'read':
            print(f"Reading {x['directory'].values[0]}")
        if mode == 'rename':
            print(f"Renaming {x['directory'].values[0]}")

    if mode == 'read':
        dict = {'parquet': io.read_parquet, 'excel': io.read_excel, 'csv': io.read_csv}

    if mode == 'rename':
        dict = {form: io.rename_file for form in ['parquet','excel','csv']}

    if file_format in list(dict.keys()):

        func = dict[file_format]

        try:
            df = func(x['directory'].values[0], **kwargs)

            if keep_origin_col:
                df['origin'] = x['directory'].values[0]

            df = file_func(df)
        
        except Exception as e:
            if errors == 'raise':
                raise e
            if errors == 'ignore':
                return pd.DataFrame()

    else:
        try:
            df = file_func(x['directory'].values[0], **kwargs)

        except Exception as e:
            if errors == 'raise':
                raise e
            if errors == 'ignore':
                return pd.DataFrame()

    return df


def datalake_walk(base_folder,
                  file_format,
                  min_date='1900-01-01',
                  last_layer='folder',
                  max_date='2099-12-31',
                  verbose=0,
                  n_jobs=-1,
                  file_func = lambda x: x,
                  date_sep = '-',
                  occ = -1,
                  keep_origin_col = False,
                  errors = 'raise',
                  mode = 'read',
                  **kwargs):

    """
    Função que permite navegar de forma recursiva dentro de um sistema de pastas dividido em anos, meses e dias
    e concatena os arquivos navegados.
    Ele permite implementação de lógica incremental a partir do parâmetro min_date.

    Args:
        base_folder (str): Diretório raiz que contem os anos, meses e dias
        min_date (str): Data mínima desejada
        file_format (str): Tipo de arquivo a ser lido na pasta. Pode ser parquet, csv ou excel.
        last_layer (str): Ultima camada de pastas. Pode ser year, month ou day.
        max_date (str): Data máxima desejada
        verbose (int): Nivel de verbosidade do codigo. Acima de zero, printa entradas nas pastas
        n_jobs (int): Numero de jobs maximo a ser usado na paralelização da leitura
        file_func (func): Função a ser aplicada no momento da leitura
        date_sep (str): Separador de data em pastas com arquivos com datas no nome
        occ (int): Ocorrencia do split que a data se encontra em caso de folder
        keep_origin_col (bool): Para manter ou não o nome da coluna de diretorio de origem do dataset
        errors (str): Pode ser 'raise' (quebra codigo quando da erro) ou 'ignore' (segue com dataframe vazio)
        mode (str): Modo de leitura. Pode ser 'read' para ler o arquivo ou 'rename' para renomear o arquivo
        **kwargs: Argumentos a serem passados na read_any (ex: sep do read_csv)

    Returns:
        pd.DataFrame: DataFrame concatenado final com todos os arquivos que foram navegados

    """
    min_date = pd.to_datetime(min_date)
    max_date = pd.to_datetime(max_date)

    extension = file_format if file_format != 'excel' else 'xls'

    list_folders = [col for col in io.glob(base_folder) if f'.{extension}' in col]

    start = -2
    date_format = '%Y'

    if last_layer == 'day':
        start = -4
        date_format = '%Y/%m/%d'
    if last_layer == 'month':
        start = -3
        date_format = '%Y/%m'

    df_folders = pd.DataFrame(list_folders,columns=['directory'])
    df_folders['file_name'] = df_folders['directory'].str.split('/').str.get(-1)

    if last_layer != 'folder':
        df_folders['date'] = pd.to_datetime(df_folders['directory'].str.split('/').str.slice(start=start, stop=-1).str.join('/'), format=date_format)
        df_folders = df_folders.loc[df_folders['date'].between(min_date, max_date)]

    else:
        try:
            df_folders['date'] = get_date_from_names(df_folders['directory'], sep=date_sep, occ=occ)
            df_folders = df_folders.loc[df_folders['date'].between(min_date, max_date)]
        except:
            pass
    
    df = None

    if len(df_folders) == 1:
        df = extract_file(df_folders, file_format=file_format,
                          verbose=verbose, file_func=file_func, keep_origin_col=keep_origin_col, 
                          errors=errors, mode=mode, **kwargs)
    if len(df_folders) > 1:
        df = applyParallel(df_folders.groupby(['directory']), extract_file, keep_origin_col=keep_origin_col,
                           file_format=file_format, file_func=file_func, verbose=verbose, errors=errors,
                           n_jobs=n_jobs, mode=mode, **kwargs).reset_index(drop=True)

    return df


def datalake_get_last(base_folder,
                      file_format,
                      min_date='1900-01-01',
                      last_layer='folder',
                      max_date='2099-12-31',
                      verbose=0,
                      file_func = lambda x: x,
                      date_sep = '-',
                      occ=-1,
                      keep_origin_col = False,
                      n_jobs=-1,
                      errors='raise',
                      mode='read',
                      **kwargs
):

    """
    Função que permite navegar de forma recursiva dentro de um sistema de pastas e pega ultimo arquivo.
    Ele permite implementação de lógica incremental a partir do parâmetro min_date.

    Args:
        base_folder (str): Diretório raiz que contem os anos, meses e dias
        min_date (str): Data mínima desejada
        file_format (str): Tipo de arquivo a ser lido na pasta. Pode ser parquet, csv ou excel.
        last_layer (str): Ultima camada de pastas. Pode ser year, month ou day.
        max_date (str): Data máxima desejada
        verbose (int): Nivel de verbosidade do codigo. Acima de zero, printa entradas nas pastas
        file_func (func): Função a ser aplicada no momento da leitura
        date_sep (str): Separador de data em pastas com arquivos com datas no nome
        occ (int): Ocorrencia do split que a data se encontra em caso de folder
        n_jobs (int): Numero de jobs maximo a ser usado na paralelização da leitura
        keep_origin_col (bool): Para manter ou não o nome da coluna de diretorio de origem do dataset
        errors (str): Pode ser 'raise' (quebra codigo quando da erro) ou 'ignore' (segue com dataframe vazio)
        mode (str): Modo de leitura. Pode ser 'read' para ler o arquivo ou 'rename' para renomear o arquivo
        **kwargs: Argumentos a serem passados na read_any (ex: sep do read_csv)

    Returns:
        pd.DataFrame: DataFrame concatenado final com todos os arquivos que foram navegados

    """

    min_date = pd.to_datetime(min_date)
    max_date = pd.to_datetime(max_date)

    partition_cols = io.get_partition_cols(uri=base_folder)
    mod_base_folder = base_folder

    regex = re.compile('\(|\{')
    group_indexes = [ind for ind, i in enumerate(mod_base_folder.split('/')) if regex.match(i) is not None]

    for col in partition_cols:
        mod_base_folder = mod_base_folder.replace('{'+col+'}','*')
    
    extension = file_format if file_format != 'excel' else 'xls'
    
    list_folders = [col for col in io.glob(mod_base_folder) if f'.{extension}' in col]
    
    start = -2
    date_format = '%Y'

    if last_layer == 'day':
        start = -4
        date_format = '%Y/%m/%d'
    if last_layer == 'month':
        start = -3
        date_format = '%Y/%m'

    df_folders = pd.DataFrame(list_folders, columns=['directory'])
    df_folders['file_name'] = df_folders['directory'].str.split('/').str.get(-1)

    if last_layer != 'folder':
        df_folders['date'] = pd.to_datetime(
            df_folders['directory'].str.split('/').str.slice(start=start, stop=-1).str.join('/'),
            format=date_format
        )
        df_folders = df_folders.loc[df_folders['date'].between(min_date, max_date)]

    else:
        try:
            df_folders['date'] = get_date_from_names(df_folders['directory'], sep=date_sep, occ=occ)
            df_folders = df_folders.loc[df_folders['date'].between(min_date, max_date)]
        except:
            pass
    
    df_folders[f'group_base'] = 1
    
    for col in group_indexes:
        df_folders[f'group_{col}'] = df_folders['directory'].str.split('/').str.get(col)
    
    key = ['group_base'] + [f'group_{col}' for col in group_indexes]

    df_folders = df_folders.sort_values('directory')
    df_folders = df_folders.groupby(key, as_index=False).tail(1)

    df = None

    if len(df_folders) == 1:

        df = extract_file(df_folders, file_format=file_format,mode=mode,
                          verbose=verbose, file_func=file_func, keep_origin_col=keep_origin_col,
                          errors=errors, **kwargs)
    
    if len(df_folders) > 1:
        df = applyParallel(df_folders.groupby(['directory']), extract_file, keep_origin_col=keep_origin_col,
                           file_format=file_format, file_func=file_func, verbose=verbose, errors=errors,
                           mode=mode, n_jobs=n_jobs, **kwargs).reset_index(drop=True)

    return df