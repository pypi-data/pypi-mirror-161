# 目录结构及说明


```
.
├── examples
|   └── xxx.py
├── froModuleDrivers
|   └── xxx.py
├── setup.py
└── README.md

```


### examples文件夹说明
- 提供了每个硬件驱动基础的测试例子
- 更多控制方法请参考每个硬件驱动的api文档

### froModuleDrivers文件夹说明
- froModuleDrivers目录下存放了fro K12系列产品通用的socket通讯类的控制驱动源码，请勿随意修改

- 文件功能如下表所示

| filename    | fun  |
| ----------- | ---- |
| __init__.py |      |
| baseDriver.py |      |
| nioConnector.py |      |
| nioManager.py | 驱动管理模块 |
| protocol.py |      |
| protocolHandler.py |      |
| utils.py |      |
| gateway.py | 网关节点驱动 |
| homeDeviceDriver.py | 家居设备控制板驱动 |
| agricultureDeviceDriver.py | 农业设备控制板驱动 |
| conveyerBeltDriver.py | 传送带驱动 |
| roboticArmDriver.py | 机械臂驱动 |
| libraryDriver.py | 图书管理驱动 |
| mCarDriver.py | 小车驱动 |
| generalDeviceDriver.py | 百控板驱动 |


### setup.py

- 安装驱动到PC，安装完之后可以在任意目录来引用 from froModuleDrivers import xxx


# 安装方法

### 离线安装
- 下载源码到计算机
- 在froModuleDrivers同目录下打开命令行，运行指令：pip install .
```python
pip install .
```

### 在线安装
- 联网状态可以直接运行:pip install froModuleDrivers
```python
pip install froModuleDrivers
```


### Tips:

- 升级方法为：pip install -U froModuleDrivers
```python
pip install -U froModuleDrivers
```
或
```python
pip install -U froModuleDrivers -i https://pypi.org/simple
```

- 如果联网安装过程中发现更新速度过慢或者pypi源中暂不包含该软件包，可以尝试临时使用如下的镜像源。
官方：
```python
pip install froModuleDrivers -i https://pypi.org/simple
```
清华园：
```python
pip install froModuleDrivers -i https://pypi.tuna.tsinghua.edu.cn/simple
```
中国科学技术大学：
```python
pip install froModuleDrivers -i http://pypi.mirrors.ustc.edu.cn/simple/
```

# 版本信息

### V1.0.0
- first commit

### V1.0.1 
- 修复了核心驱动的一些格式和文档说明

### V1.0.2
- 上传驱动文件`gateway.py` `homeDeviceDriver.py` `agricultureDeviceDriver.py` `conveyerBeltDriver.py` `roboticArmDriver.py`
- 增加了pip安装过程中出现的问题的一些解决方法

### V1.0.3
- 修改了语音识别节点未识别成功时返回值未False

### V1.0.4
- 修复了语音识别节点识别到"小飞同学"唤醒词时打印的keyERROR错误

### V1.0.5
- 增加了识别一条新语句的方法

### V1.0.6
- 增加了图书管理模块的驱动`libraryDriver.py`

### V1.0.7
- 增加了小车的驱动`mCarDriver.py`

### V1.0.9
- 增加了百控板的驱动`generalDeviceDriver.py`
- 修复了一些`gateway.py`的BUG
- `homeDeviceDriver.py`驱动中窗帘模块的编码统一改为0x00B9,并删除了一些方法
- API添加说明

### V1.0.10
- 修复了百控板的驱动`generalDeviceDriver.py`中语音识别编码字典(voiceEncodeV3)与硬件返回不匹配的BUG

### V1.0.11
- 添加了百控板的驱动`generalDeviceDriver.py`中语音识别设置相关的3个方法
