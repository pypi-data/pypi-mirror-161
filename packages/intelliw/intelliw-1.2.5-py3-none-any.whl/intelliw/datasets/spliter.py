'''
Author: hexu
Date: 2021-10-14 14:54:05
LastEditTime: 2022-07-13 14:41:17
LastEditors: Hexu
Description: 数据集切分工具
FilePath: /iw-algo-fx/intelliw/datasets/spliter.py
'''
from abc import ABCMeta, abstractmethod
import math
import random
from typing import Iterable
from intelliw.utils.exception import DatasetException
from intelliw.config import config
from intelliw.utils.global_val import gl
from intelliw.utils.logger import get_logger
from intelliw.datasets.datasource_base import DataSourceType


def get_set_spliter(data):
    logger = get_logger()
    if config.DATA_SPLIT_MODE == 0:
        spliter_cls = SequentialSpliter
    elif config.DATA_SPLIT_MODE == 1:
        spliter_cls = ShuffleSpliter
    elif config.DATA_SPLIT_MODE == 2:
        spliter_cls = TargetRandomSpliter
    else:
        err_msg = "输出数据源设置失败，数据集划分模式: {}".format(config.DATA_SPLIT_MODE)
        logger.error(err_msg)
        raise ValueError(err_msg)
    return spliter_cls(data, config.TRAIN_DATASET_RATIO, config.VALID_DATASET_RATIO, config.TEST_DATASET_RATIO)


def check_split_ratio(train_ratio, valid_ratio, test_ratio):
    assert 0 < train_ratio <= 1, f"数据集比例不正确, 训练集比例{train_ratio}"
    assert 0 <= valid_ratio < 1, f"数据集比例不正确, 验证集比例{valid_ratio}"
    assert 0 <= test_ratio < 1, f"数据集比例不正确, 测试集比例{test_ratio}"
    assert train_ratio + valid_ratio + test_ratio < 1.09, "数据集比例不正确, 总和不为1"


def get_set_count(length, train_ratio, valid_ratio, test_ratio):
    train_num = math.floor(length * float(train_ratio))
    if test_ratio == 0:
        valid_num = length - train_num
        test_num = 0
    else:
        valid_num = math.floor(length * float(valid_ratio))
        test_num = length - train_num - valid_num
    return train_num, valid_num, test_num


class DataSetSpliter(metaclass=ABCMeta):
    def __init__(self, data, train_ratio, valid_ratio, test_ratio):
        if not isinstance(data, (dict, list)):
            raise TypeError("data_source has a wrong type, required: list, actually: {}".format(
                type(data).__name__))

        check_split_ratio(train_ratio, valid_ratio, test_ratio)

        if config.SOURCE_TYPE == DataSourceType.IW_IMAGE_DATA:  # 图片数据源:
            self.alldata = data
        else:
            self.alldata = data.pop("result")
            self.column_meta = data.pop("meta")
        self.data_num = len(self.alldata)
        self.train_num, self.valid_num, self.test_num = get_set_count(
            self.data_num, train_ratio, valid_ratio, test_ratio
        )

    def train_reader(self) -> Iterable:
        if self.train_num == 0:
            return []
        return self._train_reader()

    @abstractmethod
    def _train_reader(self) -> Iterable:
        pass

    def validation_reader(self) -> Iterable:
        if self.valid_num == 0:
            return []
        return self._validation_reader()

    @abstractmethod
    def _validation_reader(self) -> Iterable:
        pass

    def test_reader(self) -> Iterable:
        if self.test_reader == 0:
            return []
        return self._test_reader()

    @abstractmethod
    def _test_reader(self) -> Iterable:
        pass

# SequentialSpliter 顺序读取数据


class SequentialSpliter(DataSetSpliter):
    """顺序读取数据
    数据按照训练集比例分割，前面为训练集，后面为验证集
    """

    def __init__(self, data, train_ratio, valid_ratio, test_ratio):
        super().__init__(data, train_ratio,
                         valid_ratio, test_ratio)
        self.train_data = None
        self.valid_data = None
        self.test_data = None

    def _train_reader(self):
        if self.train_data is None:
            self._set_data()
        return self.train_data

    def _validation_reader(self):
        if self.valid_data is None:
            self._set_data()
        return self.valid_data

    def _test_reader(self):
        if self.test_data is None:
            self._set_data()
        return self.test_data

    def _set_data(self):
        # 获取所有数据
        train_data = self.alldata[:self.train_num]
        if self.test_num == 0:
            valid_data = self.alldata[self.train_num:]
            test_data = []
        else:
            valid_data = self.alldata[self.train_num:
                                      self.train_num + self.valid_num]
            test_data = self.alldata[self.train_num + self.valid_num:]

        if config.SOURCE_TYPE == DataSourceType.IW_IMAGE_DATA:
            self.train_data = train_data
            self.valid_data = valid_data
            self.test_data = test_data
        else:
            self.train_data = {"meta": self.column_meta, "result": train_data}
            self.valid_data = {"meta": self.column_meta, "result": valid_data}
            self.test_data = {"meta": self.column_meta, "result": test_data}


