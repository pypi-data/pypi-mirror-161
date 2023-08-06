'''
Author: hexu
Date: 2021-10-14 14:54:05
LastEditTime: 2022-07-27 14:59:55
LastEditors: Hexu
Description: 远程csv数据集
FilePath: /iw-algo-fx/intelliw/datasets/datasource_nlp_corpora.py
'''
import random
import shutil
import time
import os
import fileinput
import zipfile
from intelliw.datasets.datasource_base import AbstractDataSource
from intelliw.utils import iuap_request
from intelliw.utils.logger import get_logger
import traceback
from intelliw.utils.storage_service import StorageService
from intelliw.config import config
from intelliw.utils.exception import DatasetException
from intelliw.utils.util import unzip_file
from intelliw.datasets.spliter import get_set_count, check_split_ratio

logger = get_logger()


class CorpusType:
    csv = 'csv'
    json = 'json'
    txt = 'txt'

    TXT = 1
    CSV = 2
    JSON = 3

    ItoN = {1: "txt", 2: "csv", 3: "json"}


class DataSourceNLPCorpora(AbstractDataSource):
    """
    nlp语料处理
    """

    def __init__(self, source_address: str, ds_id: str, source_train_type: int, download_dir='./tmp_local_nlp_corpora_origin_data/'):
        self.ratio = [config.TRAIN_DATASET_RATIO,
                      config.VALID_DATASET_RATIO, config.TEST_DATASET_RATIO]
        check_split_ratio(*self.ratio)

        self.download_dir = download_dir
        self.source_address = source_address
        self.ds_id = ds_id
        self.source_train_type = source_train_type
        self._gen_corpora_dir()
        self._file_suffix = self._get_file_suffix(self.source_train_type)
        if self.source_address.startswith("http"):
            loacl_corpus = self.__download_file()
        else:
            loacl_corpus = config.NLP_CORPORS_PATH

        # self._csv_label self._file_list 顺序会有影响
        self._file_list = self._file_process(loacl_corpus)
        self._csv_label = self._get_csv_label()
        self._total = None
        self.random = random.Random(1024)
        self._file_batch = 5e4

        self.dirpath = [config.NLP_CORPORS_TRAIN_FILEPATH,
                        config.NLP_CORPORS_VAL_FILEPATH, config.NLP_CORPORS_TEST_FILEPATH]

    def total(self):
        return len(self._file_list)
        # from itertools import (takewhile, repeat)
        # buffer = 1024 * 1024
        # with open(self.__tmp_corpus_file_path) as f:
        #     buf_gen = takewhile(lambda x: x, (f.read(buffer)
        #                         for _ in repeat(None)))
        #     self.__total = sum(buf.count('\n') for buf in buf_gen)
        # for fpath in self._file_list:
        #     cmd = f"wc -l {fpath}"
        #     res = os.popen(cmd).read()
        #     self.__total += int(res.split()[0])
        # return self.__total

    def reader(self, pagesize=10000, offset=0, limit=0, transform_function=None):
        return list()

    def corpora_process(self, split_mode: int = 0):
        """nlp语料切分

        Args:
            split_mode (int, optional): 0顺序 1乱序. Defaults to 0.

        此方法中所有长度3的列表, 均代表 [训练, 验证, 测试]
        """
        start_time = time.time()
        # 切分函数的缓存, 减少切分次数
        spliter_cache = {}
        # dataset_class 一共有 训练 验证 测试 三种数据集
        dataset_class = 3
        # file_index 文件名称，self._file_batch行拆分一个
        file_index = [1]*dataset_class
        # counts 数据集总行数
        counts = [0]*dataset_class
        # io_reader 数据集写入文件io
        io_reader = []
        for i in range(dataset_class):
            file_path = os.path.join(
                self.dirpath[i], f"{file_index[i]}.{self._file_suffix}")
            io_reader.append(open(file_path, "w", encoding="utf-8"))
            if self._csv_label:
                io_reader[i].write(self._csv_label)

        # 进行多文件循环数据集拆分
        for epoch, part in enumerate(self._read_part(self._file_list)):
            # split_mode 根据拆分模式进行处理
            if split_mode:
                self.random.shuffle(part)
            part_count = len(part)

            # set_data 此part数据集原始数据
            set_data = [[]] * dataset_class
            if part_count >= 10:
                # nums 此part数据集数据条数
                nums = spliter_cache.get(part_count)
                if nums is None:
                    nums = get_set_count(part_count, *self.ratio)
                    spliter_cache[part_count] = nums
                set_data[0] = part[:nums[0]]
                if not nums[2]:
                    set_data[1] = part[nums[0]:]
                else:
                    set_data[1] = part[nums[0]:sum(nums[:2])]
                    set_data[2] = part[sum(nums[:2]):]
            else:
                set_data[0] = part
            part.clear()

            # 更新数据集总数据
            for idx, num in enumerate(nums):
                counts[idx] += num

            # 将数据写入对应文件
            [i.writelines(s) for i, s in zip(io_reader, set_data)]

            # 5轮刷新一次缓存区，减少内存压力
            if epoch and epoch % 5 == 0:
                [i.flush() for i in io_reader]

            # 根据数据条数,更新句柄
            for idx, count in enumerate(counts):
                if count > self._file_batch * file_index[idx]:
                    file_index[idx] += 1
                    file_path = os.path.join(
                        self.dirpath[idx], f"{file_index[idx]}.{self._file_suffix}")
                    io_reader[idx].close()
                    io_reader[idx] = open(file_path, "w", encoding="utf-8")
                    if self._csv_label:
                        io_reader[idx].write(self._csv_label)

            print(
                f"[Framework Log] corpora processing: train: {counts[0]} 条, validation: {counts[1]} 条, test: {counts[2]} 条", end='\r', flush=True)

        # 关闭所有句柄
        [io.close() for io in io_reader]
        logger.info(
            f"corpora processed: total: {sum(counts)} 条,  train: {counts[0]} 条, validation: {counts[1]} 条, test: {counts[2]} 条, time: {time.time()-start_time}")

        # 清空下载文件夹
        shutil.rmtree(self.download_dir)

    def _gen_corpora_dir(self):
        logger = get_logger()
        filepath = os.path.join('./', config.NLP_CORPORS_FILEPATH)
        if os.path.exists(filepath):
            logger.warn(f"语料数据保存路径存在:{filepath}, 正在删除路径内容")
            shutil.rmtree(filepath, ignore_errors=True)
        os.makedirs(self.download_dir, 0o755, True)
        os.makedirs(config.NLP_CORPORS_TRAIN_FILEPATH, 0o755, True)
        os.makedirs(config.NLP_CORPORS_VAL_FILEPATH, 0o755, True)
        os.makedirs(config.NLP_CORPORS_TEST_FILEPATH, 0o755, True)

    def _read_part(self, file_paths, size=5000, encoding="utf-8"):
        hook = fileinput.hook_encoded(encoding=encoding)
        with fileinput.input(files=file_paths, openhook=hook) as f:
            while True:
                part = []
                for _ in range(size):
                    try:
                        t = f.__next__()
                        if f.isfirstline() and self._file_suffix == CorpusType.csv:
                            continue
                        part.append(t)
                    except StopIteration:
                        if part:
                            break
                        else:
                            return
                yield part

    def __download_file(self):
        start_time = time.time()
        logger.info('Downloading nlp corpora from %s to %s',
                    self.source_address, self.__tmp_corpus_file_path)

        # 1 获取s3链接
        request_data = {'dsIds': self.ds_id,
                        'type': self.source_train_type, 'tenantId': config.TENANT_ID}
        response = iuap_request.post_json(
            url=self.input_address, json=request_data)
        response.raise_for_status()
        file_links = response.json

        # 1.5 如果是文件 or 如果是zip
        # self._file_suffix = zip

        # 2 下载文件
        for idx, link in enumerate(file_links):
            filename = os.path.join(
                self.download_dir, f"{idx}.{self._file_suffix}")
            try:
                downloader = StorageService(
                    link, config.FILE_UP_TYPE, "download")
                downloader.download(filename, stream=True)
                logger.info(f"NLP语料下载成功, 耗时:{time.time()-start_time}s")
            except Exception as e:
                err = traceback.format_exc()
                raise DatasetException(f"NLP语料下载失败: {err}")
        return self.download_dir

    def _file_process(self, path):
        if zipfile.is_zipfile(path):
            logger.info("解压语料文件")
            dirpath = unzip_file(path)
        elif os.path.isdir(path):
            dirpath = path
        else:
            raise DatasetException(f"不支持的文件格式{path}")
        # 读取文件夹， 筛选文件
        file_list = []

        def get_file(d, f):
            for i in os.listdir(d):
                p = os.path.join(d, i)
                if i.endswith(self._file_suffix):
                    f.append(p)
                elif os.path.isdir(p):
                    get_file(p, f)
            return f

        file_list = get_file(dirpath, file_list)

        if len(file_list) == 0:
            raise DatasetException(
                f"未获取语料文件， 文件格式应为 .{self._file_suffix} 后缀文件")

        return file_list

    def _get_csv_label(self):
        # 获取csv表头
        if self._file_suffix == CorpusType.csv:
            fp = open(self._file_list[0], encoding='utf-8')
            csv_label = fp.__next__()
            fp.close()
            return csv_label
        else:
            return None

    def _get_file_suffix(self, source_train_type):
        if source_train_type not in CorpusType.ItoN.keys():
            raise DatasetException(
                f"NLP语料类型错误: CorpusType is {source_train_type}, 1-txt 2-csv 3-json")
        return CorpusType.ItoN[source_train_type]

    def __call__(self):
        abspath = os.path.abspath('.')
        return {'path': os.path.join(abspath, config.NLP_CORPORS_FILEPATH),
                'train_set': os.path.join(abspath, config.NLP_CORPORS_TRAIN_FILEPATH),
                'val_set': os.path.join(abspath, config.NLP_CORPORS_VAL_FILEPATH),
                'test_set': os.path.join(abspath, config.NLP_CORPORS_TEST_FILEPATH)}
