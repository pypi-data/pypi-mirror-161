import setuptools

setuptools.setup(
    # 名称
    name='tools-lmself',

    # 版本号
    version='0.0.14',

    # 作者
    author='upcoder',

    # 邮箱
    auther_email='',

    # 描述
    description='工具包',

    # 详细描述
    long_description=open('README.md', 'r', encoding='utf-8').read(),

    # README的格式
    long_description_content_type='text/markdown',

    # 项目的地址
    url='',

    # 打包时需要加入的模块
    packages=setuptools.find_packages(),

    # 项目的依赖库,读取requirements.txt内容
    install_requires=open('requirements.txt', 'r', encoding='utf-8').read(),

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
