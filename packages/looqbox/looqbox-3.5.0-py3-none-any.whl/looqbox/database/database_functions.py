import warnings

from looqbox.global_calling import GlobalCalling
from looqbox.objects.looq_table import ObjTable
from looqbox.utils.utils import base64_decode
from looqbox.database.database_exceptions import TimeOutException, alarm_handler, ConnectionTypeNotFound
import pandas as pd
import jaydebeapi
import pymongo
import datetime
import signal
import json
import os
from google.cloud import bigquery
from google.oauth2 import service_account
import re

__all__ = ["sql_in", "sql_close", "connect", "sql_execute", "sql_between"]

# The _set_connection_alias and _get_connection_alias function are used to save the
# connection alias in the log_query to improve readability. This change prevent log_query from
# save a jaydebeapi.Connection object as connection name, thus raise query trace difficulty
connection_alias = ""


def _set_connection_alias(connection: str) -> None:
    global connection_alias
    connection_alias = connection


def _get_connection_alias() -> str:
    global connection_alias
    return connection_alias


def connect(connection_name: list or str, parameter_as_json=False, use_all_jars=True) -> jaydebeapi.Connection:
    """
    Execute a connection in a database.

    :param connection_name: String or list of database names
    :param parameter_as_json: Set if the parameters will be in JSON format or not
    :param use_all_jars: If set as True, the connection will import all available jars, allowing connection with
                         different database within the same JVM.
                         If this flag is set as False only the connection required jar will be loaded, thus the
                         connection is going to become prone to error, in case another database technology
                         (e.g. another driver, use another version for the same driver) is used, the Looqbox Kernel
                         will crash due the lack of the correct jar(s) file(s).
                         Therefore, setting use_all_jars as False is recommended for tests purpose or for an advanced
                         user.
    :return: A Connection object
    """
    if isinstance(connection_name, str):
        connection_list = [connection_name]
    else:
        connection_list = connection_name

    _set_connection_alias(connection_name)

    connection_credential = _get_connection_credentials(connection_list, parameter_as_json)
    connection_type = _get_connection_type(connection_credential)
    try:
        if connection_type == "jdbc":
            conn = _open_jdbc_connection(connection_credential, use_all_jars)

        elif connection_type == "mongo_db":
            conn = _open_mongo_connection(connection_credential)

        elif connection_type == "big_query":
            conn = _handle_api_connection(connection_credential)

        else:
            raise ConnectionTypeNotFound("\nConnection type is not supported")
    except:
        raise Exception("Error while trying to connect to the database")

    return conn


def _get_connection_type(connection_credential):
    return connection_credential.get("type", "jdbc").lower()


def _open_jdbc_connection(connection_credential, use_all_jars):
    # build driver_args to enable connections that rather use or not user and password
    if _is_user_and_password_empty(connection_credential):
        driver_args = {}
    else:
        driver_args = {
            'user': connection_credential['user'],
            'password': base64_decode(connection_credential['pass'])
        }
    # Since jaydebeapi instantiate a JVM to perform the db connection, any kind of alteration (jar/drive insertion or
    # removing) are impossible, thus being essential to shut down the current JVM (create an error in Looqbox Kernel)
    # in this regard, all jars are imported into the JVM by default
    jars_path = _get_all_jar_files() if use_all_jars else connection_credential["jar"]
    conn = jaydebeapi.connect(
        connection_credential['driver'],
        connection_credential['connString'],
        driver_args,
        jars=jars_path,
    )
    return conn


def _is_user_and_password_empty(connection_credential: dict) -> bool:
    return connection_credential['user'] == '' and connection_credential['pass'] == ''


def _open_mongo_connection(connection_credential: dict) -> dict:
    # Since the original object MongoClient, it's the one that has the close connection method,
    # it must be passed forward, until the very end of sql_execute
    mongo_connection = pymongo.MongoClient(connection_credential.get("connString"))
    conn = {"database": _get_database_from_mongo_connString(connection_credential.get("connString")),
            "mongo_connection": mongo_connection
            }
    return conn


