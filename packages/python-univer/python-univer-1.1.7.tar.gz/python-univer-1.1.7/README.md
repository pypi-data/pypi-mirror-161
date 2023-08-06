# Python Univer

Содержит маппинг данных из Univer для SqlAlchemy

## Установка

```sh
$ pip install python_univer
```

## Конфигурация
```python
from python_univer.config import Config, DRIVER
from python_univer.orm import get_session


config = Config(host='адрес', user='пользователь', password='пароль', db='имя базы данных', driver=DRIVER.FREETDS)
Session = get_session(config)
```

## Использование
```python
from python_univer.models import Student


session = Session()

students = session.query(Student).filter(Student.course == 2, Student.status == 1)

for student in students:
    print(student)
```