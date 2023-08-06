# database操作(支持 mysql sqlite)

## 使用教程

### 下载

```shell
pip install pydb3
```

### 创建连接

```python
'''默认为sqlite'''
db = Db()
'''连接Sqlite'''
db = Db(file_path='D:\\db\\test.sqlite')
'''连接Mysql'''
db = Db('mysql', host='localhost', port='3306', user='root', database='db', password='123456')
```

#### 创建表

```python

from pydb3.db import Db
from pydb3.model import Integer, VarChar, Model, Image, Date, DateTime

'''定义模型'''


class Student(Model):
    name = VarChar(length=12, null=False, primary=False, comment="姓名")
    age = Integer(length=2, null=False, default=18, comment="年龄")
    score = Integer(length=11, null=False, default=10, comment="分数")
    mark = Integer(length=12, default=0, auto=True, null=False, primary=True, comment="标签")
    date = Date(length=12, default=0, null=False, auto=True, primary=False, comment='日期')
    image = Image(comment='图片')
    create_time = DateTime(default=None, null=False, auto=True, comment="时间")

    def __init__(self, name='test', age=None, mark=None, date=None, create_time=None, image=None):
        self.name = name
        self.age = age
        self.mark = mark
        self.date = date
        self.create_time = create_time
        self.image = image


if __name__ == '__main__':
    # 设置数据源
    db = Db()
    Student.set_db(db)
    s = Student()
    # 创建表
    s.create_table()
    # 获得所有学生
    students = Student.find()
    # 获得年龄为18岁的学生
    students = Student.find(age=18)
    # 保存到excel
    Student.export_excel('test.xlsx', students)
    # 从网页下载图片
    s.image = 'url=图片链接'
    # 从数据库中下载图片到本地
    s.image = 'path=保持路径'
    # 将对象相应属性保持对数据库
    s.save()
```

#### 新增数据

```python
db = Db()
datas = [None, '小明', 12]
'''相当于 insert into table values(NULL,'小明',12)'''
db.insert('table', datas).execute()
```

#### 查询

```python
db = Db()
'''相当于 select * from table where name=1 and age=1 limit 0,100'''
db.select("table").where(name=1).and_(age=1)[0:100].execute()
'''相当于 select * from table where name=1 and address like '%北京%'''
db.select("table").where(name=1, age=12).like(address='北京').execute()
'''相当于 select Count(*) from table'''
db.select('table').count().execute()
'''相当于 select name from table group by name having name='test' '''
db.select('table', 'name').group_by('name').having(name='test').execute()
'''相当于 select * from student join class on student.id=class.stu_id'''
db.select('student').join('class', id='stu_id').execute()
```

#### 更新

```python
db = Db()
'''相当于 update table  set name='李白' where name=1 and age=1 limit 0,100'''
db.update("table", name='李白').where(name=1).and_(age=1)[0:100].execute()
```

#### 删除

```python
db = Db()
'''相当于 delete from table where a=1'''
db.delete('table').where(a=1).execute()
```