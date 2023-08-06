import tempfile
from functools import partial
from pyarrow.parquet import read_schema
from pyarrow.parquet import read_table as pa_read_table
from io import BytesIO, StringIO
from urllib.request import urlretrieve
from pptx import Presentation
from thinkcell import Thinkcell
import json
import pandas as pd
import numpy as np
import re
import gc
import os
from typing import Union

from azure.storage.filedatalake import DataLakeServiceClient, DataLakeFileClient
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.identity import DefaultAzureCredential

import logging

from ..data_cleaning.parallelism import applyParallel
from .io_utils import *

# Set the logging level for all azure-* libraries
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

import warnings
warnings.filterwarnings('ignore')

DEFAULT_CREDENTIAL_KWARGS = json.loads(os.getenv('DEFAULT_CREDENTIAL_KWARGS','{}'))
DEFAULT_SERVICE_KWARGS = json.loads(os.getenv('DEFAULT_SERVICE_KWARGS','{}'))
DEFAULT_CONN_KWARGS = json.loads(os.getenv('DEFAULT_CONN_KWARGS','{}'))
DEFAULT_GLOB_CONN_KWARGS = json.loads(os.getenv('DEFAULT_GLOB_CONN_KWARGS','{}'))
DEFAULT_BLOB_SERVICE = os.getenv('DEFAULT_BLOB_SERVICE','gen2')
DEFAULT_UPLOAD_MODE = os.getenv('DEFAULT_UPLOAD_MODE','full')
DEFAULT_NUM_THREADS = os.getenv('DEFAULT_NUM_THREADS',-1)

def create_blob_service(uri, conn_type=DEFAULT_BLOB_SERVICE,
                        service_kwargs=DEFAULT_SERVICE_KWARGS,
                        credential_kwargs=DEFAULT_CREDENTIAL_KWARGS):
    
    """
    Funçao que cria o serviço de conexão a um determinado storage account
    Args:
        uri (str): Url com endereço de uma pasta em um storage account
        conn_type (str): String com serviço de conexão a Azure. Pode ser blob ou gen2.
        service_kwargs (dict): Dicionário com parametros de conexão ao serviço da Azure.
    Returns:
        object: DataLakeServiceClient (gen2)/BlobServiceClient (blob), dependendo do conn_type
    """

    credential = DefaultAzureCredential(**credential_kwargs)

    account_name = uri.replace('abfs://','').split('.')[0]

    if conn_type == 'gen2':
        dlService = DataLakeServiceClient(account_url=f"https://{account_name}.dfs.core.windows.net",
                                          credential = credential,
                                          **service_kwargs)

    if conn_type == 'blob':
        dlService = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net",
                                      credential = credential,
                                      **service_kwargs)

    return dlService

def rename_file(uri_old, uri_new, conn_type=DEFAULT_BLOB_SERVICE):

    """
    Função que renomeia um arquivo na Azure.
    Args:
        uri_old (str): Url do arquivo com nome antigo
        uri_new (str): Url do arquivo com nome novo
        conn_type (str): String com serviço de conexão a Azure. Pode ser blob ou gen2.
    """

    service_client = create_blob_service(uri=uri_old, conn_type=conn_type)
    container_name = uri_old.split('/')[3]
    old_name = '/'.join(uri_old.split('/')[4:])
    new_name = '/'.join(uri_new.split('/')[4:])

    try:

        if conn_type == 'gen2':
            file_system_client = service_client.get_file_system_client(file_system=container_name)
            file_client = file_system_client.get_file_client(file_path=old_name)

        if conn_type == 'blob':
            file_client = service_client.get_blob_client(container=container_name, blob=old_name)
        
        file_client.rename_file(new_name)
    
    finally:

        file_client.close()
        del file_client

        if conn_type == 'gen2':
            file_system_client.close()
            del file_system_client

        service_client.close()
        del service_client

        gc.collect()

