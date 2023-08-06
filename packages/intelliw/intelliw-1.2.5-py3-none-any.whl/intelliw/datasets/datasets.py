'''
Author: hexu
Date: 2021-10-14 14:54:05
LastEditTime: 2022-07-14 17:28:36
LastEditors: Hexu
Description: 数据集
FilePath: /iw-algo-fx/intelliw/datasets/datasets.py
'''
from intelliw.datasets.spliter import get_set_spliter
from intelliw.datasets.datasource_base import AbstractDataSource, DataSourceEmpty, AbstractDataSourceWriter, \
    EmptyDataSourceWriter, DataSourceType, DatasetType
from intelliw.utils.logger import get_logger
from intelliw.config import config

logger = get_logger()


def get_datasource(intelliv_src: str, intelliv_row_addr: str) -> AbstractDataSource:
    datasource_type = config.SOURCE_TYPE
    if datasource_type == DataSourceType.EMPTY:
        return DataSourceEmpty()
    elif datasource_type == DataSourceType.REMOTE_CSV:
        from intelliw.datasets.datasource_remote_csv import DataSourceRemoteCsv
        return DataSourceRemoteCsv(config.DATA_SOURCE_ADDRESS)
    elif datasource_type == DataSourceType.INTELLIV:
        from intelliw.datasets.datasource_intelliv import DataSourceIntelliv
        return DataSourceIntelliv(intelliv_src, intelliv_row_addr, config.INPUT_MODEL_ID)
    elif datasource_type == DataSourceType.LOCAL_CSV:
        from intelliw.datasets.datasource_local_csv import DataSourceLocalCsv
        return DataSourceLocalCsv(config.CSV_PATH)
    elif datasource_type == DataSourceType.IW_IMAGE_DATA:
        from intelliw.datasets.datasource_iwimgdata import DataSourceIwImgData
        return DataSourceIwImgData(intelliv_src, intelliv_row_addr, config.INPUT_DATA_SOURCE_ID, config.INPUT_DATA_SOURCE_TRAIN_TYPE)
    elif datasource_type == DataSourceType.IW_FACTORY_DATA:
        from intelliw.datasets.datasource_iwfactorydata import DataSourceIwFactoryData
        return DataSourceIwFactoryData(intelliv_src, intelliv_row_addr, config.INPUT_DATA_SOURCE_ID)
    elif datasource_type == DataSourceType.NLP_CORPORA:
        from intelliw.datasets.datasource_nlp_corpora import DataSourceNLPCorpora
        return DataSourceNLPCorpora(intelliv_src, config.INPUT_DATA_SOURCE_ID, config.INPUT_DATA_SOURCE_TRAIN_TYPE)
    else:
        err_msg = "数据读取失败，无效的数据源类型: {}".format(datasource_type)
        logger.error(err_msg)
        raise ValueError(err_msg)


def get_datasource_writer(output_addr: str) -> AbstractDataSourceWriter:
    output_datasource_type = config.OUTPUT_SOURCE_TYPE
    if output_datasource_type == DataSourceType.EMPTY:
        return EmptyDataSourceWriter()
    elif output_datasource_type == DataSourceType.INTELLIV or output_datasource_type == DataSourceType.IW_FACTORY_DATA:
        from intelliw.datasets.datasource_intelliv import DataSourceWriter
        return DataSourceWriter(output_addr, config.OUTPUT_DATA_SOURCE_ID, config.INFER_ID, config.TENANT_ID)
    else:
        err_msg = "输出数据源设置失败，无效的数据源类型: {}".format(output_datasource_type)
        logger.error(err_msg)
        raise ValueError(err_msg)


class DataSets:
    def __init__(self, datasource: AbstractDataSource):
        self.datasource = datasource
        self.alldata = list()
        self.column_meta = list()

    def empty_reader(self, dataset_type=DatasetType.TRAIN):
        return self.datasource.reader(page_size=1, offset=0, limit=0, transform_function=None, dataset_type=dataset_type)

    def reader(self, page_size=100000, offset=0, limit=0, split_transform_function=None):
        return self.datasource.reader(page_size, offset, limit, split_transform_function)

    def data_pipeline(self, split_transform_function, alldata_transform_function, feature_process):
        if config.SOURCE_TYPE == DataSourceType.NLP_CORPORA:
            # nlp是文本文件，为了防止文件过大，有自己的处理逻辑
            return self._nlp_data(config.DATA_SPLIT_MODE)
        else:
            # 获取全部数据(切片数据处理， 列选择和数据筛选)
            alldata = self.read_all_data(split_transform_function)
            # 数据处理（全局函数和特征工程）
            alldata = self._data_process(
                alldata, alldata_transform_function, feature_process)
            # 数据集切分
            spliter = get_set_spliter(alldata)

            train, validation, test = spliter.train_reader(
            ), spliter.validation_reader(), spliter.test_reader()
            # 数据集处理 图片下载/语料下载/数据返回
            if config.SOURCE_TYPE == DataSourceType.IW_IMAGE_DATA:
                return self._images_data(train, validation, test)
            else:
                return [[train], [validation], [test]]

    def read_all_data(self, split_transform_function=None):
        reader = self.reader(config.DATA_SOURCE_READ_SIZE, 0,
                             self.datasource.total(), split_transform_function)
        for idx, r in enumerate(reader):
            if config.SOURCE_TYPE != DataSourceType.IW_IMAGE_DATA:
                if idx == 0:
                    self.column_meta = reader.meta
                    self.alldata = r
                elif 'result' in r and 'result' in self.alldata:
                    self.alldata['result'].extend(r['result'])
            else:
                self.alldata.extend(r)
        return self.alldata

    def _data_process(self, alldata, alldata_transform_function, feature_process):
        if config.SOURCE_TYPE == DataSourceType.IW_IMAGE_DATA:
            pass
        elif alldata_transform_function or feature_process:
            if alldata_transform_function:
                alldata = alldata_transform_function(alldata)
            if feature_process:
                alldata = feature_process(alldata)
        return alldata

    def _images_data(self, train, val, test):
        tr = self.datasource.download_images(
            train, dataset_type=DatasetType.TRAIN)
        v = self.datasource.download_images(
            val, dataset_type=DatasetType.VALID)
        te = self.datasource.download_images(
            test, dataset_type=DatasetType.TEST)
        return [tr, v, te]

    def _nlp_data(self, split_mode: int):
        self.datasource.corpora_process(split_mode)
        return [self.datasource()]*3


def get_dataset(intelliv_src: str, intelliv_row_addr: str) -> DataSets:
    datasource = get_datasource(intelliv_src, intelliv_row_addr)
    return DataSets(datasource)
