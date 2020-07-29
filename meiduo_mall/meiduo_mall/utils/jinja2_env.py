from jinja2 import Environment
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage

def jinja2_environment(**options):
    # jinja2环境
    # 创建环境对象
    env = Environment(**options)
    # 自定义语法
    env.globals.update({
        'static': staticfiles_storage.url, #静态文件的一个前缀
        'url': reverse, #使用reverse命名空间
    })
    return env
