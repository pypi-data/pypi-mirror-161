'''
Author: hexu
Date: 2021-10-14 14:54:05
LastEditTime: 2022-07-14 10:19:35
LastEditors: Hexu
Description: 远程csv数据集
FilePath: /iw-algo-fx/intelliw/datasets/datasource_remote_csv.py
'''
import time

from intelliw.datasets.datasource_base import AbstractDataSource
from intelliw.datasets.datasource_local_csv import DataSourceLocalCsv
from intelliw.utils.exception import DatasetException
from intelliw.utils.logger import get_logger
import traceback
from intelliw.utils.storage_service import StorageService
from intelliw.config.config import FILE_UP_TYPE

logger = get_logger()


class DataSourceRemoteCsv(AbstractDataSource):
    """
    远程 csv 文件数据源
    """

    def __init__(self, source_address, download_path='./tmp_csv_file.csv'):
        self.source_address = source_address
        self.__tmp_csv_file_path = download_path
        self.__download_file()
        self.__local_csv_data_source = DataSourceLocalCsv(
            self.__tmp_csv_file_path)

    def total(self):
        return self.__local_csv_data_source.total()

    def reader(self, pagesize=10000, offset=0, limit=0, transform_function=None, dataset_type='train_set'):
        return self.__local_csv_data_source.reader(pagesize, offset, limit, transform_function)

    def __download_file(self):
        start_time = time.time()
        logger.info('Downloading csv files from %s to %s',
                    self.source_address, self.__tmp_csv_file_path)
        download_file_name = self.source_address
        local_file_path = self.__tmp_csv_file_path

        try:
            downloader = StorageService(download_file_name, FILE_UP_TYPE, "download")
            downloader.download(local_file_path, stream=True)
            logger.info(f"Csv下载成功, 耗时:{time.time()-start_time}s")
        except Exception as e:
            err = traceback.format_exc()
            raise DatasetException(f"Csv下载失败: {err}")
