
import setuptools
#from setuptools import setup

setuptools.setup(
    name='pybaiduphoto',
    scripts=[] ,
    version='2022.08.01.2217',
    author='Hengyue Li',
    author_email='305069590@qq.com',
    packages=setuptools.find_packages(),
    license='LICENSE.md',
    description='A simple API to interact with baidu-photo',
    long_description=open('README.md',encoding="utf8").read(),
    long_description_content_type="text/markdown",
    install_requires=['requests>=2.22.0', 'rich==10.16.1'],
    python_requires='>=3.6',
    url = "https://github.com/HengyueLi/baiduphoto",
)
