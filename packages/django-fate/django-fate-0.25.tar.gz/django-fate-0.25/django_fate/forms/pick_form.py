from django import forms

__all__ = ['pick_form']


def pick_form(*fields: str, target_form) -> forms.Form:
    """根据fields提供的字段名，动态地从target_form中摘取所需字段，生成并返回一个Form Class
    :param fields: 生成Form的所需字段名
    :param target_form:摘取的目标Form
    :return:Form Class

    class AppForm(forms.Form):
        name = forms.CharField(required=True)
        phone = forms.CharField(required=True, min_length=11)
        username = forms.CharField(required=True)
        password = forms.CharField(required=True)
        .....

    LoginForm =pick_form('username','password',target_form=AppForm)
    等价于:
     class LoginForm(forms.Form):
        username = forms.CharField(required=True)
        password = forms.CharField(required=True)

    """
    if not issubclass(target_form, forms.Form):
        raise TypeError(f'{target_form.__name__}必须是Form的子类！')

    # 目标Form类中定义的所有字段字典
    target_fields = target_form.base_fields
    form_fields = {}  # 从目标类中收集的字段字典
    for field_name in fields:
        try:
            form_fields[field_name] = target_fields[field_name]
        except KeyError:
            raise ValueError(f'pick_form接受了一个{field_name}参数,但是{target_form.__name__}中未定义{field_name}')
        # clean部分
        try:
            form_fields['clean_' + field_name] = getattr(target_form, 'clean_' + field_name)
        except AttributeError:
            pass

    return type('Form', (forms.Form,), form_fields)