def _get_database_from_mongo_connString(connection_string: str) -> str:
    regex_pattern = "(?<=\\w/)\\w+(?=[/\\w+]?)"
    database_name = re.findall(regex_pattern, connection_string)[0]
    return database_name


def _handle_api_connection(connection):
    warnings.warn("This connection does not support connect, use sql_execute directly")
    return connection


def sql_execute(connection, query, replace_parameters=None, close_connection=True, show_query=False,
                null_as=None, add_quotes=False, cache_time=0):
    """
    Function to execute a query inside the connection informed. The result of the query will be
    transformed into a ObjTable to be used inside the response.


    :param connection: Connection name or object
    :param query: sql script to query result set (in Big Query or JDBC database), for a Mongo use, the query parameter
    must be defined as followed:
    query = {"collection": "example",
             "query": {"store":10},
             "fields": {"_id": 0, "name": 1, "sales": 1}
            }
    :param replace_parameters: List of parameters to be used in the query. These parameters will replace the numbers
    wit h `` in the query.
        Example:
            replace_parameters = [par1, par2, par3, par4]
            query = "select * from bd where par1=`1` and par2=`2` and par3=`3` and par4=`4`

            In this case the values of `1`, `2`, `3`, `4` will be replaced by par1, par2, par3, par4 respectively (using
            the order of the list in replace_parameters).

    :param close_connection: Define if automatically closes the connection
    :param show_query: Print the query in the console
    :param null_as: Default value to fill null values in the result set
    :param add_quotes: Involves replaced parameters with quotes
    Example:
        replace_parameters = [par1]
            query = "select * from db where par1=`1`"
        For add_quotes = True
            query = "select * from db where par1='par1'"
        For add_quotes = False
            query = "select * from db where par1=par1"
    :param cache_time: Time to leave of cache file in seconds, one might set up to 300 seconds
    :return: A Looqbox ObjTable with the data retrieved from the query
    """

    if replace_parameters is not None:
        query = _sql_replace_parameters(query, replace_parameters, add_quotes)

    test_mode = GlobalCalling.looq.test_mode

    if show_query and test_mode:
        print(query)

    query_dataframe = ObjTable(null_as=null_as)

    sql_timeout = 0 if test_mode else _get_script_timeout()

    # Configure timeout features
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(sql_timeout)

    start_time = datetime.datetime.now()

    connection = connect(connection)

    try:
        if cache_time > 0:
            query_dataframe.data, query_dataframe.metadata = _use_query_cache(cache_time, close_connection, connection,
                                                                              query, query_dataframe)
        else:
            query_dataframe.data, query_dataframe.metadata = _get_query_result(close_connection, connection,
                                                                               query, query_dataframe)

        total_sql_time = datetime.datetime.now() - start_time

        GlobalCalling.log_query({"connection": str(_get_connection_alias()), "query": str(query),
                                 "time": str(total_sql_time), "success": True})

    except jaydebeapi.DatabaseError as e:
        sql_close(connection)
        total_sql_time = datetime.datetime.now() - start_time

        GlobalCalling.log_query({"connection": str(_get_connection_alias()), "query": str(query),
                                 "time": str(total_sql_time), "success": False})

        print(str(e), "java.sql.SQLException: expected")

    except TimeOutException as ex:
        sql_close(connection)
        total_sql_time = datetime.datetime.now() - start_time

        GlobalCalling.log_query({"connection": str(_get_connection_alias()), "query": str(query),
                                 "time": str(total_sql_time), "success": False})

    except Exception as general_error:
        sql_close(connection)
        total_sql_time = datetime.datetime.now() - start_time

        GlobalCalling.log_query({"connection": str(_get_connection_alias()), "query": str(query),
                                 "time": str(total_sql_time), "success": False})

        print(str(general_error))

    finally:
        signal.alarm(0)
        if not test_mode:
            _update_sql_timeout(total_sql_time)

    df_cols_and_rows = query_dataframe.data.shape
    query_dataframe.rows = df_cols_and_rows[0]
    query_dataframe.cols = df_cols_and_rows[1]

    if test_mode:
        total_sql_time = datetime.datetime.now() - start_time
        print("SQL fetch in...", total_sql_time.total_seconds(), "secs")

    if close_connection:
        sql_close(connection)

    return query_dataframe