def upload_chunks(file_client: Union[DataLakeFileClient,BlobClient],
                  data: Union[BytesIO,StringIO],  
                  **upload_kwargs):

    """
    Função genérica de upload de arquivo em chunks na Azure.

    Args:
        file_client (Union[DataLakeFileClient,BlobClient]): Cliente de arquivo da azure.
        data (Union[BytesIO,StringIO]): Stream de dados a serem subidos
        **upload_kwargs: Argumentos a serem passados para a upload_data/upload_blob. 
                        Ver DataLakeFileClient.upload_data ou BlobFileClient/upload_blob para mais detalhes

    """

    assert 'chunk_size' in upload_kwargs, "You must pass chunk_size if using upload_mode=chunks"

    if 'chunk_size' in upload_kwargs:
        chunk_size = upload_kwargs.pop('chunk_size')
    
    upload_kwargs.pop('overwrite')
    
    if isinstance(file_client, BlobClient):
        file_client.create_append_blob()

    if isinstance(file_client, DataLakeFileClient):
        file_client.create_file()
        
    while True:

        read_data = data.read(chunk_size)

        if not read_data:
            break
            
        if isinstance(data, StringIO):
            read_data = ''.join(read_data)

        if isinstance(file_client, BlobClient):
            file_client.append_block(read_data, **upload_kwargs)

        if isinstance(file_client, DataLakeFileClient):

            if file_client.exists():
                filesize_previous = file_client.get_file_properties().size
            else:
                filesize_previous = 0

            file_client.append_data(data=read_data, offset=filesize_previous, length=len(read_data), **upload_kwargs)
            file_client.flush_data(filesize_previous+len(read_data))

def upload_data(byte_stream: Union[BytesIO,StringIO], 
                file_client: Union[DataLakeFileClient,BlobClient], 
                upload_mode: str = DEFAULT_UPLOAD_MODE,
                **upload_kwargs):

    """
    Função genérica de upload de arquivo na Azure.

    Args:
        byte_stream (Union[BytesIO,StringIO]): Stream de dados a serem subidos
        file_client (Union[DataLakeFileClient,BlobClient]): Cliente de arquivo da azure.
        upload_mode (str): Modo de upload. Pode ser 'full' (de uma vez só) ou 'chunks' (em pedaços).
                           No modo chunks, precisa explicitar o chunk_size no upload_kwargs.
        **upload_kwargs: Argumentos a serem passados para a upload_data/upload_blob. 
                        Ver DataLakeFileClient.upload_data ou BlobFileClient/upload_blob para mais detalhes

    """
    
    delete_func = lambda x: x
    upload_func = lambda x: x

    if isinstance(file_client, DataLakeFileClient):
        delete_func = file_client.delete_file
    if isinstance(file_client, BlobClient):
        delete_func = file_client.delete_blob

    if upload_mode == 'full':

        if isinstance(file_client, DataLakeFileClient):
            upload_func = file_client.upload_data

        if isinstance(file_client, BlobClient):
            if 'chunk_size' in upload_kwargs:
                upload_kwargs.pop('chunk_size')
            upload_func = file_client.upload_blob
    
    if upload_mode == 'chunks':
        upload_func = partial(upload_chunks, file_client=file_client)

    if file_client.exists():
        delete_func()
    
    byte_stream.seek(0)

    if upload_mode == 'full':
        if isinstance(byte_stream, StringIO):
            byte_stream = ''.join(byte_stream.readlines())

    upload_func(data=byte_stream, 
                overwrite=True, 
                **upload_kwargs)
    
    return file_client

