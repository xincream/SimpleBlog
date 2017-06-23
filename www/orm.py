# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# @author: xincream


from python_blog.www.util import log, debug, warn, create_args_string
from python_blog.www.util import select, execute


class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)


class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)


class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)


class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)


class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False,  default)


class TextField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):
        # 排除Model类本身:
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        # 获取table名称:
        table_name = attrs.get('__table__', None) or name
        log('found model: %s (table: %s)' % (name, table_name))
        # 获取所有的Field和主键名:
        mapping = dict()
        fields = []
        primary_key = None
        print(attrs.items())
        for k, v in attrs.items():
            if isinstance(v, Field):
                log('found mapping: %s ==> %s' % (k, v))
                mapping[k] = v
                if v.primary_key:  # find主键
                    if primary_key:
                        raise Exception('Duplicate primary key for field: %s...' % k)
                    primary_key = k
                else:
                    fields.append(k)
        if not primary_key:
            raise Exception('primary key not found...')
        for k in mapping.keys():
            attrs.pop(k)
        attrs['__mappings__'] = mapping  # 属性和列的映射关系
        attrs['__table__'] = table_name
        attrs['__primary_key__'] = primary_key
        attrs['__fields__'] = fields
        # 构造默认的SELECT, INSERT, UPDATE和DELETE语句
        attrs['__select__'] = 'SELECT %s, %s FROM %s' % (primary_key, ', '.join(fields), table_name)
        attrs['__insert__'] = 'INSERT INTO %s (%s, %s) VALUES(%s)' % \
                              (table_name, ', '.join(fields), primary_key,
                               create_args_string(len(fields) + 1))
        attrs['__update__'] = 'UPDATE %s SET %s WHERE %s = ?' % \
                              (table_name,
                               ', '.join(map(lambda i: '%s=?' % (mapping.get(i).name or i), fields)),
                               primary_key)
        attrs['__delete__'] = 'DELETE FROM %s WHERE %s = ?' % (table_name, primary_key)
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % item)

    def __setattr__(self, key, value):
        self[key] = value

    def get_value(self, key):
        return getattr(self, key, None)

    def get_value_or_default(self, key):
        value = getattr(self, key, None)
        if not value:
            field = self.__mappings__[key]
            if field.default is not None:  # 有默认值就取默认值
                value = field.default if callable(field.default) else field.default
                debug('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)  # save存入后，之后就可以通过get_value拿到
        return value

    @classmethod
    async def find(cls, pk):
        """find object by primary key."""
        rs = await select('%s WHERE %s = ?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    @classmethod
    async def find_count(cls, sf, where=None, args=None):
        sql = ['SELECT count(%s) AS count FROM %s' % (sf, cls.__table__)]
        if where:
            sql.append('WHERE')
            sql.append(', '.join(map(lambda i: '%s = ?' % i, where)))
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['count']

    @classmethod
    async def find_all(cls, where=None, args=None, **kw):
        sql = [cls.__select__]
        if where:
            sql.append('WHERE')
            sql.append(', '.join(map(lambda i: '%s = ?' % i, where)))
        if not args:
            args = []
        order_by = kw.get('order_by', None)  # order_by = []
        if order_by:
            sql.append('ORDER BY')
            sql.extend(order_by)
        limit = kw.get('limit', None)
        if limit:
            sql.append('LIMIT')
            if isinstance(limit, int):
                sql.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:  # 从第一个数开始limit第二个数
                sql.append(', '.join([str(i) for i in limit]))
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    async def save(self):
        args = list(map(self.get_value_or_default, self.__fields__))
        args.append(self.get_value_or_default(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            warn('failed to insert record: affected rows: %s' % rows)

    async def update(self):  # 根据主键更新
        args = list(map(self.getValue, self.__fields__))
        args.append(self.get_value(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            warn('failed to update record by primary_key: affected rows: %s' % rows)

    async def remove(self):
        args = [self.get_value(self.__primary_key__)]
        rows = await  execute(self.__delete__, args)
        if rows != 1:
            warn('failed to remove record by primary_key: affected rows: %s' % rows)









