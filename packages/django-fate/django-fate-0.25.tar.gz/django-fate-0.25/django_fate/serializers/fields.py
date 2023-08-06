import json
from json.decoder import JSONDecodeError


class Field:
    def __init__(self):
        self.field = None

    def __get__(self, instance, owner):
        return self.process

    def __set_name__(self, owner, name):
        if self.field is None:
            self.field = name

    @classmethod
    def process(cls, value):
        # 整型和None类型不转换，布尔类型也是整型
        if isinstance(value, int) or value is None:
            return value
        else:
            return str(value)


class Foreignkey(Field):
    def __init__(self, serialize_class):
        super().__init__()
        self.serialize_class = serialize_class

    def process(self, value):
        if not value:
            return None
        return self.serialize_class(value)


class JsonTextField(Field):

    def process(self, value):
        if not value:
            return None
        try:
            return json.loads(value)
        except JSONDecodeError:
            return value
            # raise ValueError('json loads发生错误,字段:{} ！'.format(self.field))


class ImgField(Field):
    def __init__(self, host, media_url):
        super().__init__()
        self.host, self.media_url = host, media_url

    def process(self, value):
        if not value:
            return None
        return self.host + self.media_url + str(value)


class DateTimeField(Field):

    def process(self, value):
        if not value:
            return value
        return str(value)[0:19]


class ManyToManyField(Field):
    def __init__(self, serialize_class):
        super().__init__()
        self.serialize_class = serialize_class

    def __get__(self, instance, owner):
        self.instance = instance
        return self.process

    def process(self, model_obj):
        hook_name = 'hook_' + self.field
        hook_func = getattr(self.instance, hook_name, None)
        if hook_func:
            query_set = hook_func(model_obj)
        else:
            many_obj = getattr(model_obj, self.field, None)
            query_set = many_obj.all() if many_obj else ()
        return self.serialize_class(query_set)


class RelatedField(Field):
    """" 序列化相关表
    class A(models.Model):
        pass

    class B(models.Model):
        a = models.ForeignKey(A)

    在上述示例中model A作为外键被model B所关联，那么在序列化model A时可以使用RelatedField来添加model B的序列化:
    class ASerializers(Serializers):
        # b 是model B的类名的小写
        b = RelatedField(serialize_class=xxx)
        # 也可以使用"别名b", 但是需要在field中给出model B的类名的小写
        别名b = RelatedField(serialize_class=xxx, field="b")
    """

    def __init__(self, serialize_class, field=None):
        super().__init__()
        self.field = field
        self.serialize_class = serialize_class

    def __get__(self, instance, owner):
        self.instance = instance
        return self.process

    def __set_name__(self, owner, name):
        if self.field is None:
            self.field = name
        self.name = name  # 用于找到钩子函数名

    def process(self, model_obj):
        hook_name = 'hook_' + self.name
        hook_func = getattr(self.instance, hook_name, None)
        if hook_func:
            query_set = hook_func(model_obj)
        else:
            cross_obj = getattr(model_obj, self.field + '_set', None)
            query_set = cross_obj.all() if cross_obj else ()
        return self.serialize_class(query_set)
