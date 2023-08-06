import types
from typing import Tuple
from django.http import HttpRequest
from django.forms import Form
from .pick_form import pick_form

__all__ = ['RequestMethodError',
           'FormValidationError',
           'form_validator',
           'FormValidator']


class RequestMethodError(Exception):
    """请求方法错误"""


class FormValidationError(Exception):
    """表单验证失败"""


def form_validator(form_class: Form, must_method: str = None):
    """
    检查form参数
    请求方法验证失败抛出 RequestMethodError 异常
    表单验证不通过时抛出 FormValidationError 异常
    :param form_class:Django form class
    :param must_method: POST or GET

    @form_validator(LoginForm, must_method="POST")
    def login(request):
        pass
    """

    def wrap(func):
        def core(*args, **kwargs):
            request = next(i for i in args if isinstance(i, HttpRequest))
            if must_method and request.method != must_method:
                raise RequestMethodError(f'必须为{must_method}请求！')
            form = form_class(getattr(request, request.method))
            if not form.is_valid():
                raise FormValidationError(form.errors)
            return func(*args, **kwargs)

        return core

    return wrap


class FormValidator:
    """
    # 先定义一个APPForm，可以将应用中需要验证的字段都放到APPForm中
    class APPForm(forms.Form):
        username = forms.CharField(required=True)
        password = forms.CharField(required=True)
        email = forms.CharField(required=True)
        phone = forms.CharField(required=True)

    # 定义一个表单验证器
    class LoginFormValidator(FormValidator):
        must_method = 'POST'
        target_form = APPForm # APPForm作为目标Form
        fields = ('username', 'password') # 根据fields从目标Form中生成相应字段的Form

    # API 接口中使用
    @LoginFormValidator
    def login(request):
        return JsonResponse({'result': 'ok'})

    """
    # 指定的请求方法，为None则不限制请求方法
    must_method = 'POST'
    # pick_form使用的字段，也就是需要验证的字段
    fields: Tuple[str] = None
    # 目标Form, pick_form会从目标目标Form根据fields生成一个Form Class
    target_form: Form = None

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        request = next(i for i in args if isinstance(i, HttpRequest))
        # 检查请求方法
        if self.must_method and request.method != self.must_method:
            raise RequestMethodError(f'必须为{self.must_method}请求！')
        # 检查表单验证
        form = self.form_class(getattr(request, request.method))
        if not form.is_valid():
            raise FormValidationError(dict(form.errors))

        return self.func(*args, **kwargs)

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return types.MethodType(self, instance)

    def __init_subclass__(cls, **kwargs):
        meta = cls.__dict__.get('Meta', None)
        is_abstract = getattr(meta, 'abstract', False)
        if is_abstract:  # 作为抽象基类不检查类定义
            return

        if not cls.target_form:
            raise RuntimeError(f'{cls.__name__} 必须指定一个 target_form')

        if not cls.fields:
            raise RuntimeError(f'{cls.__name__} 必须定义一个fields元组')
        # pick一个From类
        cls.form_class = pick_form(*cls.fields, target_form=cls.target_form)
