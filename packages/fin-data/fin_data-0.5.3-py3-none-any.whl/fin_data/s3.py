from datetime import datetime
from functools import cache
from pathlib import Path
from pprint import pformat
from typing import List, Optional

import boto3
import pandas as pd
import sqlalchemy as sa
from boto3.session import Config
from pydantic import BaseSettings
from tqdm import tqdm

from .utils import logger


class S3Settings(BaseSettings):
    s3_endpoint_url: str = "http://localhost:9000"
    aws_access_key_id: str
    aws_secret_access_key: str


def s3_storage_options():
    s3_settings = S3Settings()
    return {
        "key": s3_settings.aws_access_key_id,
        "secret": s3_settings.aws_secret_access_key,
        "client_kwargs": {"endpoint_url": s3_settings.s3_endpoint_url},
    }


@cache
def s3():
    s3_settings = S3Settings()
    return boto3.resource(
        "s3",
        endpoint_url=s3_settings.s3_endpoint_url,
        aws_access_key_id=s3_settings.aws_access_key_id,
        aws_secret_access_key=s3_settings.aws_secret_access_key,
        config=Config(signature_version="s3v4"),
    )


def get_bucket(bucket_name: str):
    bucket = s3().Bucket(bucket_name)
    if not bucket.creation_date:
        logger.info(f"Creating bucket: {bucket_name}")
        bucket.create()
    return bucket


def delete_file(bucket_name: str, file_name: str):
    file = Path(file_name).path
    logger.info(f"Deleting file {file} from bucket {bucket_name}.")
    s3().Object(bucket_name, file).delete()


def save_parquet(
    df: pd.DataFrame,
    bucket: str,
    table: sa.Table,
    symbol: Optional[str] = None,
    archive: bool = False,
    file_start_time: datetime = None,
    date_format: str = "%y%m%d_%H%M",
):
    file_parts = [table.name]
    if symbol:
        file_parts.append(symbol)
    if file_start_time:
        file_parts.append(file_start_time.strftime(date_format))
    file = f"s3://{bucket}/{'_'.join(file_parts)}.parquet"
    logger.info(f"Saving parquet file: {file}")
    df.to_parquet(
        file,
        storage_options=s3_storage_options(),
        compression="gzip" if archive else "snappy",
    )
    return file


def df_from_s3(files: List[str]):
    if isinstance(files, str):
        files = [files]
    logger.info(f"Creating DataFrame with {len(files)} files:\n{pformat(files)}")
    storage_options = s3_storage_options()
    df = pd.concat(
        [pd.read_parquet(file, storage_options=storage_options) for file in files]
    )
    return df


def df_from_bucket(bucket_name: str):
    s3 = s3()
    bucket = s3.Bucket(bucket_name)
    files = [f"s3://{bucket_name}/{f.key}" for f in bucket.objects.all()]
    logger.info(f"Creating DataFrame with {len(files)} files from bucket {bucket_name}")
    storage_options = s3_storage_options()
    dfs = []
    for f in tqdm(files):
        dfs.append(pd.read_parquet(f, storage_options=storage_options))
    return pd.concat(dfs)
