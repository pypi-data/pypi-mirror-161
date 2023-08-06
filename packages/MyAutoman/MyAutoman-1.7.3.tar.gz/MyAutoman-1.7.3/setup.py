#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages  

setup(
    name='MyAutoman',  # 包的名字
    author='wwj&zqy',  # 作者
    version='1.7.3',  # 版本号
    license='BSD License',

    description='Automan',  # 描述
    long_description='''Automan''',
    author_email='wangwenjie@smyfinancial.com',  # 你的邮箱**
#    url='',
    # 包内需要引用的文件夹
    # packages=setuptools.find_packages(exclude=['url2io',]),
    packages=find_packages(),
    include_package_data=True,
    # keywords='NLP,tokenizing,Chinese word segementation',
    # package_dir={'jieba':'jieba'},
    # package_data={'jieba':['*.*','finalseg/*','analyse/*','posseg/*']},

    # 依赖包
    install_requires=[
        'xgboost == 1.0.2',
        "scikit-learn == 0.22.2.post1",
        "numpy == 1.18.2",
        "pandas >= 0.25.3",
        "hyperopt == 0.2.3",
        "matplotlib == 3.2.1",
        "scipy == 1.4.1",
        "statsmodels == 0.11.1",
        "seaborn == 0.10.0",
        "Cython",
        "XlsxWriter",
        "openpyxl == 3.0.3",
        "imblearn == 0.0",
        "joblib == 0.14.1",
        "lightgbm == 2.2.3",
        "imbalanced-learn == 0.6.2",
        "XlsxWriter == 1.2.8",
        "tqdm==4.45.0",
        "m2cgen==0.9.0",
        "pympler==0.9",
        "protobuf==3.17.3",
        "absl-py==0.13.0",
        "ortools==9.0.9048",
        "optbinning==0.8.0",
        "dill==0.3.4",
        "pyod==0.9.7",
        "xlrd==1.2.0",
        "shap==0.40.0",
    ],
    # classifiers=[
    #     "Programming Language :: Python :: 3",
    #     "License :: OSI Approved :: wwj License",
    #     "Operating System :: windosw Independent",
    # ],
    zip_safe=True,
)
