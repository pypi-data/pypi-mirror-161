# 算法框架使用手册

## 1.  流程概述

算法平台支持开发者导入算法包或模型包。

### 1.1  算法导入

开发者自行导入算法包的使用流程如下所示。开发者导入编写的算法包，平台校验确认算法包符合要求后，开发者可以使用导入的算法包创建模型。创建好的模型可以在平台进行训练。模型训练好后，开发者可以将该模型上线，成功上线后，即可使用该服务进行推理。

```
导入算法 -> 新建模型 -> 训练 -> 推理
```



### 1.2 模型导入

开发者导入模型包的使用流程如下所示。开发者编写、训练好模型包后，将模型包导入算法平台，平台校验确认算法包符合要求后，开发者可以使用导入的模型包上线，成功上线后，即可使用该服务进行推理。

```
导入模型 -> 推理
```



### 1.3  应用导入

开发者导入模型包使用流程如下所示。开发者导入模型包，上线即可使用。

```
导入应用 -> 上线
```



## 2. 算法包

### 2.1  算法包目录结构

一个典型的算法包目录结构如下图所示:

```
${my algorithm}  
    ├── algorithm.py          算法入口文件
    ├── algorithm.yaml        算法描述文件
    ├── README.md             项目描述文件
    ├── debug_contorler.py    本地开发测试文件
    ├── requirements.txt      python 依赖包
    └── docs                  算法框架使用说明
        ├── README.md         框架使用说明
        └── instructions.md   算法文件说明
```

- `algorithm.py` 是算法文件，用户编写的主要逻辑入口在这个文件中。
- `algorithm.yaml` 是算法的描述文件，这个文件定义了算法的基本信息，是算法包的元数据描述。
- 用户代码中需要依赖的python 包，可以在 `requirements.txt` 中声明，平台在加载用户的算法包时，会根据该文件安装依赖包。
- 如果用户需要使用自定义的镜像，可以提供 `Dockerfile`，平台会使用该 `Dockerfile` 来构建运行算法包的镜像。

各文件说明如下表所示：

| 文件             | 必须 | 说明                     |
| ---------------- | ---- | ------------------------ |
| algorithm.py     | Y    | 算法入口文件             |
| algorithm.yaml   | Y    | 算法描述文件             |
| requirements.txt | N    | 算法包python库依赖文件   |
| Dockerfile       | N    | 算法包自定义镜像构建文件 |
| README.md        | N    | 算法说明文件             |



### 2.2  算法描述文件·`algorithm.yaml`

`algorithm.yaml` 是算法描述文件，该文件对算法进行了基本描述，包括算法的基本信息、特征工程转换函数、超参数定义、推理API等，是算法的元数据描述。

算法描述文件使用 YAML格式，各字段定义详见下表：

*Algorithm*：

| 参数                    | 参数说明                                   | 必填 | 类型   | 示例数据               |
| ----------------------- | ------------------------------------------ | ---- | ------ | ---------------------- |
| Algorithm.name          | 算法包名称                                 | Y    | string | demo_algorithm         |
| Algorithm.desc          | 算法描述                                   | Y    | string | 示例算法               |
| Algorithm.example       | 示例调用代码                               | N    | string |                        |
| Algorithm.ref           | 算法url（如 wiki 页面、github 页面等 url） | N    | sring  | https://www.diwork.com |
| Algorithm.requestMem    | 算法运行内存最小值                         | N    | string | 256m                   |
| Algorithm.isGpu         | 算法运行是否使用GPU                        | N    | bool   | false                  |
| Algorithm.isDistributed | 算法运行是否使用分布式                     | N    | bool   | false                  |

*Algorithm.router[]*：

| 参数                            | 参数说明                                           | 必填 | 类型         | 示例数据            |
| ------------------------------- | -------------------------------------------------- | ---- | ------------ | ------------------- |
| Algorithm.router[]              | 算法上线后的推理接口                               | N    | object array |                     |
| Algorithm.router[].path         | 接口api                                            | Y    | string       | /api/demo/infer     |
| Algorithm.router[].func         | 接口调用的推理函数（函数需要在algorithm.py中实现） | Y    | string       | infer               |
| Algorithm.router[].desc         | 接口描述                                           | N    | string       | 推理接口api         |
| Algorithm.router[].method       | 请求方式                                           | N    | string       | get/post/put/delete |
| Algorithm.router[].need_featrue | 请求数据是否需要进行特征处理                       | N    | bool         | false               |