def _get_query_result(close_connection, connection, query, query_dataframe):
    if _is_connection_jdbc(connection):
        query_dataframe.data, query_dataframe.metadata = _get_JDBC_query_result(connection, query, close_connection)

    elif _is_connection_mongo(connection):
        query_dataframe.data, query_dataframe.metadata = _get_mongo_query_result(connection, query)

    elif _is_connection_big_query(connection):
        query_dataframe.data, query_dataframe.metadata = _get_BQ_query_result(connection, query)

    else:
        raise Exception("Connection function not found: \n Looqbox could not find a function to execute the query")

    return query_dataframe.data, query_dataframe.metadata


def _is_connection_jdbc(connection) -> bool:
    is_jdbc = isinstance(connection, jaydebeapi.Connection) or \
              isinstance(connection, jaydebeapi.Cursor)
    return is_jdbc


def _is_connection_mongo(connection) -> bool:
    is_mongo = isinstance(connection, dict) and \
               isinstance(connection.get("mongo_connection"), pymongo.mongo_client.MongoClient)
    return is_mongo


def _is_connection_big_query(connection):
    is_big_query = isinstance(connection, dict) and \
                   "apiKey" in connection.keys()
    return is_big_query


def _use_query_cache(cache_time, close_connection, connection, query, query_dataframe):
    # since cache is saved in rds format, it's necessary
    # to load the equivalent R functions

    from pyreadr import read_r, write_rds

    # data frame name used in rds file, since R and Python shared the same files,
    # no name has to be attached to the data
    DF_NAME = None

    cache_name = _generate_cache_file_name(query)

    test_mode = GlobalCalling.looq.test_mode

    if test_mode:
        check_if_temp_folder_exists()
    cache_file = GlobalCalling.looq.temp_file(cache_name, add_hash=False)

    if _is_cache_still_valid(cache_file, cache_time):
        if test_mode:
            print("using cache\npath:", cache_file)
        try:
            cached_data = read_r(cache_file)[DF_NAME]
            query_dataframe.data = pd.DataFrame(cached_data, columns=cached_data.keys())
            query_dataframe.metadata = {}  # temporally disable metadata for cache
        except FileNotFoundError as file_exception:
            print(file_exception)
    else:
        if test_mode:
            print("creating cache\npath:", cache_file)
        query_dataframe.data, query_dataframe.metadata = _get_query_result(close_connection, connection,
                                                                           query, query_dataframe)
        try:
            write_rds(cache_file, query_dataframe.data)
        except Exception as folder_exception:
            print(folder_exception + "\nCould not find location: " + cache_file)

    return query_dataframe.data, query_dataframe.metadata


def _is_cache_still_valid(cache_file, cache_time):
    import time

    return os.path.isfile(cache_file) and (time.time() - os.stat(cache_file).st_mtime) < cache_time


def check_if_temp_folder_exists():
    temp_path = GlobalCalling.looq.temp_dir
    if not os.path.isdir(temp_path):
        os.mkdir(temp_path)


def _generate_cache_file_name(query):
    """
    Cache file name is created by encrypt the sql script into a MD5
    string, thus avoiding duplicated names.
    """
    from hashlib import md5

    if isinstance(query, dict):
        query = _convert_mongo_query_to_string(query)

    hashed_file_name = md5(query.encode())
    return str(hashed_file_name.hexdigest()) + ".rds"


