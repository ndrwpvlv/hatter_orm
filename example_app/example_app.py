import logging

from hatter_orm.columns import Column
from hatter_orm.db import Database
from hatter_orm.fields import IntegerField, TextField, RealField
from hatter_orm.models import Model
from hatter_orm.helpers import try_or_error

logging.basicConfig(filename="hatter.log", level=logging.INFO)


class Item(Model):
    __tablename__ = 'items'
    id = Column(IntegerField, primary_key=True, autoincrement=True)
    title = Column(TextField, not_null=True)
    caption = Column(TextField)
    price = Column(RealField, not_null=True)
    category = Column(IntegerField, foreign_key='categories.id')
    producer = Column(IntegerField, foreign_key='producers.id')

    def __init__(self, title, price, producer, category='Null', caption=''):
        self.title = title
        self.caption = caption
        self.price = price
        self.category = category
        self.producer = producer


class Category(Model):
    __tablename__ = 'categories'
    id = Column(IntegerField, primary_key=True, autoincrement=True)
    title = Column(TextField, not_null=True)
    caption = Column(TextField)

    def __init__(self, title, caption=''):
        self.title = title
        self.caption = caption


class Producer(Model):
    __tablename__ = 'producers'
    id = Column(IntegerField, primary_key=True, autoincrement=True)
    title = Column(TextField, not_null=True)
    caption = Column(TextField)

    def __init__(self, title, caption=''):
        self.title = title
        self.caption = caption


@try_or_error
def main():
    # Database initialization
    db = Database()

    # Create tables
    logging.info('---------------------')
    logging.info('Create tables')
    db.create_all([Item, Category, Producer])

    # Some data for tables
    categories = [['Apple', 'Apple mobile phones'], ['Samsung', 'Samsung mobile phones'], ]
    producers = [['Apple', 'Apple California'], ['Samsung', 'Samsung Korea'], ]
    items = [['iPhone 6', 30000.0, 1, 1], ['iPhone 7', 45000.0, 1, 1], ['iPhone 8', 60000.0, 1, 1],
             ['Samsung Galaxy', 45000.0, 2, 2], ]

    # Append data to tables.
    # We disable foreign keys checking here and
    # enable it at end of commit to avoid foreign keys errors during database populating.
    # Check your data before commit.
    db.add('PRAGMA foreign_keys = "0"')
    for item in items:
        db.add(Item(*item))
    for c in categories:
        db.add(Category(*c))
    for p in producers:
        db.add(Producer(*p))
    db.add('PRAGMA foreign_keys = "1"')
    db.commit()

    # Example of request with foreign key with join
    logging.info('---------------------')
    logging.info('Basic query with foreign key join')
    item = Item.session(db).query(['items.id', 'items.title', 'items.price', 'categories.title',
                                    'producers.title']).foreign_key().all()
    logging.info(item.serialize_json())  # Log serialize to json
    print(item.serialize_json())
    logging.info(item.serialize())  # Log serialize
    print(item.serialize())

    # Example of request for delete
    logging.info('---------------------')
    logging.info('Basic query for delete')
    Item.session(db).delete().filter_by(id=1).all()
    item = Item.session(db).query(['items.id', 'items.title', 'items.price', 'categories.title',
                                   'producers.title']).foreign_key().all()
    logging.info(item.serialize_json())  # Log serialize to json
    print(item.serialize_json())

    # Example of update
    logging.info('---------------------')
    logging.info('Basic query for update')
    Item.session(db).update(title='Nokia 3310').filter_by(title='iPhone 7').all()
    item = Item.session(db).query(['items.id', 'items.title', 'items.price', 'categories.title',
                                   'producers.title']).foreign_key().all()
    logging.info(item.serialize_json())  # Log serialize to json
    print(item.serialize_json())

    logging.info('---------------------')
    logging.info('Tables deleting')
    db.drop(Item)
    db.drop_all()
    db.close()


if __name__ == '__main__':
    main()