def to_any(byte_stream, uri,
           conn_type=DEFAULT_BLOB_SERVICE,
           upload_mode=DEFAULT_UPLOAD_MODE,
           verbose=1,
           **upload_kwargs):
    
    """
    Função genérica de escrita de arquivo na Azure.

    Args:
        byte_stream (stream): Stream de dados a serem subidos
        uri (url): Url a ser subida o stream de dados
        upload_mode (str): Modo de upload. Pode ser 'full' (de uma vez só) ou 'chunks' (em pedaços).
                           No modo chunks, precisa explicitar o chunk_size no upload_kwargs.
        conn_type (str): String com serviço de conexão a Azure. Pode ser blob ou gen2.
        **upload_kwargs: Argumentos a serem passados para a upload_data/upload_blob. 
                        Ver DataLakeFileClient.upload_data ou BlobFileClient/upload_blob para mais detalhes

    """

    service_client = create_blob_service(uri=uri, conn_type=conn_type)
    container_name = uri.split('/')[3]
    blob_name = '/'.join(uri.split('/')[4:])

    if verbose > 0:
        logger.info(f'Writing {blob_name}')

    if conn_type == 'gen2':
        file_system_client = service_client.get_file_system_client(file_system=container_name)
        file_client = file_system_client.get_file_client(file_path=blob_name)

    if conn_type == 'blob':
        file_client = service_client.get_blob_client(container=container_name, blob=blob_name)

    try:
        file_client = upload_data(byte_stream = byte_stream, 
                                  file_client = file_client, 
                                  upload_mode = upload_mode,
                                  **upload_kwargs)

    finally:

        file_client.close()
        del file_client

        if conn_type == 'gen2':
            file_system_client.close()
            del file_system_client

        service_client.close()
        del service_client

        gc.collect()

def read_any(uri, func, conn_type = DEFAULT_BLOB_SERVICE, **kwargs):

    """
    Função de download genérico de arquivo na Azure

    Args:
        uri (url): Url a ser subida o stream de dados
        func: Função de leitura do arquivo
        conn_type (str): String com serviço de conexão a Azure. Pode ser blob ou gen2.
        **kwargs: Argumentos a serem passados para a função de leitura
    
    Returns:
        Output da função func
    """

    service_client = create_blob_service(uri, conn_type = conn_type)
    container_name = uri.split('/')[3]
    blob_name = '/'.join(uri.split('/')[4:])

    if conn_type == 'gen2':
        file_system_client = service_client.get_file_system_client(file_system=container_name)
        file_client = file_system_client.get_file_client(blob_name)

    if conn_type == 'blob':
        file_client = service_client.get_blob_client(container=container_name, blob=blob_name)

    assert file_client.exists(), f'Could not find blob in {blob_name}'

    try:
        byte_stream = BytesIO()

        if conn_type == 'gen2':
            byte_stream.write(file_client.download_file().readall())
        if conn_type == 'blob':
            byte_stream.write(file_client.download_blob().readall())

    except:
        byte_stream.close()

        file_client.close()
        del file_client

        if conn_type == 'gen2':
            file_system_client.close()
            del file_system_client

        service_client.close()
        del service_client

        gc.collect()

        raise Exception(f'Could not read blob in {blob_name}')

    try:

        byte_stream.seek(0)
        df = func(byte_stream, **kwargs)

    finally:

        byte_stream.close()

        file_client.close()
        del file_client

        if conn_type == 'gen2':
            file_system_client.close()
            del file_system_client

        service_client.close()
        del service_client

        gc.collect()

    return df

def get_partition_cols(uri: str,
                       df: pd.DataFrame = None):
    
    """
    Função que, dada uma url, te retorna as colunas a serem usadas como partição dos arquivos.

    Args:
        uri (str): String com url a ser escrito o arquivo
        df (pd.DataFrame): DataFrame a se pegar as colunas para checar se a partition_col existe. Default é None
    Returns:
        list: Lista de colunas de partição

    """

    partition_cols = [col.lstrip('\{').rstrip('\}') for col in set(re.findall('\{.*?\}',uri))]

    if isinstance(df, pd.DataFrame):
        partition_cols = [col for col in partition_cols if col in df.columns]

    return partition_cols


