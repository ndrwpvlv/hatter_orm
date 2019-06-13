import json
import re
from collections import OrderedDict

from .config import Config
from .helpers import OrderedClass, try_or_error


class Model(metaclass=OrderedClass):
    __tablename__ = None
    __request_constructor__ = {}
    __db__ = None
    __response__ = None
    __columns_query__ = None

    @try_or_error
    def __call__(self, *args, **kwargs):
        return self.__request_constructor__ or self.insert()

    def __exit__(self, exc_type, exc_value, traceback):
        print(exc_type, exc_value, traceback)

    @classmethod
    def table_name(cls):
        if not cls.__tablename__:
            cls.__tablename__ = '{}'.format(cls.__name__.lower())
        return cls.__tablename__

    @classmethod
    def columns(cls) -> tuple:
        """
        Get columns from Class
        :return: tuple((column_name_1, (kw1, kw2, ...)), (column_name_2, (kw1, kw2, ...)), ...)
        """
        return tuple([tuple([name, getattr(cls, name).keywords()]) for name in cls.columns_names()])

    def fields(self) -> dict:
        """
        Get fields of Model instance with values
        :return: Ordered dict with values
        """
        names = tuple([name for name in self.__dict_ordered__ if
                       not any([callable(getattr(self, name)), name.startswith('__'), name.endswith('__')])])
        return OrderedDict([(name, getattr(self, name)) for name in names])

    @classmethod
    def columns_names(cls) -> list:
        """
        Get column names of Model instance
        :return: list with columns names
        """
        return [name for name in cls.__dict_ordered__ if
                not any([callable(getattr(cls, name)), name.startswith('__'), name.endswith('__')])]

    @classmethod
    def create_table(cls):
        request_body = ['`{}` {}'.format(col[0], ' '.join([row[1] for row in col[1] if not row[0] in [
            'foreign_key', 'on_update', 'on_delete]']])) for col in cls.columns()]
        request_fk = ', '.join(
            ['FOREIGN KEY(`{}`) REFERENCES {} ON UPDATE CASCADE ON DELETE CASCADE'.format(col[0], row[1]) for col in
             cls.columns() for row in col[1] if row[0] is 'foreign_key'])
        return 'CREATE TABLE IF NOT EXISTS `{}` ({});'.format(
            cls.table_name(), ', '.join([*request_body, request_fk]) if request_fk else ', '.join(request_body))

    def insert(self):
        fields = self.fields()
        columns = self.columns()
        primary_columns = [col[0] for col in columns if
                           ('primary_key' or 'autoincrement') in [row[0] for row in col[1]]]
        keys = [key for key in fields if key not in primary_columns]
        values = tuple([fields[key] for key in keys])
        request = 'INSERT INTO `{}`({}) VALUES({})'.format(self.table_name(), ','.join(keys), ('?,' * len(keys))[:-1])
        return tuple([request, values])

    @classmethod
    def session(cls, db):
        """
        Connect class to database for query
        :param db: db instance
        :return: self class
        """
        cls.__db__ = db
        return cls

    @classmethod
    def query(cls, columns: list = None):
        """
        Update query initialisation
        :param columns: list of columns for querying
        :return: self cls
        """
        cls.__columns_query__ = columns
        cls.__request_constructor__['header'] = 'SELECT {} FROM {}'.format(','.join(columns), cls.__tablename__) if \
            columns else 'SELECT * FROM {}'.format(cls.__tablename__)
        return cls

    @classmethod
    def update(cls, **updaters):
        """
        Update query initialisation
        :param updaters: dict with update expressions for SET.
                         example: User.session(db).update(name='John', age=36).filter_by(last_name='Johnson').all()
        :return: self cls
        """
        if any([True if key in cls.__dict_ordered__ else False for key in updaters]):
            _set = 'SET {}'.format(','.join(
                ['{} = "{}"'.format(key, updaters.get(key)) for key in updaters if key in cls.__dict_ordered__]))
            cls.__request_constructor__['header'] = 'UPDATE {} {}'.format(cls.__tablename__, _set)
        return cls

    @classmethod
    def delete(cls):
        """
        Delete query initialisation
        :return: self cls
        """
        cls.__request_constructor__['header'] = 'DELETE FROM {}'.format(cls.__tablename__)
        return cls

    @classmethod
    def filter_by(cls, **filters):
        """
        SQL WHERE part of request creator
        :param filters: dict with equal filters. Example: User.session(db).query().filter_by(name='John').all()
        :return: self cls
        """
        if any([True if key in cls.__dict_ordered__ else False for key in filters]):
            cls.__request_constructor__['filter_by'] = 'WHERE {}'.format(
                ' '.join(['{} = "{}"'.format(key, filters.get(key)) for key in filters if key in cls.__dict_ordered__]))
        return cls

    @classmethod
    def order_by(cls, query: str = None, desc: bool = False):
        """
        SQL ORDER BY part of request
        :param query: Column name for sorting, str
        :param desc: Descending order trigger, bool
        :return: self cls
        """
        if query:
            cls.__request_constructor__['order_by'] = 'ORDER BY {} {}'.format(query, 'ASC' if not desc else 'DESC')
        return cls

    @classmethod
    def foreign_key(cls, join_type: str = 'LEFT'):
        """
        Foreign key joiner
        :return: self cls
        """
        _columns = [[c[0], cls.bracket_to_dot(constraint[1])] for c in cls.columns() for constraint in c[1] if
                    constraint[0] is 'foreign_key']
        _join = join_type if join_type in Config.JOIN_TYPES else Config.DEFAULT_JOIN
        cls.__request_constructor__['join'] = ''.join(
            ['\n{} JOIN {} ON {}.{} = {}'.format(
                _join, c[1].split('.')[0], cls.__tablename__, c[0], c[1]) for c in _columns])
        return cls

    @classmethod
    def exec(cls, limit: int = 1, offset: int = 0):
        """
        Concatenate the request from blocks to single string, add it and commit.
        It has tow options: limit and offset.
        Returned response is copied to cls.__response__. After commit cls.__request_constructor__ become blank
        :param limit: count of rows in response from db
        :param offset: rows offset
        :return: self.csl
        """
        args = locals()
        structure = ['header', 'filter_by', 'order_by', 'offset', 'join', ]
        if not all([args['limit'] >= Config.SQL_RESPONSE_LIMIT, args['offset'] < 1]):
            cls.__request_constructor__['offset'] = 'LIMIT {} OFFSET {}'.format(args['limit'], args['offset'])
        request_body = ' '.join(
            ['{}'.format(cls.__request_constructor__.get(key)) for key in structure if
             cls.__request_constructor__.get(key)])
        cls.__db__.add('{};'.format(request_body))
        cls.__response__ = cls.__db__.commit()
        cls.__request_constructor__ = {}
        return cls

    @classmethod
    def all(cls, offset: int = 0):
        """
        Get all rows wrapper for .exec()
        :param offset: offset variable for .exec()
        :return:
        """
        return cls.exec(limit=Config.SQL_RESPONSE_LIMIT, offset=offset)

    @classmethod
    def first(cls):
        """
        Get first row wrapper for .exec()
        :return:
        """
        return cls.exec(limit=1, offset=0)

    @classmethod
    def serialize(cls) -> dict:
        """
        Serialize response to dict
        :return: response dict
        """
        return {cls.__tablename__: [OrderedDict([(key, value) for key, value in zip(
            cls.__columns_query__ or cls.columns_names(), item)]) for item in cls.__response__]}

    @classmethod
    def serialize_json(cls) -> json:
        """
        Serialize response to json
        :return: response dict to json
        """
        return json.dumps(cls.serialize())

    @staticmethod
    def bracket_to_dot(bracket: str) -> str:
        """
        Convert bracket notation Table(id) to Table.id
        :param bracket: string with patter Table(id)
        :return: string with pattern Table.id
        """
        column = re.findall('([a-zA-Z0-9_]+)\(([a-zA-Z0-9_]+)\)', bracket)
        return '.'.join(column[0]) if column else None
