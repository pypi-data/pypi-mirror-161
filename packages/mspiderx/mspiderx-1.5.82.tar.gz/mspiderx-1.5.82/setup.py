from setuptools import find_packages, setup

setup(
    name='mspiderx',  # 模块名
    version='1.5.82',  # 版本
    description='Perfect function',
    packages=find_packages(),  # 目录所有文件
    url='https://pypi.org/project/spiderx/',  # 文件文档下载地址
    author='wgnms',  # 作者名
    author_email='wgnms@qq.com',  # 邮箱
    install_requires=['requests>=2.25.0',
                      'lxml>=4.6.0',
                      'colorama>=0.4.0',
                      #'rsa>=4.7.0',
                      #'wmi>1.5.0',
                      #'pycryptodome>=3.10.0',
                      'pyinstaller>=4.5.0',
                      'openpyxl>=3.0.7',
                      'js2py>=0.71',
                      'pyexecjs>=1.5.1',
                      'pillow>=8.3.1',
                      'pymysql>=1.0.2',
                      'psutil>=5.9.0',
                      'chardet>=4.0.0',
                      'loguru>=0.6.0',
                      'jsonpath>=0.82',
                      'pyserial>=3.5'
                      # 'pymsgbox>=1.0.9',
                      # 'sqlalchemy>=1.4.22',
                      # 'tinyaes>=1.0.1',
                      # 'faker>=9.5.2',
                      # 'python-docx'
                      ],  # xx>=1.1
    python_requires=">=3.6"  # >=3.6,!=3.1.*
)
'''
python-docx 文档处理

python setup.py build
python setup.py sdist bdist_wheel

python setup.py build sdist bdist_wheel
twine upload dist/* 

#问题解决办法 
pywin32 运行错误
python C:\Python\Python38-32\Scripts\pywin32_postinstall.py -install  

no module named Crypto  模块错误
解决办法:
  site-packages目录下修改crypto文件夹为Crypto

运行 N_m3u8dl_Cli.exe 需要模拟输出控制台中的终端 选上
'''