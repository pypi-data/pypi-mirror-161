from dbpoolpy.dbpool import acquire, release
from dbpoolpy.dbhelper import SelectHelper, InsertHelper, UpdateHelper, DeleteHelper

def with_dbo(func):
    def _(self, *args, **kwargs):
        self.open_dbo()
        res = None
        try:
            res = func(self, *args, **kwargs)
        finally:
            self.close_dbo()
        return res
    return _

class TableBase():

    def __init__(self, db):
        self._db = db
        self._dbo = None

    def __enter__(self):
        self.open_dbo()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        ''' 退出时如果没有关闭，则关闭连接 '''
        self.close_dbo()
        return exception_type is None

    def __del__(self):
        ''' 变量回收时，关闭连接 '''
        self.close_dbo()

    def close_dbo(self):
        if self._dbo is not None:
            release(self._dbo)
            self._dbo = None

    def open_dbo(self):
        if self._dbo is None:
            self._dbo = acquire(self._db)
        return self._dbo


    def sql(self, cls, is_auto_close, fill_args):
        try:
            if self._dbo is None:
                self.open_dbo()
            return cls.sql(self, fill_args)
        finally:
            if is_auto_close:
                self.close_dbo()


class SelectTable(TableBase, SelectHelper):
    def __init__(self, db, table):
        TableBase.__init__(self, db)
        SelectHelper.__init__(self, dbo=self._dbo, tables=table)

    def sql(self, is_auto_close=True, fill_args=True):
        return TableBase.sql(self, SelectHelper, is_auto_close, fill_args)

    @with_dbo
    def all(self, isdict=True):
        sql = self.sql(is_auto_close=False, fill_args=False)
        return self._dbo.query(sql, self._where_args or None, isdict=isdict)

    @with_dbo
    def first(self, isdict=True):
        sql = self.sql(is_auto_close=False, fill_args=False)
        if sql.find('limit') == -1:
            sql += ' limit 1'
        return self._dbo.get(sql, self._where_args or None, isdict=isdict)


class InsertTable(TableBase, InsertHelper):
    def __init__(self, db, table):
        TableBase.__init__(self, db)
        InsertHelper.__init__(self, dbo=self._dbo, table=table)

    def sql(self, is_auto_close=True, fill_args=True):
        return TableBase.sql(self, InsertHelper, is_auto_close, fill_args)

    @with_dbo
    def execute(self):
        sql = self.sql(is_auto_close=False, fill_args=False)
        return self._dbo.execute_insert(sql, self._values_args or None)


class UpdateTable(TableBase, UpdateHelper):
    def __init__(self, db, table):
        TableBase.__init__(self, db)
        UpdateHelper.__init__(self, dbo=None, table=table)

    def sql(self, is_auto_close=True, fill_args=True):
        return TableBase.sql(self, UpdateHelper, is_auto_close, fill_args)

    def manysql(self, is_auto_close=True, fill_args=True):
        try:
            if self._dbo is None:
                self.open_dbo()
            return UpdateHelper.manysql(self, fill_args)
        finally:
            if is_auto_close:
                self.close_dbo()

    @with_dbo
    def execute(self):
        if self._many_values and self._many_where:
            sql, args = self.manysql(is_auto_close=False, fill_args=False)
            return self._dbo.executemany(sql, args)
        else:
            sql = self.sql(is_auto_close=False, fill_args=False)
            args = self._values_args + self._where_args
            return self._dbo.execute(sql, args or None)


class DeleteTable(TableBase, DeleteHelper):
    def __init__(self, db, table):
        TableBase.__init__(self, db)
        DeleteHelper.__init__(self, dbo=self._dbo, table=table)

    def sql(self, is_auto_close=True, fill_args=True):
        return TableBase.sql(self, DeleteHelper, is_auto_close, fill_args)

    @with_dbo
    def execute(self):
        sql = self.sql(is_auto_close=False, fill_args=False)
        return self._dbo.execute(sql, self._where_args or None)


class Settor(object):
    def __init__(self, settor):
        self.settor = settor

    def where(self, **kwargs):
        self.settor.where(**kwargs).execute()


class Mapper(object):
    def __init__(self, mapper, mod="all"):
        self.mapper = mapper
        self.mod = mod

    def where(self, **kwargs):
        if self.mod == 'all':
            datas = self.mapper.where(**kwargs).all(isdict=False)
            return [i[0] for i in datas] if datas else datas
        elif self.mod == 'first':
            data = self.mapper.where(**kwargs).first(isdict=False)
            return data[0] if data else data


class Table(object):
    @classmethod
    def _db(cls):
        return cls.__server__

    @classmethod
    def _schema(cls):
        return cls.__schema__

    @classmethod
    def _table(cls):
        return "%s.%s" % (cls.__schema__, cls.__table__)

    @classmethod
    def select(cls, **kwargs):
        return SelectTable(cls._db(), cls._table())

    @classmethod
    def update(cls, **kwargs):
        return UpdateTable(cls._db(), cls._table())

    @classmethod
    def insert(cls, **kwargs):
        return InsertTable(cls._db(), cls._table())

    @classmethod
    def delete(cls, **kwargs):
        return DeleteTable(cls._db(), cls._table())

    @classmethod
    def find(cls, **kwargs):
        return SelectTable(cls._db(), cls._table()).where(**kwargs).all()

    @classmethod
    def find_one(cls, **kwargs):
        return SelectTable(cls._db(), cls._table()).where(**kwargs).first()

    @classmethod
    def get(cls, **kwargs):
        info = cls.find_one(**kwargs)
        assert info, "库(%s)表(%s)未找到对应信息(%s)" % (
                cls._schema(), cls._table(), str(kwargs))
        return info

    @classmethod
    def add(cls, **kwargs):
        return InsertTable(cls._db(), cls._table()).values(**kwargs).execute()

    @classmethod
    def add_many(cls, many):
        cls.insert(many=many).execute()

    @classmethod
    def add_batch(cls, data, batch=2000):
        with TableBase(cls._db()) as tb:
            tb._dbo.insert_batch(cls._table(), data, batch)

    @classmethod
    def set(cls, **kwargs):
        return Settor(UpdateTable(cls._db(), cls._table()).values(**kwargs))

    @classmethod
    def set_batch(cls, many_values, many_where, batch=2000):
        with TableBase(cls._db()) as tb:
            tb._dbo.update_batch(cls._table(), many_values, many_where, batch)

    @classmethod
    def rm(cls, **kwargs):
        return DeleteTable(cls._db(), cls._table()).where(**kwargs).execute()

    @classmethod
    def map(cls, field):
        return Mapper(SelectTable(cls._db(), cls._table()).fields(str(field)), mod='all')

    @classmethod
    def map_one(cls, field):
        return Mapper(SelectTable(cls._db(), cls._table()).fields(str(field)), mod='first')
