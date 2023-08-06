from setuptools import setup, find_packages


setup(
    name='Gongge',
    version='0.0.6',
    keywords='img',
    description='九宫格图片分割，最简单的Python图像分割工具。',
    license='MIT License',
    url='https://github.com/xuehang00126',
    author='学航',
    author_email='30290382@qq.com',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    long_description=open('README.md',encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'Pillow~=9.2.0',
        'numpy~=1.23.1',
        'matplotlib~=3.5.2'
    ],
)
