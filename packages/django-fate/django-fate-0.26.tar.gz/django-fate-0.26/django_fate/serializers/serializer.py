from django.db.models import Model
from collections import Iterable
from .fields import Field, ManyToManyField, RelatedField

__all__ = ['Serializer']


class SerializerMeta(type):
    def __new__(mcs, name, bases, act):
        # 记录多对多字段和跨表
        many_and_related = []
        for attr_name, attr in act.items():
            if isinstance(attr, ManyToManyField) or isinstance(attr, RelatedField):
                many_and_related.append(attr_name)
        act['_many_and_related'] = tuple(many_and_related)
        return super().__new__(mcs, name, bases, act)

    def __call__(cls, set_or_obj):
        self = super().__call__()
        return self._serialize(set_or_obj)


class Serializer(metaclass=SerializerMeta):
    _many_and_related = ()

    def __init__(self):
        self.hans_display = None
        self.fields = []

    def _serialize(self, set_or_obj):
        """序列化queryset或model_obj"""

        if isinstance(set_or_obj, Iterable):
            return [self._to_dict(obj) for obj in set_or_obj]

        elif isinstance(set_or_obj, Model):
            return self._to_dict(set_or_obj)

        else:
            raise TypeError('{}类型不支持序列化'.format(type(set_or_obj)))

    def _to_dict(self, model_obj):
        data_dict = {}

        for field in model_obj._meta.fields:
            # only被定义时，忽略only以外的全部字段
            if self.Meta.only and field.name not in self.Meta.only:
                continue
            # 只在没定义only时defer生效，only一旦定义defer失效
            if not self.Meta.only and field.name in self.Meta.defer:
                continue

            # 等价于 model_obj.get(field.name)
            field_value = getattr(model_obj, field.name)  # 获取字段的值
            process = getattr(self, field.name, Field.process)  # 获取（在描述符中）字段的处理方法
            if field.choices:  # 获取该字段的display
                data_dict[field.name + '_display'] = dict(field.choices).get(field_value, None)
            data_dict[field.name] = process(field_value)

        # 多对多字段不在obj._meta.fields中，也不能直接用 model_obj.get() 获得 ,关联跨表字段更不能
        for field_name in self._many_and_related:
            process = getattr(self, field_name)
            data_dict[field_name] = process(model_obj)

        return data_dict

    def __init_subclass__(cls, **kwargs):
        """子类被初始化后的操作"""
        cls.Meta.only = getattr(cls.Meta, 'only', ())
        cls.Meta.defer = getattr(cls.Meta, 'defer', ())

    class Meta:
        only = ()  # only被定义时，忽略only以外的全部字段
        # 本次序列化排除的字段
        defer = ()  # 只在没定义only时defer生效，only一旦定义defer失效
