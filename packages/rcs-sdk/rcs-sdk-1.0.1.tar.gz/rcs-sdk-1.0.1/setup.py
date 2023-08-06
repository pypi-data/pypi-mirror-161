"""
  模块描述：
  @author 8526
  @date 2022-04-29 10:58:07
  版权所有 Copyright www.dahantc.com
"""
import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='rcs-sdk',
    version='1.0.1',
    author='8526',
    description='大汉三通',
    long_description='RCS 平台业务功能调用',
    url='https://gitee.com/dahanrcs/sdk-python',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
