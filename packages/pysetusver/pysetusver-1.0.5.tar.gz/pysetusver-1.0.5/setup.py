import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pysetusver",# 项目名称，保证它的唯一性，不要跟已存在的包名冲突即可
    version="1.0.5",#程序版本
    author="HANASE", # 项目作者
    author_email="shenziqian66@163.com",#作者邮件
    description="letmeseesee", # 项目的一句话描述
    long_description=long_description,#加长版描述？
    long_description_content_type="text/markdown",#描述使用Markdown
    packages=setuptools.find_packages(),#无需修改
    classifiers=[
        "Programming Language :: Python :: 3",#使用Python3
        "License :: OSI Approved :: Apache Software License",#开源协议
        "Operating System :: OS Independent",
    ],
)