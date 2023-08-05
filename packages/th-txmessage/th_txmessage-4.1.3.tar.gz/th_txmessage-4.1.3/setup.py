from setuptools import setup, find_packages

setup(name='th_txmessage',  # 打包后的包文件名
      version='4.1.3',  # 版本号
      description='听海内部爬虫核心类库',  # 说明
      long_description="听海爬虫组一些核心代码集合",  # 详细说明
      license="MIT Licence",  # 许可
      url='',
      author='wzr',
      author_email='510540795@qq.com',
      packages=find_packages(),  # 这个参数是导入目录下的所有__init__.py包
      include_package_data=True,
      platforms="any",
      install_requires=["apscheduler", "qcloud-cmq-sdk-py3", "requests", "retry"],  # 引用到的第三方库
      # py_modules=['pip-test.DoRequest', 'pip-test.GetParams', 'pip-test.ServiceRequest',
      #             'pip-test.ts.constants', 'pip-test.ac.Agent2C',
      #             'pip-test.ts.ttypes', 'pip-test.ac.constants',
      #             'pip-test.__init__'],  # 你要打包的文件，这里用下面这个参数代替
      # packages=[''] # 这个参数是导入目录下的所有__init__.py包
      )
