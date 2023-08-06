from setuptools import setup, find_packages
from os import path

# 读取readme文件，这样可以直接显示在主页上
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Gongge',
    version='0.0.2',
    keywords='img',
    description='九宫格图片分割，最简单的Python图像分割工具。',
    license='MIT License',
    url='https://github.com/xuehang00126',
    author='学航',
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
