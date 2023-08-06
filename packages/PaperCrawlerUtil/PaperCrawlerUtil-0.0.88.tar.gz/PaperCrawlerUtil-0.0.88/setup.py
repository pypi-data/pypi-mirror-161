# -*- coding: utf-8 -*-
# @Time    : 2022/7/3 21:38
# @Author  : 银尘
# @FileName: setup.py.py
# @Software: PyCharm
# @Email   ：liwudi@liwudi.fun
import setuptools  # 导入setuptools打包工具

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PaperCrawlerUtil",  # 用自己的名替换其中的YOUR_USERNAME_
    version="0.0.88",  # 包版本号，便于维护版本
    author="liwudi.fun",  # 作者，可以写自己的姓名
    author_email="154125960@qq.com",  # 作者联系方式，可写自己的邮箱地址
    description="a collection of utils used to create crawler and document process",  # 包的简述
    long_description=long_description,  # 包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    url="https://github.com/Liwu-di/PaperCrawlerUtil",  # 自己项目地址，比如github的项目地址
    packages=setuptools.find_packages(exclude=["PaperCrawlerUtil.logs"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['aiohttp==3.8.1', 'attr==0.3.1', 'attrs==20.3.0', 'beautifulsoup4==4.11.1', 'environs==9.5.0',
                      'fake_headers==1.0.2', 'fake_useragent==0.1.11', 'Flask==1.1.4', 'gevent==21.12.0',
                      'googletrans==4.0.0rc1', 'loguru==0.6.0', 'lxml==4.9.0', 'pdf2docx==0.5.4',
                      'pdfplumber==0.7.1', 'pyquery==1.4.3', 'requests==2.28.1', 'retrying==1.3.3',
                      'setuptools==61.2.0', 'tornado==6.1', 'redis==3.5.3', 'markupsafe==2.0.1', 'PyPDF2==2.4.2',
                      'tqdm==4.64.0', 'PyExecJS==1.6.1'],
    python_requires='>=3.6',  # 对python的最低版本要求
    include_package_data=True,

)
