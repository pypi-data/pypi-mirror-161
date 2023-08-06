from inflect import engine


class ModelMeta(type):

    def __getattr__(cls, item):
        return getattr(cls(), item)


class Field:

    def __init__(self, column):
        self.column = column

    def __gt__(self, other):
        return self._('>', other)

    def __ge__(self, other):
        return self._('>=', other)

    def __lt__(self, other):
        return self._('<', other)

    def __le__(self, other):
        return self._('<=', other)

    def __eq__(self, other):
        return self._('=', other)

    def __ne__(self, other):
        return self._('!=', other)

    def __contains__(self, item):
        return self.contains(item)

    def _build(self, operator, value):
        return f"({self.column} {operator} {value})"

    def like(self, value, sensitive=True):
        operator = 'LIKE' if sensitive else 'ILIKE'
        return f"{self.column} {operator} '{value}'"

    def contains(self, value, sensitive=True):
        return self.like(f"%{value}%", sensitive)

    def starts_with(self, value, sensitive=True):
        return self.like(f"{value}%", sensitive)

    def ends_with(self, value, sensitive=True):
        return self.like(f"%{value}", sensitive)

    def between(self, begin, end):
        return self._('BETWEEN', f"{begin} AND {end}")

    _ = _build


field = Field


class WhereGrammar:

    def __init__(self, wheres):
        # self._wheres = where_builder
        self.raws = wheres['raws']
        self.chunks = wheres['chunks']

    def __repr__(self):
        query = ""

        for chunk in self.chunks:
            column = chunk['column']
            operator = chunk['operator']
            value = chunk['value']
            self.raws.append(f"{column} {operator} {value}")

        query += " AND ".join(self.raws)

        return query


class QueryBuilder:

    def __init__(self, table):
        self.table = table
        self._query = ""

        self._selects = []
        # self.where_raws = []
        # self.where_chunks = []
        self._wheres = {
            'raws': [],
            'chunks': []
        }

    def __repr__(self):
        table = self.table

        columns = '*' if len(self._selects) == 0 else ", ".join(self._selects)

        self._query = f"SELECT {columns} FROM {table}"
        breakpoint()
        where_grammar = WhereGrammar(self._wheres)
        self._query += f" WHERE {where_grammar}"

        return self._query

    def all(self):
        """
        User.all()
        -> select * from users

        :return:
        """
        # return "SELECT * FROM " + self.table
        return self

    def where(self, *args, **kwargs):
        """
        User.where(name='Foo')
        -> Select * from users where name = 'Foo'

        User.where(name='Foo').where(age=10)
        -> Select * from users where name = 'Foo' and age = 10

        User.where(field(name).contains("albert"))
        User.where("albert" in field('name'))
        -> select * from users where name like '%albert%'

        User.where(field(age) > 10)
        -> select * from users where age > 10

        User.where(field('age').between(2, 39))
        User.where(2 < field('age') < 39)
        -> select * from users where age between 2 and 39

        User.where(age=[1,2,3,4,5])
        :return:
        """
        # This is mean that using raw _query
        if len(args) > 0:
            for raw in args:
                self._wheres['raws'].append(raw)

            return self

        for column in kwargs:

            operator = '='

            value = kwargs[column]
            value = self._normalize_value(value)

            if isinstance(value, list):
                operator = 'IN'
                value = kwargs[column]

            self._wheres['chunks'].append({
                'column': column,
                'operator': operator,
                'value': value
            })

        return self

    def _normalize_value(self, value):
        if isinstance(value, bool):
            value = 't' if value is True else 'f'
        if isinstance(value, str):
            value = f"'{value}'"

        if isinstance(value, (list, tuple)):
            value_temp = []
            for val in value:
                value_temp.append(str(self._normalize_value(val)))
            value = ', '.join(value_temp)
            value = f"({value})"

        return value

    def to_sql(self):
        return self._query


class Db:

    @classmethod
    def table(cls, name):
        ...


class Model(metaclass=ModelMeta):
    __table__: str = None

    def __getattr__(self, item):
        return getattr(self.builder(self.table), item)

    @property
    def builder(self):
        return QueryBuilder

    @property
    def table(self):
        if self.__table__ is None:
            table_name = self.__class__.__name__.lower()
            return engine().plural(table_name)

        return self.__table__