*Algorithm.algorithm[]*：

| 参数                                                  | 参数说明                                                                             | 必填 | 类型                  | 示例数据     |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------ | ---- | --------------------- | ------------ |
| Algorithm.algorithm                                   | 算法详细描述                                                                         | Y    | Object                |              |
| Algorithm.algorithm.desc                              | 算法描述                                                                             | Y    | string                | 示例算法     |
| Algorithm.algorithms.transforms[]                     | 特征工程函数定义                                                                     | Y    | object array          |              |
| Algorithm.algorithms.transforms[].type                | 特征工程函数阶段，支持 pre-train：训练前， pre-predict：推理前，post-predict：推理后 | Y    | string                | pre-train    |
| opetion.min                                           |                                                                                      |      |                       |              |
| Algorithm.algorithms.transforms[].functions[]         | 具体特征工程函数                                                                     | Y    | object array          |              |
| Algorithm.algorithms.transforms[].key                 | 特征工程函数名，即函数签名的函数名称                                                 | Y    | string                | convert_data |
| Algorithm.algorithms.transforms[].name                | 特征工程函数名称                                                                     | Y    | string                | 特征转换     |
| Algorithm.algorithms.transforms[].desc                | 特征工程函数描述                                                                     | N    | string                | 特征转换     |
| Algorithm.algorithms.transforms[].can_split           | 此函数是否按行处理数据                                                               | N    | false                 | true         |
| Algorithm.algorithms.transforms[].parameters[]        | 特征工程函数参数定义                                                                 | N    | object array          |              |
| Algorithm.algorithms.transforms[].parameters[].key    | 特征工程函数参数key                                                                  | Y    | string                | parameter_1  |
| Algorithm.algorithms.transforms[].parameters[].name   | 特征工程函数参数名称                                                                 | Y    | string                | 特征转换参数 |
| Algorithm.algorithms.transforms[].parameters[].val    | 特征工程函数参数当前值                                                               | N    | string/number/boolean | hello        |
| Algorithm.algorithms.transforms[].parameters[].option | 特征工程函数参数配置项，详见参数配置项说明                                           | N    | object                |              |
| Algorithm.algorithms.parameters[]                     | 算法超参数                                                                           | Y    | object array          |              |
| Algorithm.algorithms.parameters[].key                 | 算法超参数key                                                                        | Y    | string                | parameter_2  |
| Algorithm.algorithms.parameters[].name                | 算法超参数名称                                                                       | Y    | string                | 参数2        |
| Algorithm.algorithms.parameters[].val                 | 算法超参数当前值                                                                     | N    | string/number/boolean | 123          |
| Algorithm.algorithms.parameters[].option              | 算法超参数配置项，详见参数配置项说明                                                 | N    | object                |              |

*Algorithm.algorithms.transforms\[\].parameters\[\].option，与Algorithm.algorithms.parameters\[\].option 中的参数定义如下表所示*：
| 参数                | 参数说明                                                       | 必填 | 类型                  | 示例数据 |
| ------------------- | -------------------------------------------------------------- | ---- | --------------------- | -------- |
| option.type         | 参数类型，目前支持 string、booean、integer、double、array(int) | Y    | string                | integer  |
| option.defaultValue | 参数默认值                                                     | N    | string/number/boolean | 1        |

开发者上传完毕算法包，创建数据模型是可以配置配置文件中定义的参数，平台会根据option 中的配置，选取合适的控件进行展示校验。

一个简单的算法描述文件示例如下：

```
AlgorithmInformation:
  name: "demo-algorithm"
  desc: "示例算法"
  example: ""
  ref: "http://github.com/microsoft/LightGBM"
  isGpu: true
  isDistributed: true
  requestMem: "512M"
  algorithm:
    desc: "示例算法"   
    transforms:
    - type: "pre-train"
      functions:
      - desc: "数据增强"
        name: "数据增强"
        key: "convert_data"
        parameters:
        - key: "convert_data_param"
          desc: "数据增强参数"
          name: "数据增强参数"
          val: true
          option:
            defaultValue: true
            type: "boolean"
    parameters:
    - key: "hyper_parameter_1"
      name: "超参数1"
      desc: "超参数1"
      val: true
      option:
        defaultValue: true
        type: "boolean"
```





### 2.3  算法入口文件 algorithm.py

#### 2.3.1 概述

