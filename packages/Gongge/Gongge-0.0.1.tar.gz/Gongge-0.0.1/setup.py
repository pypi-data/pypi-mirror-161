from setuptools import setup, find_packages
from os import path
# 读取readme文件，这样可以直接显示在主页上
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Gongge',
    version='0.0.1',
    keywords='img',
    description='一个九宫格图片生成库',
    license='MIT License',
    url='',
    author='xuehang',
    author_email='30290382@qq.com',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'Pillow~=9.2.0',
        'numpy~=1.23.1',
        'matplotlib~=3.5.2'
    ],
)
