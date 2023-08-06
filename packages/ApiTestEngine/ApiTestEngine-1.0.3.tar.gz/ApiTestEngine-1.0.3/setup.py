"""
============================
Author:柠檬班-木森
Time:2020/7/16   16:20
E-mail:3247119728@qq.com
Company:湖南零檬信息技术有限公司
============================
"""
"""
python setup.py sdist bdist_wheel
twine upload dist/*

"""

from setuptools import setup, find_packages

with open("readme.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

setup(
    name='ApiTestEngine',
    version='1.0.3',
    author='MuSen',
    author_email='musen_nmb@qq.com',
    url='https://github.com/musen123/ApiTestEngine',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["Faker==13.4.0",
                      "jsonpath==0.82",
                      "PyMySQL==1.0.2",
                      'requests==2.27.1',
                      "requests-toolbelt==0.9.1",
                      "rsa==4.8"
                      ],
    packages=find_packages(),
    package_data={
        "": ['*.md',"*.py",],
    },
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