# ShuffleSpliter 乱序读取
class ShuffleSpliter(DataSetSpliter):
    """乱序读取

    注意:
    此方法需要读取全部数据，会给内存带来压力
    """

    def __init__(self, data, train_ratio, valid_ratio, test_ratio):
        super().__init__(data, train_ratio,
                         valid_ratio, test_ratio)

        self.train_data = None
        self.valid_data = None
        self.test_data = None
        self.seed = 1024  # 使用固定 seed 保证同一个数据集多次读取划分一致

    def _train_reader(self):
        if self.train_data is None:
            self._set_data()
        return self.train_data

    def _validation_reader(self):
        if self.valid_data is None:
            self._set_data()
        return self.valid_data

    def _test_reader(self):
        if self.test_data is None:
            self._set_data()
        return self.test_data

    def _set_data(self):
        # 获取所有数据
        r = random.Random(self.seed)
        r.shuffle(self.alldata)
        train_data = self.alldata[:self.train_num]
        if self.test_num == 0:
            valid_data = self.alldata[self.train_num:]
            test_data = []
        else:
            valid_data = self.alldata[self.train_num:
                                      self.train_num + self.valid_num]
            test_data = self.alldata[self.train_num + self.valid_num:]

        if config.SOURCE_TYPE == DataSourceType.IW_IMAGE_DATA:
            self.train_data = train_data
            self.valid_data = valid_data
            self.test_data = test_data
        else:
            self.train_data = {"meta": self.column_meta, "result": train_data}
            self.valid_data = {"meta": self.column_meta, "result": valid_data}
            self.test_data = {"meta": self.column_meta, "result": test_data}


class TargetRandomSpliter(DataSetSpliter):
    """根据目标列乱序读取
    按照目标列中类别的比例，进行训练集和验证集的划分，保证训练集和验证集中类别比例与整体数据比例相同

    使用此方法的前提：
     - 有目标列
     - 是分类

    几种可能存在的边界：
     - 分类太多: 1w数据分出来5k类别, 算法框架在tag_count/total > 0.5的时候会warn
     - 类别唯一: 只有一个tag
     - 某类别唯一: 某个tag只有一
     - 无目标列下标: 需要配置targetCol
     - 训练集或验证集比例为1

    注意:
    此方法需要读取全部数据，会给内存带来压力
    """

    def __init__(self, data, train_ratio, valid_ratio, test_ratio):
        super().__init__(data, train_ratio,
                         valid_ratio, test_ratio)

        self.target_col = None
        self.train_data = None
        self.valid_data = None
        self.test_data = None
        self.seed = 1024  # 使用固定 seed 保证同一个数据集多次读取划分一致
        self.train_ratio = train_ratio
        self.valid_ratio = valid_ratio
        self.test_ratio = test_ratio
        self._verify()

    def _verify(self):
        target_metadata = gl.get("target_metadata")
        if target_metadata is None or len(target_metadata) == 0:
            raise DatasetException("配置文件(algorithm.yaml)中未设置target相关数据")
        if len(target_metadata) > 1:
            raise DatasetException("目前只支持针对单目标列的数据shuffle处理")
        self.target_col = target_metadata[0]["target_col"]
        if type(self.target_col) != int:
            raise DatasetException(
                f"类型错误:targetCol类型应为int, 当前数据: {self.target_col}-{type(self.target_col)}")
        if self.train_ratio in (0, 1):
            raise DatasetException("根据目标列乱序读取,train_ratio不应设置为1或者0")

    def _train_reader(self):
        if self.train_data is None:
            self._set_data()
        return self.train_data

    def _validation_reader(self):
        if self.valid_data is None:
            self._set_data()
        return self.valid_data

    def _test_reader(self):
        if self.test_data is None:
            self._set_data()
        return self.test_data

    def _set_data(self):
        import pandas as pd

        df = pd.DataFrame(self.alldata)
        # 边界处理
        if df.shape[1] < self.target_col + 1:
            raise DatasetException(
                f"数据集不存在目标列, 数据集列数{df.shape[1]}, 目标列下标{self.target_col}")

        train, valid, test = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        tags = df[df.columns[self.target_col]].unique().tolist()

        # 边界处理
        tag_count = len(tags)
        if (tag_count < 2) or (tag_count << 1 >= self.total_read):
            raise DatasetException("目标列类别数量唯一, 或者类别数量超过总数据的50%")

        for tag in tags:
            all_data = df[df[df.columns[self.target_col]] == tag]

            # 边界处理
            if all_data.shape[0] == 1:
                raise DatasetException(f"tag: {tag} 只有一条数据")

            # train
            train_data = all_data.sample(
                int(self.train_ratio * len(all_data)), random_state=self.seed)
            train_index, all_index = train_data.index, all_data.index
            other_index = all_index.difference(train_index)  # 去除sample之后剩余的数据
            other_data = all_data.loc[other_index]

            train = pd.concat([train, train_data], ignore_index=True)
            if self.test_ratio == 0:
                # valid
                valid = pd.concat([valid, other_data], ignore_index=True)
            else:
                # valid
                new_valid_ratio = self.valid_ratio / (1 - self.train_ratio)
                valid_data = other_data.sample(
                    int(new_valid_ratio * len(other_data)), random_state=self.seed)

                # test
                valid_index, remaining_index = valid_data.index, other_data.index
                test_index = remaining_index.difference(
                    valid_index)  # 去除sample之后剩余的数据
                test_data = other_data.loc[test_index]

                valid = pd.concat([valid, valid_data], ignore_index=True)
                test = pd.concat([test, test_data], ignore_index=True)

        self.train_data = {"meta": self.column_meta,
                           "result": train.values.tolist()}
        self.valid_data = {"meta": self.column_meta,
                           "result": valid.values.tolist()}
        self.test_data = {"meta": self.column_meta,
                          "result": test.values.tolist()}