def _convert_mongo_query_to_string(query: dict) -> str:
    query_as_string = ""
    keys = list(query.keys())
    values = list(query.values())
    for i in range(len(keys)):
        query_as_string += str(keys[i]) + " " + str(values[i]) + ";"
        query_as_string += " "

    # Removed addition blank space at the end
    query_as_string = query_as_string[:-1]

    # since the character { and } could mess up the md5 conversion between R and Python
    # theses must be removed from the string
    query_as_string = query_as_string.replace("{", "").replace("}", "")
    return query_as_string


def _get_JDBC_query_result(connection, query, close_connection):
    """
    Function to get the table resulting from the query

    :param connection: Connection name or class
    :param query: Query to get the table
    :param close_connection: Define if automatically closes the connection
    :return: Return the data frame resulting from the query.
    """

    try:
        if isinstance(connection, str):
            connection = connect(connection)

        conn_curs = connection.cursor()

    except:
        if close_connection and not isinstance(connection, str):
            conn_curs.close()
            sql_close(conn_curs)

        raise Exception("Error to connect in database.")

    try:
        conn_curs.execute(query)
        col_names = [i[0] for i in conn_curs.description]
        fetch_tuple = conn_curs.fetchall()

        metadata = get_column_types(conn_curs)

        # Fix error when fetch brings one None row
        query_df = pd.DataFrame()
        if fetch_tuple or len(fetch_tuple) > 0:
            if len(fetch_tuple[0]) == 1:
                if fetch_tuple[0][0] is not None:
                    query_df = pd.DataFrame(fetch_tuple, columns=col_names)
            else:
                query_df = pd.DataFrame(fetch_tuple, columns=col_names)

        sql_close(conn_curs)

        return query_df, metadata
    except:
        if close_connection and not isinstance(connection, str):
            conn_curs.close()
            sql_close(conn_curs)

        raise Exception("Error to execute query.")


def _get_mongo_query_result(connection, query):
    database_connection = connection["mongo_connection"][connection.get("database")]
    collection = database_connection[(query.get("collection"))]
    query_result = collection.find(query.get("query"), query.get("fields"))
    dataframe = pd.DataFrame(query_result)

    metadata = dict(dataframe.dtypes)
    return dataframe, metadata


def _get_BQ_query_result(big_query_credentials, query):
    big_query_key = json.loads(big_query_credentials.get("apiKey"))
    bq_client = _connect_to_client(big_query_key)
    bq_request = bq_client._connection.api_request(
        "POST",
        "/projects/{}/queries".format(bq_client.project),
        data={"query": query, "useLegacySql": False},
    )
    if bq_request.get("totalRows", "0") != "0":
        fields = bq_request.get("schema").get("fields")
        rows = bq_request.get("rows")
        column_names = [field.get("name") for field in fields]
        column_types = [field.get("type") for field in fields]
        type_dict = dict(zip(column_names, column_types))
        row_list = [row.get("f") for row in rows]
        raw_data_frame = pd.DataFrame(data=row_list, columns=column_names)
        data_frame = raw_data_frame.applymap(lambda cell: cell.get("v"))
        _convert_columns_type(data_frame, type_dict)
    else:
        data_frame = pd.DataFrame()

    metadata = get_table_metadata_from_request(bq_request)

    return data_frame, metadata


def _connect_to_client(big_query_key):
    SCOPES = ["https://www.googleapis.com/auth/bigquery", "https://www.googleapis.com/auth/cloud-platform"]
    credentials = service_account.Credentials.from_service_account_info(big_query_key)
    client = bigquery.Client(
        credentials=credentials,
        project=credentials.project_id
    )
    return client