def to_parquet(df: pd.DataFrame, 
               uri, 
               conn_type = DEFAULT_BLOB_SERVICE,
               upload_kwargs=DEFAULT_CONN_KWARGS, 
               n_jobs=DEFAULT_NUM_THREADS,
               upload_mode=DEFAULT_UPLOAD_MODE,
               **kwargs):
    
    """
    Função de escrita para arquivos parquet e consequente subida a Azure.

    Args:
        df (pd.DataFrame): DataFrame a se escrever em parquet e subir a Azure
        uri (str): String com url a ser escrito o arquivo.
                   Para criar partições a partir de uma coluna, basta escrever o nome da coluna entre chaves.
        conn_type (str): String com serviço de conexão a Azure. Pode ser blob ou gen2.
        upload_kwargs (dict): Argumentos a serem passados para a upload_data/upload_blob. 
                        Ver DataLakeFileClient.upload_data ou BlobFileClient/upload_blob para mais detalhes
        n_jobs (int): Numero máximo de workers a serem usados em uploads paralelos
        **kwargs: Argumentos a serem passados para a função de escrita em parquet.
                  Consultar df.to_parquet para mais detalhes.
    """

    if 'use_deprecated_int96_timestamps' in kwargs:
        kwargs.pop('use_deprecated_int96_timestamps')

    partition_cols = get_partition_cols(df=df, uri=uri)

    def to_parquet_unit(x):

        byte_stream = BytesIO()
        x.to_parquet(byte_stream, use_deprecated_int96_timestamps=True, **kwargs)
        partition_dict = {col: x[col].unique()[0] for col in partition_cols}

        if len(partition_cols) > 0:
            uri_unit = uri.format(**partition_dict)
        else:
            uri_unit = uri

        to_any(byte_stream, uri_unit, conn_type=conn_type, upload_mode=upload_mode, **upload_kwargs)
    
    if len(partition_cols) > 0:
        applyParallel(dfGrouped=df.groupby(partition_cols, as_index=False), 
                      func=to_parquet_unit, 
                      n_jobs=n_jobs,
                      concat_results=False)
    
    else:
        to_parquet_unit(df)

def to_excel(df: pd.DataFrame, 
             uri, 
             conn_type = DEFAULT_BLOB_SERVICE, 
             mode='pandas',
             n_jobs=DEFAULT_NUM_THREADS,
             upload_kwargs=DEFAULT_CONN_KWARGS, 
             upload_mode=DEFAULT_UPLOAD_MODE,
             **kwargs):
    
    """
    Função de escrita para arquivos excel e consequente subida a Azure.

    Args:
        df (pd.DataFrame): DataFrame a se escrever em excel e subir a Azure
        uri (str): String com url a ser escrito o arquivo.
                   Para criar partições a partir de uma coluna, basta escrever o nome da coluna entre chaves.
        conn_type (str): String com serviço de conexão a Azure. Pode ser blob ou gen2.
        mode (str): Modo de escrita de excel. No momento somente suporte a 'pandas' (default). 
                    Futuro suporte a 'pyexcelerate'.
        upload_kwargs (dict): Argumentos a serem passados para a upload_data/upload_blob. 
                        Ver DataLakeFileClient.upload_data ou BlobFileClient/upload_blob para mais detalhes
        n_jobs (int): Numero máximo de workers a serem usados em uploads paralelos
        **kwargs: Argumentos a serem passados para a função de escrita em parquet.
                  Consultar df.to_parquet para mais detalhes.
    """

    #Pyexcelerate still not supported
    if mode == 'pyexcelerate':
        logger.warn(f'to_excel method is currently not supported with pyexcelerate mode')
        mode = 'pandas'
    
    func_dict = {'pandas': pd.DataFrame.to_excel, 'pyexcelerate': pyx_to_excel}

    partition_cols = get_partition_cols(df=df, uri=uri)
    
    def to_excel_unit(x):

        byte_stream = BytesIO()
        func_dict[mode](x, byte_stream, **kwargs)
        partition_dict = {col: x[col].unique()[0] for col in partition_cols}

        if len(partition_cols) > 0:
            uri_unit = uri.format(**partition_dict)
        else:
            uri_unit = uri

        to_any(byte_stream, uri_unit, conn_type=conn_type, upload_mode=upload_mode, **upload_kwargs)
    
    if len(partition_cols) > 0:
        applyParallel(dfGrouped=df.groupby(partition_cols, as_index=False), 
                      func=to_excel_unit, 
                      n_jobs=n_jobs,
                      concat_results=False)
    
    else:
        to_excel_unit(df)

