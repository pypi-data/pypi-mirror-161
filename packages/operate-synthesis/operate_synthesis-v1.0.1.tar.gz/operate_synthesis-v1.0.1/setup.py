from distutils.core import setup
setup(
    name='operate_synthesis',# 需要打包的名字,即本模块要发布的名字
    version='v1.0.1',#版本
    description='Make Python simpler', # 简要描述
    packages=['opsy'],
    py_moudles=["opsy.pa","opsy.fo","opsy.gui"],#  需要打包的模块
    author='Anonymous_user2.3333', # 作者名
    author_email='pagain@163.com',   # 作者邮件
##    url='https://github.com/vfrtgb158/email', # 项目地址,一般是代码托管的网站
    requires=["wxPython"], # 依赖包,如果没有,可以不要
)
