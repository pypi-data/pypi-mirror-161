# 量子创新研究院云平台SDK使用说（I）--入门篇

## 1 SDK软件包安装：
在python和pip的环境命令行下执行

pip3 install ezQpy

如无报错即安装成功。

## 2 实验入门

### 2.1 接口导入


```python
from ezQpy import *
```

### 2.2 账户设置


```python
#如果用户账户ID或密码有误，在提交实验的时候依然会有提示。
username = "您的ID" 
password = "您的密码"
account = Account(username, password)
```

### 2.3 开始编程
通过QCIS语言定义线路，QCIS语言详解见相关教程。


```python
qcis_circuit = '''
H Q1
H Q2
CZ Q1 Q2
H Q2
H Q3
CZ Q2 Q3
H Q3
M Q1
M Q2
M Q3
   '''
#可以通过多种方法自行产生待提交的程序。
```

### 2.4 提交实验
作为入门教程，可以只通过最简单的submit_job()参数来提交一个实验，更多参数见进阶教程。

通过submit_job() 将线路传到云平台上的超导量子计算机实体机上，并获得实验结果查询id(query_id)，用以查询实验进度，请妥善保存好。如果返回query_id为0，则说明报错，报错内容一般会直接在执行过程中输出。


```python
query_id = account.submit_job(qcis_circuit, exp_name='GHz')
#最简形式nexp_name参量也可以不传递。
#submit_job可以有更多设置，还请关注我们的教程更新。
```

## 2.5 结果查询
当query_id不为0时，利用query_experiment()可以进行下一步查询工作。


```python
if query_id:
    result=account.query_experiment(query_id, max_wait_time=360000)
    #最大等待时间单位为秒，不传递时默认为30秒。因量子程序的执行会有排队的情况，而量子计算机本身有自动校准的时间，如果想跑全自动的程序，等待时间最好大于两者。
    print(result)
    value = result['000']
    print(value)
    f = open("./results.txt",'w')
    f.write(str(value))
    f.close()

```

    查询实验结果请等待: 1.48
    查询实验结果请等待: 2.46
    查询实验结果请等待: 4.74
    查询实验结果请等待: 4.01
    {'100': '0.056083333', '101': '0.06825', '110': '0.048666667', '111': '0.278', '000': '0.39891666', '001': '0.0655', '010': '0.046666667', '011': '0.037916668'}
    0.39891666


以上即完成最简的实验提交流程。如果需要对实验进行适当的归集，或者半自动，全自动的提交实验，重做指定实验等，可以参考后继的高级篇。