def to_ppttc(df, uri, conn_type = DEFAULT_BLOB_SERVICE,
             upload_kwargs=DEFAULT_CONN_KWARGS, upload_mode=DEFAULT_UPLOAD_MODE, **kwargs):

    #Csv writing currently not supported in blob conn_type
    if conn_type == 'blob':
        logger.warn(f'to_pptc method is currently not supported with blob conn_type')
        conn_type = 'gen2'

    byte_stream = StringIO()
    func = json.dump
    func(obj=df.charts, fp=byte_stream, **kwargs)
    to_any(byte_stream, uri, conn_type=conn_type, upload_mode=upload_mode, **upload_kwargs)

def to_csv(df: pd.DataFrame, 
           uri, 
           conn_type = DEFAULT_BLOB_SERVICE, 
           encoding='utf-8',
           upload_kwargs=DEFAULT_CONN_KWARGS,
           n_jobs=DEFAULT_NUM_THREADS,
           upload_mode=DEFAULT_UPLOAD_MODE,
           **kwargs):
    
    """
    Função de escrita para arquivos csv e consequente subida a Azure.

    Args:
        df (pd.DataFrame): DataFrame a se escrever em csv e subir a Azure
        uri (str): String com url a ser escrito o arquivo.
                   Para criar partições a partir de uma coluna, basta escrever o nome da coluna entre chaves.
        conn_type (str): String com serviço de conexão a Azure. Pode ser blob ou gen2.
        encoding (str): String com encoding do arquivo a ser subido.
        upload_kwargs (dict): Argumentos a serem passados para a upload_data/upload_blob. 
                        Ver DataLakeFileClient.upload_data ou BlobFileClient/upload_blob para mais detalhes
        n_jobs (int): Numero máximo de workers a serem usados em uploads paralelos
        **kwargs: Argumentos a serem passados para a função de escrita em parquet.
                  Consultar df.to_parquet para mais detalhes.
    """

    #Csv writing currently not supported in blob conn_type
    if conn_type == 'blob':
        logger.warn(f'to_csv method is currently not supported with blob conn_type')
        conn_type = 'gen2'

    partition_cols = get_partition_cols(df=df, uri=uri)

    def to_csv_unit(x):

        byte_stream = StringIO()
        x.to_csv(byte_stream, encoding=encoding, **kwargs)
        partition_dict = {col: x[col].unique()[0] for col in partition_cols}

        if len(partition_cols) > 0:
            uri_unit = uri.format(**partition_dict)
        else:
            uri_unit = uri

        to_any(byte_stream, uri_unit, encoding=encoding, conn_type=conn_type, upload_mode=upload_mode, **upload_kwargs)
    
    if len(partition_cols) > 0:
        applyParallel(dfGrouped=df.groupby(partition_cols, as_index=False), 
                      func=to_csv_unit, 
                      n_jobs=n_jobs,
                      concat_results=False)
    
    else:
        to_csv_unit(df)

def to_pptx(df, uri, conn_type = DEFAULT_BLOB_SERVICE, upload_kwargs=DEFAULT_CONN_KWARGS, upload_mode=DEFAULT_UPLOAD_MODE, **kwargs):

    byte_stream = BytesIO()
    df.save(byte_stream, **kwargs)

    return to_any(byte_stream, uri, conn_type=conn_type, upload_mode=upload_mode, **upload_kwargs)

