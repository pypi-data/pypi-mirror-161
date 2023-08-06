# database操作(支持 mysql mongodb)

## How to use

### mysql

### mongodb

### elasticSearch

### sqlite3

#### 创建表

```python

from pydb3.db import Db
from pydb3.model import Integer, VarChar, Model, Float, Date, DateTime

'''定义模型'''


class Student(Model):
    name = VarChar(length=12, null=False, primary=False, comment="姓名")
    age = Integer(length=2, null=False, default=18, comment="年龄")
    score = Integer(length=11, null=False, default=10, comment="分数")
    mark = Integer(length=12, default=0, auto=True, null=False, primary=True, comment="标签")
    date = Date(length=12, default=0, null=False, auto=True, primary=False, comment='日期')
    create_time = DateTime(default=None, null=False, auto=True, comment="时间")

    def __init__(self, name='test', age=None, mark=None, date=None, create_time=None):
        self.name = name
        self.age = age
        self.mark = mark
        self.date = date
        self.create_time = create_time


if __name__ == '__main__':
    # 设置数据源
    db = Db()
    Student.set_db(db)
    s = Student()
    # 创建表
    s.create_table()
    # 将s的属性插入数据库
    s.save()
```

#### 新增数据

```python
db = Db()
datas = [None, '小明', 12]
'''相当于 insert into table values(NULL,'小明',12)'''
db.insert('table', datas)
```
#### 查询

```python
db = Db()
'''相当于 select * from table where name=1 and age=1 limit 0,100'''
db.select("table").where(name=1).and_(age=1)[0:100].execute()
```

