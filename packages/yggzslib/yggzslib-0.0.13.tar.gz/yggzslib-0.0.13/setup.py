import setuptools
with open('bbh.txt') as f:
    version=f.read()
setuptools.setup(
    name='yggzslib',#库名
    version=version,#版本号，建议一开始取0.0.1
    author='Haoyang Zhang',#你的名字，名在前，姓在后，例：张一一 Yiyi Zhang
    author_email='1@yangguang-gongzuoshi.top',#你的邮箱（任何邮箱都行，只要不是假的）
    description='阳光工作室',#库介绍
    long_descripition_content_type="text/markdown",
    url='https://github.com/',
    packages=setuptools.find_packages(),
    classifiers= [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent" ,
    ],
)
