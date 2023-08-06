from .fields import Field
from django.db.models import QuerySet
from django.db import models


class FilterMeta(type):
    def __new__(mcs, name, bases, act):
        # 检测Field的命名规范
        desc_fields = []
        for attr_name, attr in act.items():
            if isinstance(attr, Field):
                desc_fields.append(attr_name)
                if attr_name.startswith('_') or attr_name[0].isupper():
                    raise TypeError(f'{name}中的{attr_name},不能为下划线开头，不能大写字母开头')
        act['_desc_fields'] = desc_fields  # 描述符中定义的字段名称列表
        return super().__new__(mcs, name, bases, act)

    def __call__(cls, *args, **kwargs):
        self = super().__call__(*args, **kwargs)
        return self.result_queryset


class Filter(metaclass=FilterMeta):
    """
    cls._desc_fields  描述符中定义的字段名称列表
    cls._fields  Meta.fields中定义的且没有在描述符中定义的字段名称列表
    """
    _desc_fields = tuple()

    def __init__(self, request, queryset=None):
        user_query = getattr(request, request.method)
        # queryset为None时取Meta.model.objects 这里不能用or运算，or运算会将空queryset认为None
        if queryset is None:
            self.result_queryset = self.Meta.model.objects
        elif isinstance(queryset, QuerySet):
            self.result_queryset = queryset
        else:
            raise ValueError(f'{self.__class__.__name__} queryset必须是QuerySet Object')

        # 排序查询名的缺省值为ordering，可以配置ordering_param进行覆盖
        ordering_param = getattr(self.Meta, 'ordering_param', 'ordering')
        ordering = user_query.get(ordering_param)  # 请求的排序条件

        # 生成用来查询的条件
        query = self._generate_query(user_query, self.result_queryset)
        self.result_queryset = self.result_queryset.filter(**query)
        # 进行排序，原地修改self.result_queryset
        self._ordering(ordering)

    def _ordering(self, ordering):
        if not isinstance(ordering, (str, list)):
            ordering = []
        if isinstance(ordering, str):
            ordering = ordering.split(',')  # 到这里ordering已经是是列表
        # ordering_fields是允许排序的字段 第一项为默认排序字段
        ordering_fields = getattr(self.Meta, 'ordering_fields', ())
        # __all__代表支持全部字段
        if ordering_fields == '__all__':
            ordering_fields = (field.name for field in self.result_queryset.model._meta.fields)
        # 过滤ordering，只剩允许排序的字段
        ordering = tuple(filter(lambda i: i.strip('-') in ordering_fields, ordering))
        if ordering:
            self.result_queryset = self.result_queryset.order_by(*ordering)

    def _generate_query(self, user_query, queryset) -> dict:
        """生成查询条件"""
        query = {}
        # 收集用户查询条件，这一步收集Meta.fields中定义的field
        for key, value in user_query.items():
            if key in self._fields:  # Meta.fields中定义的且没有在描述符中定义的字段名称列表
                query[key] = value
        # 自动模糊Meta.fields中定义的用户查询条件
        query = self._auto_contains(query, queryset)
        # 收集用户查询条件，这一步收集描述符中的查询条件
        for key, value in user_query.items():
            if key in self._desc_fields:  # 描述符中定义的字段名称列表
                setattr(self, key, value)  # 赋值描述符
                query.update(getattr(self, key))  # 获取描述符得到一个字典
        return query

    def _auto_contains(self, query: dict, queryset):
        """给查询的query字段名名自动加上模糊"""
        if not getattr(self.Meta, 'auto_contains', False):
            return query
        _copy_query = {**query}
        # 生成一个{字段名:field obj}的字典
        field_model_map = {field.name: field for field in queryset.model._meta.fields}
        for key, value in _copy_query.items():
            field_model = field_model_map.get(key, None)
            new_key = key
            # 整型（包括小整型），TextField，和CharField字段自动添加__contains
            if isinstance(field_model, (models.IntegerField, models.TextField, models.CharField)):
                new_key = key + '__contains'
            query[new_key] = query.pop(key)
        return query

    def __init_subclass__(cls, **kwargs):
        """子类被初始化后的操作"""
        # 只收集Field描述符没有定义的字段，也就是说如果描述符和Meta.fields中都定义了某个字段名称以描述符为准
        if getattr(cls.Meta, 'fields', None):
            cls._fields = tuple(i for i in cls.Meta.fields if i not in cls._desc_fields)
        else:
            cls._fields = tuple()

        if not getattr(cls.Meta, 'model', None):
            raise ValueError(f'{cls.__name__}的Meta.model不能为None')

    class Meta:
        model = None
        fields = ()  # 快捷定义支持查询的字段，可选配置默认为空元组,元组第一项为默认排序字段
        auto_contains = False  # 自动模糊 可选配置默认为False
        ordering_fields = ()  # 允许排序的字段 可选配置，默认为空元组 __all__表示全部
        # 排序查询名的缺省值为ordering，可以配置ordering_param进行覆盖
        ordering_param = 'ordering'  # 可选配置默认为ordering，