def _convert_columns_type(data_frame, types):
    type_function_map = {
        "NUMERIC": "float",
        "BIGNUMERIC": "float",
        "FLOAT": "float",
        "INTEGER": "int",
    }
    for column, type in types.items():
        if type_function_map.get(type):
            astype_type = type_function_map[type]
            data_frame[column] = data_frame[column].astype(astype_type, errors="ignore")


def get_column_types(cursor):
    metadata = dict()
    for column in cursor.description:
        column_name = column[0]
        column_type = filter_types(column[1].values)
        metadata[column_name] = {
            "type": column_type
        }
    return metadata


def get_table_metadata_from_request(request: dict) -> dict:
    metadata = dict()
    for column in request.get("schema").get("fields"):
        column_type = column.get("type")
        metadata[column.get("name")] = {
            "type": column_type
        }

    return metadata

def filter_types(type_list):
    type_dict = {
        'CHAR': ('CHAR', 'NCHAR', 'NVARCHAR', 'VARCHAR', 'OTHER'),
        'LONGVARCHAR': ('CLOB', 'LONGVARCHAR', 'LONGNVARCHAR', 'NCLOB', 'SQLXML'),
        'BINARY': ('BINARY', 'BLOB', 'LONGVARBINARY', 'VARBINARY'),
        'INTEGER': ('BOOLEAN', 'BIGINT', 'BIT', 'INTEGER', 'SMALLINT', 'TINYINT'),
        'FLOAT': ('FLOAT', 'REAL', 'DOUBLE'),
        'NUMERIC': ('DECIMAL', 'NUMERIC'),
        'DATE': ('DATE',),
        'TIME': ('TIME',),
        'TIMESTAMP': ('TIMESTAMP',),
        'ROWID': ('ROWID',)
    }
    column_type = None
    for db_type, aliases in type_dict.items():
        if type_list == aliases:
            column_type = db_type
    return column_type


def _sql_replace_parameters(query, replace_parameters, replace_with_quotes=False):
    """
    This function get the query and replace all the values between backticks to the values in the replace_parameters
    list, the values are substituted using the order in replace parameters, for example, the `1` in the query will be
    substituted by the value replace_parameters[0] and so goes on.
    Example:
        query = "select * from database where x = `1` and z = `3` and y = `2`"
        replace_parameters = [30, 50, 60}

        returns = "select * from database where x = 30 and z = 60 and y = 50"

    :param query: Query to be changed
    :param replace_parameters: List that contains the values to be substitute
    :param replace_with_quotes=False: Involves replaced parameters with quotes
    :return: Query with the values changed
    """
    separator = '"' if replace_with_quotes else ""

    for replace in range(len(replace_parameters)):
        query = query.replace('`' + str((replace + 1)) + '`', separator + str(replace_parameters[replace]) + separator)
    return query


def sql_in(query=None, values_list=None):
    """
    Transform the list in values_list to be used inside a IN statement of the SQL.
    Example:
        values_list = [1,2,3,4,5]
        query = 'select * from database where' + sql_in(" col in", values_list)

        "select * from database where col in (1, 2, 3, 4, 5)"


    :param query: Query header with the first part of the query
    :param values_list: list to be transformed as a IN format
    :return: query concatenated with values_list as a IN format
    """
    if values_list is None:
        return ""

    if not isinstance(values_list, list):
        values_list = [values_list]

    separated_list = str(values_list).replace('[', '(').replace(']', ')')

    if query is None:
        return separated_list
    else:
        return query + " " + separated_list


def sql_between(query=None, values_list=None):
    """
    Transform the list in values_list to be used as a between statement of the SQL.
    Example:
        values_list = ['2018-01-01', '2018-02-02']
        query = 'select * from database where sql_between(' date', date_int)'

        "select * from database where date between '2018-01-01' and '2018-02-02')"


    :param query: Query header with the first part of the query
    :param values_list: list to be used in a between statement
    :return: query concatenated with values_list as a between statement
    """
    if values_list is None:
        return ""

    if len(values_list) != 2:
        raise Exception("To use sql_between values_list must be of two positions")

    if not isinstance(values_list, list):
        values_list = [values_list]

    if isinstance(values_list[0], int) or isinstance(values_list[1], int):
        between_query = query + " between " + str(values_list[0]) + " and " + str(values_list[1])
    else:
        between_query = query + " between '" + values_list[0] + "' and '" + values_list[1] + "'"

    return between_query