algorithm.py 是算法入口文件，开发者的主要入口逻辑需在该文件中实现，平台读取并运行该文件，实现训练、推理等逻辑。algorithm.py 文件中需要定义 `Algorthm` 类，该类定义如下所示。开发者根据需求去实现其中特定函数。

```
class Algorithm:
    """
    算法类， 导入的算法必须定义class Algorithm， 并放入 algorithm.py 文件中
    """

    def __init__(self, parameters):
        """
        初始化， parameters 为 dict格式的参数信息， 比如
        {
            "params1": "value1",
            "params1", 2
        }
        """
        self.parameters = parameters
        self.logger = self.parameters['framework_log']   # 日志
        pass

    def load(self, path):
        """
        加载模型
            不需要调用，只需要在这里实现加载模型的方法，并赋值给一个属性就可以，例如：
            self.model = xxxx.load(path)
            上线流程：算法框架会将模型文件放在model/下，然后进行函数的执行
            本地流程：可以通过model.yaml中location字段进行配置，然后会传入path参数
            Args:
                path : 模型文件路径，根据 model.yaml 文件中的 location 字段指定
            Returns:
                无
        """
        pass

    def save(self, path):
        """
        保存模型， 保存为 path 的文件或文件夹会被框架程序自动打包上传到服务器
        如果是path是文件夹，需要加上/， 系统会创建该文件夹
            Args:
                path : 模型文件路径， 文件名或文件夹名，根据算法自定义
            Returns:
                无
        """
        pass

    def train(self, train_data, val_data, **kwargs):
        """
        模型训练
            Args:
                self.train_set 或 train_data : 训练数据
                self.valid_set 或 val_data : 验证数据
                self.test_set : 测试数据
                [{
                    "meta": [   // 表头
                        {"code": "column_a"},
                        {"code": "column_b"}
                    ],
                    "result": [ // 表体
                        ["line_1_column_1", "line_1_column_2"],
                        ["line_2_column_1", "line_2_column_2"]
                    ]
                },...]

                kwargs: 特征工程后返回的数据
                {
                    "final_target_col": 3,       // 目标列下标
                    "category_cols": [1,2,3]     // 类别列下标
                    "column_meta": [Employee_ID,Gender,Age,...]    // 原始数据的列名
                    "column_relation_df": Dataframe   // the map between the input columns and output columns, if column is droped, it will not exist in column_relation_df!
                }
            Returns:
                无
        """
        pass
```



#### 2.3.2 函数调用过程

```
# 算法包Algorithm调用过程
# 导入算法包
	-> __init__
# 训练
	-> __init__ 
	-> pre-train transfrom functions 
	-> train(
	   		  -> report_train_info 
	   		  -> sava 
	   		  -> report_val_info
	   		)
# 推理
	-> __init__ 
	-> load
	-> pre-predict transfrom functions 
	-> infer
	-> post-predict transfrom functions
```

对于导入的算法包，平台会在特定业务逻辑中调用特定的函数，其主要业务与调用函数的调用关系如上所示。

- 导入算法包环节，平台会实例化开发者实现的 `Algorithm` 类，调用该类的`__init__`构造函数，以验证该算法文件可以正常加载。

- 训练环节，平台首先会实例化开发者实现的 `Algorithm` 类，调用构造函数`__init__` 方法。实例化成功后，平台根据用户的配置加载训练数据，如果用户在 `algorithm.yaml` 中定义了`pre-train` 环节的特征工程函数，算法框架会调用`algorithm.py` 文件或模块中定义的对应函数。数据经过特征工程函数处理后，平台会调用`train`函数，开发者需要在该函数中实现主要训练逻辑。训练过程中，开发者可以调用`report_train_info`上报训练过程中的`loss`、`lr`等训练过程数据。训练得到的模型，开发者需要在`save` 方法中进行保存。开发者将模型保存逻辑实现在`save`函数中，并在`train`方法中调用。平台会将用户保存的模型文件保存到云端。得到训练模型后，用户可以对模型进行验证，验证的结果通过调用`report_val_info `进行上报。

- 推理环节，平台首先会实例化开发者实现的 `Algorithm` 类，调用构造函数`__init__ `方法。实例化成功后，框架会调用`load`函数，来加载训练环节保存的模型文件。模型加载成功后，视为模型上线成功。用户不论是通过暴露的API调用还是定时调用，算法框架会调用用户编写的infer函数，进行推理。调用infer函数前，如果用户在`algorithm.yaml `文件中定义了`pre-predict` 环节的特征工程函数，平台会将输入的数据传递给定义的特征工程函数。特征工程函数调用完毕后，平台会调用开发者编写的`infer`函数，开发者在该函数中实现推理逻辑，并返回推理结果。如果开发者定义了`post-predict`环节的特征工程函数，平台会使用开发者返回的推理结果作为参数调用对应的特征工程函数。

