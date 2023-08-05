import setuptools


def readme():
    with open("README.md", "r") as fh:
        long_description = fh.read()
    return long_description


def install_requires():
    return ['requests']


setuptools.setup(
    name="wedata",
    version="0.0.10",
    # author="Example Author",
    # author_email="author@example.com",
    # description="A small example package",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(
        where='.',
        exclude=['tests']
    ),

    # data_files=[
    #     ('', ['conf/*.conf']),
    #     ('/usr/lib/systemd/system/', ['bin/*.service']),
    # ],
    #
    # # 希望被打包的文件
    # package_data={
    #     '': ['*.txt'],
    #     'bandwidth_reporter': ['*.txt']
    # },
    # # 不打包某些文件
    # exclude_package_data={
    #     'bandwidth_reporter': ['*.txt']
    # },

    classifiers=[
        # 发展时期,常见的如下
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # 开发的目标用户
        'Intended Audience :: Developers',

        # # 属于什么类型
        # 'Topic :: Software Development :: Build Tools',

        # 许可证信息
        'License :: OSI Approved :: MIT License',

        # 目标 Python 版本
        "Programming Language :: Python :: 3",
    ],

    install_requires=['requests', 'numpy', 'pandas'],
    python_requires='>=3'
)