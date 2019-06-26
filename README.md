# Hatter_ORM

**Hatter_ORM** is simple SQLITE ORM. It was made as homework of OTUS Python course. 


## Basic usage
Initial configuration of classes

```
from hatter_orm.columns import Column
from hatter_orm.db import Database
from hatter_orm.fields import IntegerField, TextField, RealField
from hatter_orm.models import Model
from hatter_orm.helpers import try_or_error

class Item(Model):
    __tablename__ = 'items'
    id = Column(IntegerField, primary_key=True, autoincrement=True)
    title = Column(TextField, not_null=True)
    caption = Column(TextField)
    price = Column(RealField, not_null=True)
    category = Column(IntegerField, foreign_key='categories.id')
    producer = Column(IntegerField, foreign_key='producers.id')

    def __init__(self, title: str, price: float, producer: str, category: str = 'Null', caption: str = ''):
        self.title = title
        self.caption = caption
        self.price = price
        self.category = category
        self.producer = producer
``` 
Initialize of database
```
db = Database(name: str, path: str)
```
Create tables
```
db.create_all([Item, Category, Producer, ])
```
Add data to tables
```
item = Item('title', 600.0, 'producer', 'category', 'caption')
db.add(item)
```
Commit inputs
```
db.commit()
```
Close database
```
db.close()
```
## Queries
Select query based on query "constructor":
```
Item.session(db).query(['columns_names', ]).filter_by(id=1).order_by('id').foreign_key().all()
".all()" can be replaced with ".first()" or ".get()"
```
Update query:
```
Item.session(db).update(title='NEW TITLE').filter_by(title='TITLE').all()
```
Delete query:
```
Item.session(db).delete().filter_by(id=1).all()
```
###Query commit:

Every query should be finished with .get(), .all(), or .first() tail.
Formats of tails:
```
.get(limit: int = 1, offset: int = 0)
```
```
.all(offset: int = 0)
``` 
```
.first()
```
**limit** variable can be use to set number of rows to return on commit. 

**offset** is rows offset.  

## Tables creation and deletion
Delete single table
```
db.drop(Item)
```
Delete all tables
```
db.drop_all()
```

## Field types
SQLITE support Null, Integer, Real, Text and Blob fields. Hatter_ORM have Integer, Real and Text implementations.

Basic Class column creation:
```
from hatter_orm.columns import Column
from hatter_orm.fields import IntegerField, TextField, RealField
from hatter_orm.models import Model

id = Column(IntegerField, primary_key=True, autoincrement=True)
title = Column(TextField, not_null=True)
price = Column(RealField, not_null=True)
category = Column(IntegerField, foreign_key='categories.id')
producer = Column(IntegerField, foreign_key='producers.id')
```
Implemented constrains:
```
'not_null', 'default', 'primary_key', 'autoincrement', 'unique', 'foreign_key'
```

## Requirements
```
Python 3.5+
```


## Contributors
Andrei S. Pavlov (https://github.com/ndrwpvlv/)