#### 2.3.3 函数说明

##### 2.3.3.1 `__init__ (self, parameters)`

该函数是`Algorithm`的构造函数，`parameters`是开发者在`algorithm.yaml`中定义的超参数。`parameters` 是一个`dict`，其键为描述文件定义的`Algorithm.algorithms.parameters[].key`，其值为用户在训练时配置的超参数值， 在算法框架启动时，会根据配置文件进行参数类型转换，并将实例化后的`logger`放入`parameters`，使用时直接通过`parameters.get('framework_log')`获取。

##### 2.3.3.2 `load(self, path)`

开发者需要在`load`函数中实现模型加载逻辑，推理上线过程中，算法框架会调用该方法，执行用户定义的模型加载逻辑。模型文件的绝对路径会在`path`参数中传递。该模型文件是用户在训练过程中产生的，平台会在推理时将模型文件加载到path。

##### 2.3.3.3 `save(self, path)`

`save`函数是模型保存函数，开发者需要将用户的模型保存逻辑在该函数中进行实现，并在训练结束后调用该方法保存模型。`path` 是模型保存路径，用户可以使用相对路径保存到算法包所在的某个路径下，平台根据会将该路径下生成的模型文件打包上传，保存至云端。

##### 2.3.3.3 `train(self, **kwargs)`

