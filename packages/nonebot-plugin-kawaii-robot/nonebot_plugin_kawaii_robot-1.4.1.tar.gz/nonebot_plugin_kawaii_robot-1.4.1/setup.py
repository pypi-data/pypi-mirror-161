from setuptools import setup,find_namespace_packages

setup(
name='nonebot_plugin_kawaii_robot',
version='1.4.1',
description='使用Kyomotoi / AnimeThesaurus的nonebot2的回复（文i）插件',
#long_description=open('README.md','r').read(),
author='karisaya',
author_email='1048827424@qq.com',
license='AGPLv3 License',
include_package_data=True,
packages=find_namespace_packages(include=["nonebot_plugin_kawaii_robot","nonebot_plugin_kawaii_robot.*"]),
platforms='all',
install_requires=["nonebot2","nonebot-adapter-onebot"],
url='https://github.com/KarisAya/nonebot_plugin_kawaii_robot',
)