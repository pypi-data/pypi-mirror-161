import setuptools
from distutils.core import setup

setup(
    name="zfun",
    version="2.0.0",
    author="Haiyang Zheng",
    author_email="wnfdsfy@gmail.com",
    packages=setuptools.find_packages(),
    url="https://github.com/zhenghy/zpy",
    license="MIT",
    description="个人常用函数库",
    long_description=open("README.MD", "r").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "pymysql",
        "dash_mantine_components",
        "dash_tabulator",
        "PyPDF2",
        "winrm",
        "sqlalchemy",
        "fastapi",
        "aiofiles",
        "reportlab",
        "pandas",
    ],
    keywords=["common", "function", "class"],
    platforms="any",
)