*注*： 以下格式只针对表格数据， cv, nlp 类请参考 [数据集](#dataset)

`train` 函数是训练入口函数，开发者需要在该函数中实现训练逻辑。`self.train_set` 是训练集，该参数是一个`iterable`对象，开发者可以对其迭代来获取训练数据。训练数据格式如下所示：

```
{   
    // 表头
    "meta": [  
        {"code": "column_a"},
        {"code": "column_b"}
    ],
    // 表体
    "result": [ 
        ["line_1_column_1", "line_1_column_2"],
        ["line_2_column_1", "line_2_column_2"]
    ]
}
```

每次迭代`self.train_set` 都会返回如上的一个`dict`，其中 `meta` 是数据的元数据描述，其中`code` 是列名，不同类型的数据源`meta`字段内容可能会不同，但是一定有`code`字段。`result `是数据集每一行的数据。开发者可以使用这些数据进行训练。
`self.valid_set` 是验证集,`self.test_set` 是验证集, 其数据格式与训练集一致。数据集在平台的训练配置过程中进行配置，框架会根据开发者配置的比例切分数据集。

`**kwargs`:特征工程后返回的数据, 内容如下：
```
{
    "final_target_col": 3,       // 目标列下标
    "category_cols": [1,2,3]     // 类别列下标
    "column_meta": [Employee_ID,Gender,Age,...]    // 原始数据的列名
    "column_relation_df": Dataframe   // the map between the input columns and output columns, if column is droped, it will not exist in column_relation_df!
}
```

训练结束后，开发者需要在该函数调用`save`方法来保存模型。训练过程的`loss`、`lr`等数据可以调用`report_train_info`进行上报，模型验证结果可以调用`report_val_info`函数进行上报。

##### 2.3.3.4 `infer(self, infer_data)`

`infer` 函数是推理函数，开发者需要在函数中实现推理逻辑。参数`infer_data`是json输入数据。对于API调用，该参数的格式如下所示：

```
  infer_data : 推理请求数据, json输入的参数, 类型可以为列表/字符串/字典

  self.request              object: 请求体
    |- self.request.header  object: 请求头
    |- self.request.files   List[file]: form-data 文件列表
    |- self.request.query   Dict: url参数
    |- self.request.form    Dict: form表单参数
    |- self.request.json    object: json参数
```

用户可以在data中获取推理输入数据， 请求的相关参数会存储在self.request中，数据参数和用户定义一致

用户调用模型获得的推理结果作为返回值返回给框架。对于API类型的调用，算法框架会将推理结果返回给调用方，对于定时推理类型的调用，算法框架会将返回值写入用户指定的数据源。

执行推理操作时，`infer` 函数的返回值会被序列化为`json` 格式后返回给用户，因此`infer` 函数的返回值必须是可以被 `json.dumps` 序列化的。

*注*：
如果使用特征工程，infer_data格式有硬性要求
```
{
    "data":           任意格式，如果配置特征工程，此数据为处理后的数据 
    "original_data":  原始输入的data ，防止数据在通过特征处理后丢失原先的数据
}
```

**自定义推理函数API的方法**：

1. 调用算法包方法Application来设置路由：  
| 参数         | 必须 | 类型   | 默认值 | 说明                                                            | 示例              |
| ------------ | ---- | ------ | ------ | --------------------------------------------------------------- | ----------------- |
| path         | Y    | 字符串 |        | 访问路由                                                        | "/infer-api"      |
| method       | N    | 字符串 | post   | 访问方式，支持 get post push delete head patch options          | method='get'      |
| need_featrue | N    | bool   | True   | 是否需要使用特征工程，如果是自定义与推理无关的函数，请设置False | need_featrue=True |

  ```
  from intelliw.feature import Application

  @Application.route("/infer-api", method='get', need_featrue=True)
  def infer(self, test_data):
      pass
  ```



2. 通过algotiyhm.yaml下Algorithm.router[]进行参数配置
| 参数         | 必须 | 类型   | 默认值 | 说明                                                            | 示例              |
| ------------ | ---- | ------ | ------ | --------------------------------------------------------------- | ----------------- |
| path         | Y    | 字符串 |        | 访问路由                                                        | path: "/predict"  |
| func         | Y    | 字符串 |        | 路由访问的algorithm.py中的函数                                  | func: "infer"     |
| method       | N    | 字符串 | post   | 访问方式，支持 get post push delete head patch options          | method: "get"     |
| need_featrue | N    | bool   | True   | 是否需要使用特征工程，如果是自定义与推理无关的函数，请设置False | need_featrue=True |
  ```
    router:
    - path: "/predict"
      func: "infer"
      method: "get"
      need_featrue: ""
      desc: ""
  ```


3. 不设置默认会给algorithm.py下的infer函数设置post方法的路由/predict

##### 2.3.3.5 `report_train_info(self, loss, lr, iter, batchsize=1)`

该函数是训练信息上报函数，开发者不需要实现该函数，只需要在训练过程中调用该函数即可。该函数参数定义如下，其中`loss`是损失函数的`loss`值，`lr`是学习率，`iter`是当前的`iteration`，`batchsize`是每批训练数据大小。

##### 2.3.3.6 `report_val_info(self, **kwargs)`

该函数是评估结果上报函数，开发者不需要实现该函数，只需要在训练结束后根据自身需求调用该函数传递评估结果。评估结果参数以 `kwargs` 的形式传递，当前平台支持的参数定义如下表所示。开发者可以传递感兴趣的评估结果进行上报，平台会在模型服务的评估结果页面对上报结果进行展示。

| 参数名                  | 描述             |
| ----------------------- | ---------------- |
| truePositiveRate        | 真阳性率         |
| falsePositiveRate       | 伪阳性率         |
| trueNegativeRate        | 真阴性率         |
| falseNegativeRate       | 伪阴性率         |
| truePositiveSample      | 真阳性数         |
| falsePositiveSample     | 伪阳性数         |
| trueNegativeSample      | 真阴性数         |
| falseNegativeSample     | 伪阴性数         |
| accuracy                | 准确率           |
| precision               | 精确率           |
| recall                  | 召回率           |
| f1Score                 | F1值             |
| auc                     | AUC值            |
| logLoss                 | LogLoss值        |
| rocCurve                | Roc曲线          |
| silhouette_score        | 轮廓系数         |
| calinski_harabasz_score | CH分数           |
| mae                     | MAE 平均绝对误差 |
| mse                     | MSE 均方误差     |
| rmse                    | RMSE 均方根误差  |


其中，`rocCurve` 需要以`dict `的形式进行传递，示例数据如下：
```
{
    "rocX": [0.1, 0.2],
    "rocY": [0.1, 0,2]
}
```



##### 2.3.3.7 特征工程函数

开发者可以根据自身算法需要，编写特征工程函数，来对训练数据、推理数据进行预处理、后处理。

特征工程函数需要定义在`Algorithm`类之外，算法框架会根据开发者在`algorithm.yaml`定义的特征工程函数的`key`在`algorithm.py`中查找加载。

一个典型的特征工程函数如下所示：
```
def convert_data(data, params):
	# do something with data
	return data
```

在进行训练或推理前，算法框架会调用特征工程函数。调用时，会传递两个位置参数，第一个参数是当前处理的数据，第二个参数是开发者配置的特征工程函数的参数，上述示例中分别取名为`data`和`params`。其中，`params` 参数格式同`__init__`方法中传递的超参数格式，`data`格式根据特征工程函数所处的调用环节有所不同：

- 对于`pre-train` 阶段的特征工程函数，用户每次对`train_data`或`val_data`迭代读取时，读取到的结果会首先传递给特征工程函数做处理，其格式同train环节获取的数据格式。用户可以对`result`中的数据进行加工。处理完毕后，需要返回处理后的结果，其格式需要与入参保持一致。

- 对于`pre-predict`阶段的特征工程函数，`data`格式根据推理任务不同有所不同，其格式与`infer`函数的`test_data`一致，调用`infer`函数前，算法框架会将`test_data`传递给特征工程函数，再将特征工程函数的返回值传递给`infer`函数。

- `post-predic`t阶段的特征函数，其`data`为`infer`函数的返回值。

#### 2.3.4 构造算法包

编写好算法包后，开发者可以通过算法框架对算法文件夹打包

```
intelliw  package_iwa --path ${算法文件路径} --output_path xxxx
```




## 3. 模型包

### 3.1 模型包格式

一个典型的模型包目录结构如下所示：

```
${my model}  
    ├── model      
    |	└── gbm.model
    ├── algorithm.py      
    ├── algorithm.yaml    
    ├── model.yaml        
    ├── README.md         
    └── requirements.txt  
```

模型包目录结构与算法包类似，主要不同是增加了模型描述文件`model.yaml`。同时，开发者可能将训练好的模型文件放置在模型包内，上述示例中，`model` 目录即为模型文件目录。模型文件目录可在`model.yaml` 中进行配置。

各文件说明详见下表：
| 文件             | 必须 | 说明                   |
| ---------------- | ---- | ---------------------- |
| algorithm.py     | Y    | 算法入口文件           |
| algorithm.yaml   | Y    | 算法描述文件           |
| model.yaml       | Y    | 模型配置文件           |
| requirements.txt | N    | 算法包python库依赖文件 |
| README.md        | N    | 算法说明文件           |


### 3.2 模型配置文件 `model.yaml`

`model.yaml`是模型配置文件。`algorithm.yaml`描述了算法的基本能力，如支持的特征函数、支持的超参数等，而`model.yaml`描述了算法的具体运行时，给出了可配置项的具体值，如加载模型文件的路径、启用哪些特征函数、超参数的具体值等。

*注：使用算法框架本地进行训练时会自动通过`algorithm.yaml`生成`model.yaml`*

模型描述文件使用YAML格式，各配置项如下表：
| 参数                                  | 参数说明                                                                            | 必填 | 类型                  | 示例数据          |
| ------------------------------------- | ----------------------------------------------------------------------------------- | ---- | --------------------- | ----------------- |
| Model.name                            | 模型包名称                                                                          | Y    | string                | demo_model        |
| Model.desc                            | 模型包描述                                                                          | Y    | string                | 示例模型          |
| Model.requestMem                      | 算法运行内存最小值                                                                  | N    | string                | 256m              |
| Algorithm.isGpu                       | 算法运行是否使用GPU                                                                 | N    | bool                  | false             |
| Algorithm.isDistributed               | 算法运行是否使用分布式                                                              | N    | bool                  | false             |
| Model.location                        | 模型文件路径                                                                        | Y    | string                | ./model/gbm.model |
| Model.algorithm                       | 模型使用的算法                                                                      | Y    | object                |
| Model.algorithm.name                  | 算法名称                                                                            | Y    | string                | demo_algorithm    |
| Model.algorithm.desc                  | 算法描述                                                                            | Y    | string                | 示例算法          |
| Model.transforms[]                    | 模型包启用的特征函数，特征函数需在algoritm.yaml中定义                               | Y    | object array          |
| Model.transforms[].type               | 特征工程函数阶段，支持 pre-train：训练前，pre-predict：推理前，post-predict：推理后 | Y    | string                | pre-train         |
| Model.transforms[].functions[]        | 启用的特征工程函数                                                                  | Y    | object array          |
| Algorithm.algorithms.transforms[].key | 特征工程函数名，即函数签名的函数名称                                                | Y    | string                | convert_data      |
| Model.transforms[].parameters[]       | 特征工程函数参数配置                                                                | N    | object array          |
| Model.transforms[].parameters[].key   | 特征工程函数参数key                                                                 | Y    | string                | parameter_1       |
| Model.transforms[].parameters[].val   | 特征工程函数参数值                                                                  | N    | string/number/boolean | hello             |
| Algorithm.algorithms.parameters       | 算法超参数配置，以key/value形式配置                                                 | Y    | object                | arg_1: true       |

一个简单的模型描述文件示例如下，该描述文件指定了模型加载路径：`" ./model/gbm.model"`，指定了算法在`pre-predict`阶段要启用`convert_data`特征工程函数，且为该函数传递了配置项`convert_data_param`，其值为`true`。同时，为算法配置了三个超参数：`parameter_a`，`param_2`，`param_3`。

```
Model:
  name: "lightgbm"
  desc: "lightgbm测试用例"
  isGpu: true
  isDistributed: true
  requestMem: "256M"
  location: "./model/gbm.model" #  保存的模型文件路径
  algorithm:
    name: "lightgbm"
    desc: "流程测试算法"
  transforms:
  - type: "pre-predict"
    functions:
    - key: "convert_data"
      parameters:
      - key: "convert_data_param"
        val: true
  parameters:
    parameter_a: treu
    param_2: 123
    param_3: "hello"

```



### 3.3 模型执行过程

```
# 导入模型
	-> __init__
	-> load
# 推理
	-> __init__ 
	-> load
	-> pre-predict transfrom functions 
	-> infer
	-> post-predict transfrom functions
```

开发者编写的`Algorithm`类在模型包各业务环节中调用流程如上图所示。导入模型包时，会实例化`Algorithm`类，调用其`__init__`方法，之后，会调用`load`方法加载模型，`load`方法执行成功后，视为导入模型成功。上线推理时，算法框架首先会实例化`Algorithm`类，调用其`__init__`方法，并调用`load`方法加载模型。如果开发者配置了`pre-predic`t阶段的特征工程函数，推理输入数据在调用`infer`函数前传递给`pre-predict`的特征工程函数。特征工程函数处理后，算法使用该数据调用`infer`函数。如果用户定义了`post-predict`阶段的特征工程函数，`infer`函数的返回数据会传递给`post-predict`特征工程函数处理，处理后的结果返回给调用者。

### 3.4 构造模型包

编写好模型包后，开发者可以通过算法框架进行对算法文件夹打包

```
intelliw  package_iwm --path ${算法文件路径} --output_path xxxx
```



## 4. 应用包
 ### 4.1 应用包格式

一个典型的应用包目录结构如下所示：

```
${my app}  
    ├── app.yaml      
    ├── my_app.jar      
    └── Dockerfile        
```

`app.yaml`是模型包描述文件，该文件描述了应用的基本信息。如果用户需要算法平台打包，可以提供`Dockerfile`文件，算法平台会使用该`Dockerfile`和应用包中的文件打包。
| 文件       | 必须 | 说明               |
| ---------- | ---- | ------------------ |
| app.yaml   | Y    | 应用包描述文件     |
| Dockerfile | N    | 应用包镜像构建文件 |


### 4.2 应用描述文件 `app.yaml`

`app.yaml` 是应用描述文件，平台根据该文件运行应用。

配置文件配置项如下表所示：


| 参数                    | 参数说明               | 必填 | 类型   | 示例数据                                    |
| ----------------------- | ---------------------- | ---- | ------ | ------------------------------------------- |
| App.name                | 应用名称               | Y    | string | youycTag                                    |
| App.desc                | 应用描述               | Y    | string | 采购标签应用                                |
| App.requestMem          | 应用运行内存最小值     | N    | string | 512M                                        |
| Algorithm.isGpu         | 算法运行是否使用GPU    | N    | bool   | false                                       |
| Algorithm.isDistributed | 算法运行是否使用分布式 | N    | bool   | false                                       |
| App.image               | 应用镜像地址           | N    | string | hub.yonyou.com/intelliw/youyc/youyc_tag:1.0 |
| App.env                 | 应用环境变量配置       | Y    | object |                                             |
| App.env.service.port    | 服务暴露端口号         | Y    | int    | 8080                                        |

其中，`App.image` 是应用镜像地址，如果开发者配置了该地址，算法平台会在上线是加载该镜像，如果没有配置该地址，平台会使用应用包中的`Dockerfile`构建镜像。`App.env` 是应用的环境变量，开发者填写的环境变量平台会在启动应用时进行传递。`service.port`是一个特殊的环境变量，其含义是服务暴露端口，平台会将该端口向外网暴露。

一个简单的算法包示例如下：
```
App:
  name: "yonycTag"
  desc: "采购标签应用"
  requestMem: 512M
  isGpu: true
  isDistributed: true
  image: hub.yonyou.com/intelliw/youyc/youyc_tag:1.0
  envs:
    server.port: 8081
    system.code: yonycTagApp
```

### 4.3 构造应用包

编写好应用包后，开发者可以通过算法框架进行对算法文件夹打包

```
intelliw  package_iwp --path ${算法文件路径}  --output_path xxxx
```


     
<a id="dataset"></a>
## 5. 数据集

### 5.1 表格数据集
`self.train_set` 是训练集，该参数是一个`iterable`对象，开发者可以对其迭代来获取训练数据。训练数据格式如下所示：
```
{   
    // 表头
    "meta": [  
        {"code": "column_a"},
        {"code": "column_b"}
    ],
    // 表体
    "result": [ 
        ["line_1_column_1", "line_1_column_2"],
        ["line_2_column_1", "line_2_column_2"]
    ]
}
```

每次迭代`self.train_set` 都会返回如上的一个`dict`，其中 `meta` 是数据的元数据描述，其中`code` 是列名，不同类型的数据源`meta`字段内容可能会不同，但是一定有`code`字段。`result `是数据集每一行的数据。开发者可以使用这些数据进行训练。
`self.valid_set` 是验证集,`self.test_set` 是验证集, 其数据格式与训练集一致。数据集在平台的训练配置过程中进行配置，框架会根据开发者配置的比例切分数据集。

### 5.2 图片数据集格式
`self.train_set`， `self.valid_set`，`self.test_set` 均为数据集路径，格式为:  
```
{
    'path': '/{dirpath}/tmp_local_cv_image_data/', 
    'train_set': '/{dirpath}/tmp_local_cv_image_data/train/', 
    'val_set': '/{dirpath}/tmp_local_cv_image_data/val/', 
    'test_set': '/{dirpath}/tmp_local_cv_image_data/test/', 
    'annotations': '/{dirpath}/tmp_local_cv_image_data/annotations/'
}
```


图片存储在当前目录下 
```
./tmp_local_cv_image_data
    |-- train    训练集
    |-- val      验证集
    |-- test     测试集
    |-- annotations 标注信息
```

一般标注格式：
```
./tmp_local_cv_image_data     
    |-- train    训练集        
    |     |--- 1.jpg
    |     |--- 2.jpg
    |-- val      验证集        
    |     |--- 3.jpg
    |     |--- 4.jpg
    |-- test     测试集
    |     |--- 5.jpg
    |-- annotations 标注信息    
          |--- 1.json/xml
          |--- 2.json/xml
```

coco专属标注格式
标注文件来自coco官方格式，请按照官方规定使用
```
annotation demo:
{'licenses':{}, 'info':{}, 'categories':{}, 'images':[], 'annotations':[]}

./tmp_local_cv_image_data
    |-- train    训练集
    |     |--- 1.jpg
    |     |--- 2.jpg
    |-- val      验证集
    |     |--- 3.jpg
    |     |--- 4.jpg
    |-- test     测试集
    |     |--- 5.jpg
    |-- annotations 标注信息
          |--- train_set.json
          |--- validation_set.json
          |--- test_set.json
```


### 5.3 文本数据集格式
`self.train_set`， `self.valid_set`，`self.test_set` 均为数据集路径，格式为:  
```
{
    'path': '/{dirpath}/tmp_local_cv_image_data/', 
    'train_set': '/{dirpath}/tmp_local_cv_image_data/train/', 
    'val_set': '/{dirpath}/tmp_local_cv_image_data/val/', 
    'test_set': '/{dirpath}/tmp_local_cv_image_data/test/', 
}
```


文本存储在当前目录下:
文件大小阈值为1G, 超过1G进行文件分割, 文件名从1开始自增, 支持txt,csv,json三种格式
```
./tmp_local_cv_image_data
    |-- train    训练集
    |     |--- 1.txt/csv/json
    |     |--- 2.txt/csv/json
    |-- val      验证集
    |     |--- 1.txt/csv/json
    |     |--- 2.txt/csv/json
    |-- test     测试集
```
