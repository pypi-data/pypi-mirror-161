"""
Copyright (C) 2021 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""
from typing import Union

from kaskada.client import Client
import google.protobuf.wrappers_pb2 as wrappers
import kaskada
import kaskada.staging as ks
import kaskada.api.v1alpha.shared_pb2 as shared_pb
import kaskada.api.v1alpha.staged_file_pb2 as staged_pb
import kaskada.api.v1alpha.table_pb2 as table_pb

import grpc
import pandas as pd


class ExternalTable(object):
    pass


class IcebergTable(ExternalTable):
    def __init__(
        self, catalog_bucket: str, catalog_prefix: str, namespace: str, table_name: str
    ):
        self.catalog_bucket = catalog_bucket
        self.catalog_prefix = catalog_prefix
        self.namespace = namespace
        self.table_name = table_name
        # Default region to us-west-2
        self.region = "us-west-2"


def get_table_name(
    table: Union[
        table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str
    ]
) -> str:
    """
    Gets the table name from either the table protobuf, create table response, get table response, or a string

    Args:
        table (Union[table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str]):
            The target table object

    Returns:
        str: The table name (None if unable to match)
    """
    table_name = None
    if isinstance(table, table_pb.Table):
        table_name = table.table_name
    elif isinstance(table, table_pb.CreateTableResponse) or isinstance(
        table, table_pb.GetTableResponse
    ):
        table_name = table.table.table_name
    elif isinstance(table, str):
        table_name = table

    if table_name is None:
        raise Exception(
            "invalid table parameter provided. the table parameter must be the table object, table response from the \
                SDK, or the table name"
        )

    return table_name


def list_tables(
    search: str = None, client: Client = None
) -> table_pb.ListTablesResponse:
    """
    Lists all tables the user has access to

    Args:
        search (str, optional): The search parameter to filter list by. Defaults to None.
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        table_pb.ListTablesResponse: Response from the API
    """
    if client is None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        kaskada.validate_client(client)
        req = table_pb.ListTablesRequest(
            search=search,
        )
        return client.tableStub.ListTables(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)


def get_table(
    table: Union[
        table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str
    ],
    client: Client = None,
) -> table_pb.GetTableResponse:
    """
    Gets a table by name

    Args:
        table (Union[Table, CreateTableResponse, GetTableResponse, str]): The target table object
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        table_pb.GetTableResponse: Response from the API
    """
    if client is None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        table_name = get_table_name(table)
        kaskada.validate_client(client)
        req = table_pb.GetTableRequest(table_name=table_name)
        return client.tableStub.GetTable(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)


def create_table(
    table_name: str,
    time_column_name: str,
    entity_key_column_name: str,
    subsort_column_name: str = None,
    grouping_id: str = None,
    source: ExternalTable = None,
    client: Client = None,
) -> table_pb.CreateTableResponse:
    """
    Creates a table

    Args:
        table_name (str):
            The name of the table
        time_column_name (str):
            The time column
        entity_key_column_name (str):
            The entity key column
        subsort_column_name (str, optional):
            The subsort column. Defaults to None and Kaskada will generate a subsort column for the data.
        grouping_id (str, optional):
            The grouping id. Defaults to None.
        client (Client, optional):
            The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        table_pb.CreateTableResponse: Response from the API
    """
    if client is None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        kaskada.validate_client(client)
        table_args = {
            "table_name": table_name,
            "time_column_name": time_column_name,
            "entity_key_column_name": entity_key_column_name,
            "grouping_id": grouping_id,
        }
        if subsort_column_name:
            table_args["subsort_column_name"] = wrappers.StringValue(
                value=subsort_column_name
            )

        if source:
            if isinstance(source, IcebergTable):
                table_args["table_source"] = {
                    "iceberg": {
                        "config": {
                            "glue": {
                                "warehouse": {
                                    "bucket": source.catalog_bucket,
                                    "region": source.region,
                                    "prefix": source.catalog_prefix,
                                }
                            }
                        },
                        "namespace": source.namespace,
                        "table_name": source.table_name,
                    }
                }
            else:
                raise Exception("invalid external source provided")
        req = table_pb.CreateTableRequest(table=table_pb.Table(**table_args))
        return client.tableStub.CreateTable(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)


def delete_table(
    table: Union[
        table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str
    ],
    client: Client = None,
    force: bool = False,
) -> table_pb.DeleteTableResponse:
    """
    Deletes a table referenced by name

    Args:
        table (Union[Table, CreateTableResponse, GetTableResponse, str]): The target table object
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        table_pb.DeleteTableResponse: Response from the API
    """
    if client is None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        table_name = get_table_name(table)
        kaskada.validate_client(client)
        req = table_pb.DeleteTableRequest(table_name=table_name, force=force)
        return client.tableStub.DeleteTable(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)


def load_data(
    table: Union[
        table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str
    ],
    staged_file: Union[
        staged_pb.StagedFile,
        staged_pb.CreateStagedFileResponse,
        staged_pb.GetStagedFileResponse,
        str,
    ],
    client: Client = None,
) -> table_pb.LoadDataResponse:
    """
    Loads data to a table from a staged file

    Args:
        table (Union[Table, CreateTableResponse, GetTableResponse, str]): The target table object
        staged_file (Union[StagedFile, CreateStagedFileResponse, GetStagedFileResponse, Str]): The staged file object
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Raises:
        Exception: No valid table parameter provided
        Exception: No valid staged file ID parameter provided

    Returns:
        table_pb.LoadDataResponse: Response from the API
    """
    if client is None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    staged_file_id = None
    if isinstance(staged_file, staged_pb.StagedFile):
        staged_file_id = staged_file.file_id
    elif isinstance(staged_file, staged_pb.CreateStagedFileResponse) or isinstance(
        staged_file, staged_pb.GetStagedFileResponse
    ):
        staged_file_id = staged_file.file.file_id
    elif isinstance(staged_file, str):
        staged_file_id = staged_file

    if staged_file_id is None:
        raise Exception(
            "invalid staged file parameter provided. the second parameter must be the staged file object, \
                staged file response from the SDK, or the staged file ID"
        )

    try:
        table_name = get_table_name(table)
        kaskada.validate_client(client)
        req = table_pb.LoadDataRequest(
            table_name=table_name,
            file_id=staged_file_id,
        )
        return client.tableStub.LoadData(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)


def upload_file(
    table: Union[
        table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str
    ],
    file_path: str,
    client: Client = None,
):
    """
    Uploads a file directly to a table. Reads the file and uses the staging area to load the data.

    Args:
        table (Union[table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str]):
            The target table object
        file_path (str):
            The source local file path
        client (Client, optional):
            The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        LoadDataResponse: Response from the API
    """
    if client is None:
        client = kaskada.KASKADA_DEFAULT_CLIENT
    staged_file = ks.create_staged_file(file_path, client=client)
    return load_data(table, staged_file)


def upload_from_s3(
    table: Union[
        table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str
    ],
    access_key: str = None,
    secret: str = None,
    virtual_hosted: str = None,
    region: str = None,
    bucket: str = None,
    key: str = None,
    client: Client = None,
):
    """
    Uploads a file from an external S3 source to a table. Credentials are required and are not persisted in any way.

    Args:
        table (Union[table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str]):
            The target table object
        access_key (str, optional):
            Amazon Web Services Access Key. Used only for authentication and is not persisted.
        secret (str, optional):
            Amazon Web Services Secret Key. Used only for authentication and is not persisted.
        virtual_hosted (str, optional):
            The Amazon Virtual Hosted URI to the file.
            See: https://docs.aws.amazon.com/AmazonS3/latest/userguide/VirtualHosting.html.
            If not provided, the region + bucket + key will be used.
        region (str, optional):
            The target region of the S3 bucket. Only used if virtual_hosted is not provided.
        bucket (str, optional):
            The target S3 bucket. Only used if virtual_hosted is not provided.
        key (str, optional):
            The target key to the object in the S3 bucket. Only used if virtual_hosted is not provided.
        client (Client, optional):
            The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        LoadDataResponse: Response from the API
    """
    if client is None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    external_s3_file = {}
    if virtual_hosted is not None:
        external_s3_file["virtual_hosted_style"] = virtual_hosted
    else:
        external_s3_file["bucket_region_key"] = {
            "bucket": bucket,
            "region": region,
            "key": key,
        }
    try:
        table_name = get_table_name(table)
        kaskada.validate_client(client)

        if access_key and secret:
            credentials = shared_pb.AWSCredential(
                access_key={
                    "aws_access_key_id": access_key,
                    "aws_secret_access_key": secret,
                }
            )
            external_s3_file["aws_credential"] = credentials
        elif access_key and not secret:
            raise ValueError("Access Key provided but Secret was not")
        elif not access_key and secret:
            raise ValueError("Secret provided but Access Key was not")
        external_s3_file = shared_pb.ExternalS3File(**external_s3_file)
        req = table_pb.LoadDataRequest(
            table_name=table_name, external_s3_file=external_s3_file
        )
        return client.tableStub.LoadData(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)


def upload_dataframe(
    table: Union[
        table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str
    ],
    df: pd.DataFrame,
    client: Client = None,
):
    """
    Uploads a dataframe directly to a table. Writes the dataframe to a local file and loads the data to the table

    Args:
        table (Union[table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str]):
            The target table object
        df (pd.DataFrame):
            The source Pandas dataframe
        client (Client, optional):
            The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        LoadDataResponse: Response from the API
    """
    if client is None:
        client = kaskada.KASKADA_DEFAULT_CLIENT
    staged_file = ks.create_staged_file(df, client=client)
    return load_data(table, staged_file)