def sql_close(conn):
    """
    Close a connection
    :param conn: Connection of the type JayBeDeApi
    """

    if _is_connection_jdbc(conn):
        conn.close()
    elif _is_connection_mongo(conn):
        conn.get("mongo_connection").close()


def reload_database_connection(conn_file_path=GlobalCalling.looq.connection_file):
    if os.path.isfile(conn_file_path):
        GlobalCalling.looq.connection_config = json.loads(conn_file_path)
    else:
        print("Missing connection file: " + GlobalCalling.looq.connection_file)
        GlobalCalling.looq.connection_config = None


def _update_sql_timeout(time_used: float = 0):
    """
    Subtract the amount of time used in script timeout
    """
    GlobalCalling.looq.response_timeout -= int(round(time_used.total_seconds(), 0))
    return None


def _get_script_timeout() -> float:
    """
    Retrieve the remaining script run time
    """
    # Starts script timeout counting
    return GlobalCalling.looq.response_timeout


def _get_all_jar_files() -> list:
    """
    Get and append all jar files required for each entry in connection.json
    """

    jar_list = list()
    file_connections = _get_connection_file()

    # get the jar files for each connection
    for connections in file_connections:

        # Avoid errors due some wrong connection register
        try:
            connection_jar = _get_connection_credentials([connections])["jar"]
        except:
            connection_jar = []

        jar_list.extend(connection_jar)
    return jar_list


def _is_jar(file: str) -> bool:
    return not file.startswith('.') and '.jar' in file


def _get_connection_file() -> dict:
    try:
        if isinstance(GlobalCalling.looq.connection_config, dict):
            file_connections = GlobalCalling.looq.connection_config
        else:
            file_connections = open(GlobalCalling.looq.connection_config)
            file_connections = json.load(file_connections)
    except FileNotFoundError:
        raise Exception("File connections.json not found")
    return file_connections


def _get_connection_credentials(connection: list, parameter_as_json=False) -> dict:
    """
    Get credentials for a list of connections.

    :param connection: String or list of database names
    :param parameter_as_json: Set if the parameters will be in JSON format or not
    :return: A Connection object
    """
    driver_path = []
    connection_credential = _get_connection_file()
    for conn_name in connection:
        try:
            if not parameter_as_json:
                connection_credential = GlobalCalling.looq.connection_config[conn_name]
            else:
                connection_credential = connection_credential[conn_name]
        except KeyError:
            raise Exception("Connection " + conn_name + " not found in the file " + GlobalCalling.looq.connection_file)

        if _connection_have_driver(connection_credential):
            driver_path = _get_drivers_path(connection_credential, driver_path)
        connection_credential["jar"] = driver_path
    return connection_credential


def _get_drivers_path(connection_credential, driver_path):
    conn_file_name, conn_file_extension = os.path.splitext(connection_credential['driverFile'])
    old_driver_folder_path = os.path.join(GlobalCalling.looq.jdbc_path + '/' + conn_file_name + conn_file_extension)
    new_driver_folder_path = os.path.join(GlobalCalling.looq.jdbc_path + '/' + conn_file_name)
    if new_driver_folder_path:
        for file in os.listdir(new_driver_folder_path):
            if _is_jar(file):
                driver_path.append(new_driver_folder_path + '/' + file)

    elif old_driver_folder_path:
        driver_path = old_driver_folder_path
    return driver_path


def _connection_have_driver(connection):
    return connection.get('driverFile') is not None