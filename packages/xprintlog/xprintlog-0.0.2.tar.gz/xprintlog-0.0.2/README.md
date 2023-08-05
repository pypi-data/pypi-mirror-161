# xprintlog

- 无侵入
- 帮助你替换将函数内部的print函数替换为logging

## 安装

```bash
pip install xprintlog
```

## 使用

1. 直接使用装饰器进行装饰
```python
# test.py
import xprintlog as xprint
@xprint.xprint()
def test():
    print(111)

test()
#[.\test.py:6 - test][DEBUG] - 111
```

2. 使用类似于logging的方式，进行等级设置
```python
import xprintlog as xprint
@xprint.xprint(
    print_level=xprint.INFO,
    level=xprint.DEBUG
)
def test():
    print(111)


test()
# [.\test.py:7 - test][INFO] - 111

@xprint.xprint(
    print_level=xprint.DEBUG,
    level=xprint.INFO
)
def test1():
    print(111)


test1()
# 这里没有输出

```
3. 支持函数嵌套，且函数间互不影响
```python
import xprintlog as xprint
@xprint.xprint(
    print_level=xprint.INFO,
    level=xprint.DEBUG
)
def test():
    print(111)

@xprint.xprint(
    print_level=xprint.DEBUG,
    level=xprint.INFO
)
def test1():
    print(111)
    test()


test1()
# [.\test.py:7 - test][INFO] - 111

```
