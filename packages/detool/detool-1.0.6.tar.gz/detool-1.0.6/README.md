[![Supported Versions](https://img.shields.io/pypi/pyversions/leek.svg)](https://pypi.org/project/leek)
### 常用装饰器工具集
                  
#### pip安装
```shell
pip install detool
```

#### 1.统计函数执行时长装饰器
```python
import time
from detool import timer_cost

@timer_cost
def t_time():
    time.sleep(0.01)
    print(123)
```

#### 2.redis缓存装饰器
```python
    from detool import RedisCache
    
    redis_cache = RedisCache('127.0.0.1')

    @redis_cache.cache(ttl=30)
    def sum_t(a, b):
        print(f'{a}+{b}={a + b}')
        return a + b

    r = sum_t(1, 2)
    print(r)
```