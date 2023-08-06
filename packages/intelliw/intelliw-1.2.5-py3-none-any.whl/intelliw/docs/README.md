AI 工作坊脚手架
===============

欢迎使用用友AI工作坊脚手架，该脚手架提供了本地开发、调试、打包等基本功能，供开发者在**本地**开发调试。

环境要求
--------

脚手架依赖 python \>= 3.6，使用
pip进行包管理。开发者在**本地**调试时，需保证安装配置了正确的 python 环境。

脚手架使用
----------

### 环境准备

- 安装框架

  ```
  pip install intelliw -i https://pypi.python.org/simple/ -U
  ```

-   初始化算法文件
    生成算法文件框架，参数`name`为算法名称，默认值`example`,
    参数`output_path`为生成算法文件的位置，默认当前文件下。

    ```
    intelliw init --name test --output_path=/root/workspace/test/
    
    // 初始化之后生成以下结构 
          ├── algorithm.py          算法入口文件
          ├── algorithm.yaml        算法描述文件
          ├── README.md             项目描述文件
          ├── debug_contorler.py    本地开发测试文件
          ├── requirements.txt      python 依赖包
          └── docs                  算法框架使用说明
          		├── README.md       框架使用说明
          		└── instructions.md 算法文件说明
    ```
    
    
    
-   说明文档
    请参考 使用说明(docs/instructions.md)

        -   algorithm.py   说明文档
        -   algorithm.yaml 说明文档

*注： 以下功能使用框架包必须指定算法文件位置（--path/-p）*

### 算法导入

    intelliw import_alg --path ${algo_path}

### 模型导入

    intelliw import_model --path ${algo_path}

### 训练

本地训练时，训练数据只支持读取本地的 csv 文件，使用 `--csv`
参数指定文件路径。训练集与验证集的划分比例使用 `--train_ratio`
指定，默认是 0.7， 即训练集占 0.7，验证集占 0.3。以读取
`/data/export.csv` 文件为例，给出训练命令如下：

    intelliw train --path ${algo_path} --csv /data/export.csv --train_ratio 0.5

### 推理

本地推理时，算法框架会启动 HTTP 服务器处理推理请求，监听的端口可以使用
`--port` 指定，默认是 `8888`。以下示例会启动推理服务，并监听 `8000`
端口。

    intelliw infer --port 8000 --path ${algo_path}

推理服务启动后，可以调用推理接口，进行推理。推理接口是一个 `POST json`
接口，监听路径是 `/predict`，用户的请求需要封装在 `data` 字段中。
以下给出使用 `curl` 进行请求的示例命令，假设服务监听的是 `8000`
端口，需要传递的数据是 `[1.2, 2, true, "user"]`。

    curl -H "Content-Type:application/json" -X POST -d '{"data":[1.2, 2, true, "user"]}' http://localhost:8000/predict

### 打包

本地调试无误后，可使用脚本进行打包，生成的算法包/模型包路径可以使用
`--output_path` 参数指定，若不指定，默认会生成到 `target` 目录下。

生成算法包:

    intelliw  package_iwa --path ${algo_path} --output_path xxxx

生成模型包:

    intelliw package_iwm --path ${algo_path} --output_path xxxx