def build_re(glob_str):

    """
    Função que reimplementa o fnmatch.translate.
    Args:
        glob_str (str): String com glob pattern.
    Returns:
        str: String traduzida para regex pattern.
    """

    opts = re.compile('([.]|[*][*]/|[*]|[?])|(.)')
    out = ''
    for (pattern_match, literal_text) in opts.findall(glob_str):
        if pattern_match == '.':
            out += '[.]'
        elif pattern_match == '**/':
            out += '(?:.*/)?'
        elif pattern_match == '*':
            out += '[^/]*'
        elif pattern_match == '?':
            out += '.'
        elif literal_text:
            out += literal_text
    return out

def glob(uri, conn_kwargs=DEFAULT_GLOB_CONN_KWARGS, **kwargs):

    """
    Função que permite, dado uma url, pegar todos os endereços de arquivos da pasta que 
    atendam aos requisitos.

    Args:
        uri (str): Url com padrão fnmatch de regex. 
                   Já possuimos alguns recursos com suporte:
                        - * permite pegar qualquer url que possua qualquer string no lugar de *
                        - (word1|word2) permite filtrar urls que contenham as palavras word1 ou word2
                        - dentre outros
        conn_kwargs (dict): Dicionário com argumentos de conexão a serem passados para a função de get_paths
        **kwargs (dict): Argumentos da função get_paths
    Returns:
        list: Lista com url dos diretórios que atendem ao requisito da uri
    """

    blob_service = create_blob_service(uri, conn_type='gen2')
    container_name = uri.split('/')[3]
    container_url = '/'.join(uri.split('/')[:4])
    blob_name = '/'.join(uri.split('/')[4:])
    container_client = blob_service.get_file_system_client(file_system=container_name)

    # Como a get_paths exige que a path exista, nós quebramos a url em duas variaveis:
    # - path: com a parte da url que exista uma pasta
    # - path_suffix: com a query desejada dentro dessa pasta

    regex = re.compile('^(.*?[\*,\(,\[])')
    lista = regex.split(blob_name)
            
    if len(lista)==1:
        path = lista[0]
        path_suffix = ''
    else:
        new_split = '/'.join(lista[:-1]).split('/')
        path = '/'.join(new_split[:-1])
        path_suffix = new_split[-1] + lista[-1]

    list_blobs = [container_url+'/'+unit.name for unit in container_client.get_paths(path=path, **kwargs, **conn_kwargs)]

    result_list = []

    if len(list_blobs) == 0:
        print('Does not have any file that match the specified criteria')
        return result_list

    if len(path_suffix) == 0:
        return list_blobs

    else:
        path_suffix = build_re(path_suffix) #traduz fnmatch para regex
        result_list = [i for i in np.array(list_blobs) if re.search(path_suffix, i) is not None]

    return result_list

def read_cols(uri, conn_type = DEFAULT_BLOB_SERVICE):

    """
    Função de leitura de colunas em um arquivo parquet
    Args:
        uri (str): Url do arquivo
        conn_type (str): String com serviço de conexão a Azure. Pode ser blob ou gen2.
        
    """

    # Lê estritamente os metadados do parquet

    if ('.parquet' not in uri):
        raise TypeError("O formato do arquivo precisa ser parquet.")

    func = read_schema
    func.memory_map = True

    schema = read_any(uri, func, conn_type=conn_type)
    schema = pd.DataFrame(({"Column": name, "dtype": str(pa_dtype)} for name, pa_dtype in zip(schema.names, schema.types)))
    schema.dropna(inplace = True)

    return schema

def pa_read_parquet(stream, **kwargs):

    """
    Função de leitura de parquets por pyarrow.
    Implementada para poder dar suporte a arquivos com timestamp fora do range padrão do pandas.
    Args:
        stream: Streaming de dados
        **kwargs: Argumentos da função pa_read_table
    """

    to_pandas_kwargs = {}
    params = ['timestamp_as_object']

    for param in params:
        if param in kwargs:
            to_pandas_kwargs[param] = kwargs.pop(param)

    return pa_read_table(stream, **kwargs).to_pandas(**to_pandas_kwargs)

