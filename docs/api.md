# API Desc

[toc]

## 模型注册接⼝

**接⼝描述**

该接⼝⽤于在系统中注册模型

**请求说明**

HTTP Method: POST

URL: api/models/

URL Parameter: None 

Header:

| Parameter     | Value                 |
| ------------- | --------------------- |
| Content-Type  | application/json      |
| Authorization | Bearer {access_token} |

**请求参数**

| Field            | Required | Type   | Description                                                              |
| ---------------- | -------- | ------ | ------------------------------------------------------------------------ |
| model_content    | TRUE     | String | 注册到系统的模型文件，使用 Base64 编码                                   |
| model_label      | TRUE     | String | 模型返回的索引及名称，json 格式字符串，如：`{0: "background", 1: "foreground"}` |
| model_column     | TRUE     | Array  | 模型需要的列名，严格区分大小写和顺序，如：`["ABC", "DEF"]          |
| model_desc       | TRUE     | String | 模型描述                                                                 |
| model_type       | TRUE     | String | 类别，`PYTORCH` 或者 `SKLEARN`                                           |
| pipeline_content | False    | String | Base64 编码的预处理器文件，模型类型为 PyTorch 时需要                     |

**返回参数**

| Field    | Nullable | Type   | Description                                |
| -------- | -------- | ------ | ------------------------------------------ |
| log_id   | FALSE    | Number | 唯⼀ id，⽤于问题定位                        |
| model_id | TRUE     | String | 模型注册成功后的 id，如果注册失败则为 None |
| error    | TRUE     | String | 错误信息                                   |

## 单个模型查询接⼝

**接⼝描述**

该接⼝⽤于在系统中查询一个模型

**请求说明**

HTTP Method: GET

URL: api/models/${model_id}/

URL Parameter: None 

Header:

| Parameter     | Value                 |
| ------------- | --------------------- |
| Content-Type  | application/json      |
| Authorization | Bearer {access_token} |

**请求参数**

无

**返回参数**

| Field         | Nullable | Type   | Description                                                                |
| ------------- | -------- | ------ | -------------------------------------------------------------------------- |
| log_id        | FALSE    | Number | 唯⼀ id，⽤于问题定位                                                        |
| error         | TRUE     | String | 错误信息                                                                   |
| result        | TRUE     | String | 查询结果，json 字符串                                                      |
| +model_id     |          | String | 唯一模型 ID                                                                |
| +model_date   |          | String | 模型注册时间                                                               |
| +model_desc   |          | String | 模型描述                                                                   |
| +model_type   |          | String | 类别，`PYTORCH` 或者 `SKLEARN`                                             |
| +model_column |          | String | 模型需要的列名，严格区分大小写                                             |
| +model_date   |          | String | 模型注册的⽇期                                                              |
| +model_label  |          | String | 模型能识别的索引及名称，json 格式字符串，如：`{0: "background", 1: "foreground"}` |
| +tasks        |          | Array  | 模型相关的任务内容                                                         |
| ++task_id     |          | String | 关联的任务 ID                                                              |
| ++status      |          | String | 任务完成情况，{`PENDING`, `DONE`, `FAILED`}                                |
| ++task_desc   |          | String | 任务描述                                                                   |
| ++start_date  |          | String | 任务注册的⽇期                                                              |
| ++end_date    |          | String | 任务结束的⽇期                                                              |

## 所有模型查询接口

**接⼝描述**

该接⼝⽤于在系统中查询用户注册的所有模型

**请求说明**

HTTP Method: GET

URL: api/models/

URL Parameter: None 

Header:

| Parameter     | Value                 |
| ------------- | --------------------- |
| Content-Type  | application/json      |
| Authorization | Bearer {access_token} |

**请求参数**

无

**返回参数**

| Field         | Nullable | Type   | Description                                                                |
| ------------- | -------- | ------ | -------------------------------------------------------------------------- |
| log_id        | FALSE    | Number | 唯⼀ id，⽤于问题定位                                                        |
| error         | TRUE     | String | 错误信息                                                                   |
| result        | TRUE     | Array  | 查询结果，每个模型为一个 json 字符串                                       |
| +model_desc   |          | String | 模型描述                                                                   |
| +model_type   |          | String | 类别，`PYTORCH` 或者 `SKLEARN`                                             |
| +model_column |          | String | 模型需要的列名，严格区分大小写                                             |
| +model_date   |          | String | 模型注册的⽇期                                                              |
| +model_label  |          | String | 模型能识别的索引及名称，json 格式字符串，如：`{0: "background", 1: "foreground"}` |
| +tasks        |          | Array  | 模型关联的任务内容                                                         |

## 单个删除模型接⼝

**接⼝描述**

该接⼝⽤于在系统中删除指定的模型

**请求说明**

HTTP Method: DELETE

URL: api/models/${model_id}/

URL Parameter: None 

Header:

| Parameter     | Value                 |
| ------------- | --------------------- |
| Content-Type  | application/json      |
| Authorization | Bearer {access_token} |

**请求参数**

无

**返回参数**

| Field    | Nullable | Type   | Description         |
| -------- | -------- | ------ | ------------------- |
| log_id   | FALSE    | Number | 唯⼀ id，⽤于问题定位 |
| model_id | TRUE     | String | 被删除的模型 id     |
| error    | TRUE     | String | 错误信息            |

## 任务建⽴接⼝

**接⼝描述**

该接⼝⽤于在系统中建⽴分类的任务

**请求说明**

HTTP Method: POST

URL: api/models/${model_id}/tasks/

URL Parameter: None 

Header:

| Parameter     | Value                 |
| ------------- | --------------------- |
| Content-Type  | application/json      |
| Authorization | Bearer {access_token} |

**请求参数**

| Field     | Required | Type   | Description                |
| --------- | -------- | ------ | -------------------------- |
| model_id  | TRUE     | String | 用于完成任务的模型 id      |
| task_csv  | TRUE     | String | CSV 文件，使用 Base64 编码 |
| task_desc | TRUE     | String | 任务描述                   |


**返回参数**

| Field   | Nullable | Type   | Description                       |
| ------- | -------- | ------ | --------------------------------- |
| log_id  | FALSE    | Number | 唯⼀ id，⽤于问题定位               |
| task_id | TRUE     | Number | 唯⼀的任务 id，⽤于回调查询任务结果 |
| error   | TRUE     | String | 错误信息                          |

## 单个任务结果查询接⼝

**接⼝描述**

该接⼝⽤于在系统中查询任务结果

如果有结果的话，结果为 Base64 编码的 CSV，包含创建任务时的 CSV 的所有列，以及新增的预测结果列 `target`

**请求说明**

HTTP Method: GET

URL: api/tasks/${task_id}/

URL Parameter: None

Header:

| Parameter     | Value                 |
| ------------- | --------------------- |
| Content-Type  | application/json      |
| Authorization | Bearer {access_token} |

**请求参数**

无

**返回参数**

| Field          | Nullable | Type   | Description                                                              |
| -------------- | -------- | ------ | ------------------------------------------------------------------------ |
| log_id         | FALSE    | Number | 唯⼀ id，⽤于问题定位                                                      |
| error          | TRUE     | String | 错误信息                                                                 |
| result         | TRUE     | String | 返回的任务结果                                                           |
| +task_id       |          | String | 任务 ID                                                                  |
| +model_desc    |          | String | 任务描述                                                                 |
| +status        |          | String | 任务运行状况，{`PENDING`, `DONE`, `FAILED`}                              |
| +result        |          | String | 如果任务运行完成的返回，编码为 Base64 的 CSV                             |
| +model_id      |          | String | 任务所使用的模型 ID                                                      |
| +model_label   |          | String | 模型返回的索引及名称，json 格式字符串，如：`{0: "background", 1: "foreground"}` |
| +start_date    |          | String | 任务开始时间                                                             |
| +end_date      |          | String | 任务结束时间                                                             |
| +error_message |          | String | 如果任务运行失败的错误信息                                               |


## 所有任务查询接⼝ API

**接⼝描述**

该接⼝⽤于在系统中查询用户的所有任务

**请求说明**

HTTP Method: GET

URL: api/tasks/

URL Parameter: None

Header:

| Parameter     | Value                 |
| ------------- | --------------------- |
| Content-Type  | application/json      |
| Authorization | Bearer {access_token} |

**请求参数**

无

**返回参数**

| Field          | Nullable | Type   | Description                                                              |
| -------------- | -------- | ------ | ------------------------------------------------------------------------ |
| log_id         | FALSE    | Number | 唯⼀ id，⽤于问题定位                                                      |
| error          | TRUE     | String | 错误信息                                                                 |
| result         | TRUE     | Array  | 用户的所有任务，每个任务为一个 json 字符串                               |
| +task_id       |          | Number | 唯一任务 ID                                                              |
| +task_desc     |          | String | 任务描述                                                                 |
| +status        |          | String | 任务运行状况，{`PENDING`, `DONE`, `FAILED`}                              |
| +model_id      |          | String | 任务使用的模型 ID                                                        |
| +model_label   |          | String | 模型返回的索引及名称，json 格式字符串，如：`{0: "background", 1: "foreground"}` |
| +error_message |          | String | 如果任务运行失败的错误信息                                               |
| +start_date    |          | String | 任务开始时间                                                             |
| +end_date      |          | String | 任务结束时间                                                             |

## 任务删除接⼝

**接⼝描述**

该接⼝⽤于在系统中删除指定的任务

**请求说明**

HTTP Method: DELETE

URL: api/tasks/${task_id}/

URL Parameter: None

Header:

| Parameter     | Value                 |
| ------------- | --------------------- |
| Content-Type  | application/json      |
| Authorization | Bearer {access_token} |

**请求参数**

无

**返回参数**

| Field   | Nullable | Type   | Description         |
| ------- | -------- | ------ | ------------------- |
| log_id  | FALSE    | Number | 唯⼀ id，⽤于问题定位 |
| task_id | TRUE     | String | 被删除的任务 id     |
| error   | TRUE     | String | 错误信息            |


## 登录接口

**接⼝描述**

该接⼝⽤于用户登录，返回有效期 30 分钟的 Token

**请求说明**

HTTP Method: POST

URL: api/login/

URL Parameter: None

Header:

| Parameter    | Value            |
| ------------ | ---------------- |
| Content-Type | application/json |

**请求参数**

| Field    | Required | Type   | Description |
| -------- | -------- | ------ | ----------- |
| user_id  | TRUE     | String | 用户名      |
| password | TRUE     | String | 密码        |


**返回参数**

| Field        | Nullable | Type   | Description                      |
| ------------ | -------- | ------ | -------------------------------- |
| log_id       | FALSE    | Number | 唯⼀ id，⽤于问题定位              |
| access_token | TRUE     | String | 用户登陆后有效期 30 分钟的 token |
| error        | TRUE     | String | 错误信息                         |

## 登出接口

**接⼝描述**

该接⼝⽤于用户登出

**请求说明**

HTTP Method: POST

URL: api/logout/

URL Parameter: None

Header:

| Parameter     | Value                 |
| ------------- | --------------------- |
| Content-Type  | application/json      |
| Authorization | Bearer {access_token} |

**请求参数**

无

**返回参数**

| Field  | Nullable | Type   | Description         |
| ------ | -------- | ------ | ------------------- |
| log_id | FALSE    | Number | 唯⼀ id，⽤于问题定位 |
| error  | TRUE     | String | 错误信息            | s |

## log_id 错误码

200 （成功） 服务器已成功处理了请求。

202 （已接受） 服务器已接受请求，但尚未处理。

400 （错误请求） 服务器不理解请求的语法。

401 （未授权） 请求要求身份验证。 对于需要登录的应⽤，服务器可能返回此响应。

403 （拒绝访问）此资源不存在或者该用户没有权限访问。

404 （不存在）资源不存在。

412 （未满⾜前提条件） 服务器未满⾜请求者在请求中设置的其中⼀个前提条件。

413 （请求实体过⼤） 服务器⽆法处理请求，因为请求实体过⼤，超出服务器的处理能⼒。

500 （服务器内部错误） 服务器遇到错误，⽆法完成请求。

## 模型的导出

### PyTorch

上传模型时需要同时上传使用 `joblib.dump` 保存的 Sklearn Pipeline 作为预处理器文件，例：

```python3
preprocessor = ColumnTransformer([
    ('std', RobustScaler(), ['ABC', 'DEF]),
    ('pwr', PowerTransformer(), ['EFG'])]
)
pipeline = Pipeline(steps=[
    ('pre', preprocessor)
])
pipeline.fit(X)
# 保存 preprocessor
dump(pipeline, "pipeline.pkl")
```

PyTorch 导出模型为 ONNX 格式，单 Tensor，输入/输出名随意，例：

```python3
torch.onnx.export(
    model,
    torch.tensor(X_scaled, dtype=torch.float32),
    "torch.onnx",
    input_names=["input"],
    output_names=["target"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
)
```

上传模型时需要附加 `X_scaled` 的列名在 `model_columns` 中，区分大小写和前后顺序。创建任务时的 CSV 则可以使用不一样的列顺序。

### Scikit-Learn

包含 Pipeline 的 Sklearn 模型，ONNX 格式。

```python3
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

feature_names = ["ABC", "DEF", "EFG"]
initial_type = [(name, FloatTensorType([None, 1])) for name in feature_names]

onnx_model = convert_sklearn(finalpipe, initial_types=initial_type)

with open("sn.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())
```

上传模型时需要附加 `feature_names` 在 `model_columns` 中，区分大小写和前后顺序。创建任务时的 CSV 则可以使用不一样的列顺序。

因为已经包含了预处理器，所以不需要上传预处理用的 Pipeline。即便上传服务器也会直接忽略。