def read_parquet(uri, mode='pandas', conn_type = DEFAULT_BLOB_SERVICE, **kwargs):

    """
    Função de leitura genérica de parquet
    Args:
        uri (str): Url do arquivo
        mode (str): Pode ser 'pandas' para leitura padrão pelo pandas ou 'pyarrow' para leitura direta pelo pyarrow.
                    Modo pyarrow pode ser util para dataframes com timestamps fora do range default do pandas
        conn_type (str): String com serviço de conexão a Azure. Pode ser blob ou gen2.
        **kwargs: Argumentos extras das funções de leitura disponiveis.
    Returns:
        pd.DataFrame: DataFrame desejado
    """

    func = {'pandas': pd.read_parquet, 'pyarrow':pa_read_parquet}
    func = func[mode]
    return read_any(uri, func, conn_type=conn_type, **kwargs)


def read_csv(uri, mode='pandas', conn_type = DEFAULT_BLOB_SERVICE, **kwargs):

    """
    Função de leitura genérica de csv
    Args:
        uri (str): Url do arquivo
        mode (str): Pode ser 'pandas' para leitura padrão pelo pandas.
        conn_type (str): String com serviço de conexão a Azure. Pode ser blob ou gen2.
        **kwargs: Argumentos extras das funções de leitura disponiveis.
    Returns:
        pd.DataFrame: DataFrame desejado
    """

    func = {'pandas': pd.read_csv}
    func = func[mode]
    return read_any(uri, func, conn_type=conn_type, **kwargs)


def read_excel(uri, mode='pandas', conn_type = DEFAULT_BLOB_SERVICE, **kwargs):

    """
    Função de leitura genérica de excel
    Args:
        uri (str): Url do arquivo
        mode (str): Pode ser 'pandas' para leitura padrão pelo pandas.
        conn_type (str): String com serviço de conexão a Azure. Pode ser blob ou gen2.
        **kwargs: Argumentos extras das funções de leitura disponiveis.
    Returns:
        pd.DataFrame: DataFrame desejado
    """

    # A partir de uma determinada versao, o xlrd parou de dar suporte a xlsx.
    # Usa-se por padrão a engine openpyxl. Se ela não for passada, agnt força a engine
    if ('.xlsx' in uri) & ('engine' not in kwargs):
        kwargs['engine'] = 'openpyxl'

    func = {'pandas': pd.read_excel}
    func = func[mode]
    return read_any(uri, func, conn_type=conn_type, **kwargs)

def read_pptx(uri, mode='pptx', conn_type = DEFAULT_BLOB_SERVICE, **kwargs):

    """
    Função de leitura genérica de pptx
    Args:
        uri (str): Url do arquivo
        mode (str): Pode ser 'pptx' para leitura padrão pelo pptx.
        conn_type (str): String com serviço de conexão a Azure. Pode ser blob ou gen2.
        **kwargs: Argumentos extras das funções de leitura disponiveis.
    Returns:
        Presentation: Pptx desejado
    """

    func = {'pptx': Presentation}
    func = func[mode]
    return read_any(uri, func, conn_type=conn_type, **kwargs)

def read_tc_template(uri, _format='pptx', mode='thinkcell', conn_type = DEFAULT_BLOB_SERVICE, **kwargs):
    df = Thinkcell()
    df.add_template(uri)
    return df

def read_url(uri, sas_token, _format, **kwargs):
    """Read from a container with SAS token """
    with tempfile.NamedTemporaryFile() as tf:
        url_tok = uri + sas_token
        urlretrieve(url_tok, tf.name)
        df = read_any(uri=tf.name, _format=_format, **kwargs)
        return df


def file_exists(path):
    """ Checa se o arquivo informado existe """
    last_dir = path.replace(path.split('/')[-1], "*")

    if path in glob(last_dir):
        return True
    else:
        return False