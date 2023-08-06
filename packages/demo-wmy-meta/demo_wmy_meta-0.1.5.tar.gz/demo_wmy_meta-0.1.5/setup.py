from setuptools import setup, find_packages

setup(
    name = 'demo_wmy_meta',
    version = '0.1.5',
    keywords='MetaApp',
    description = '手写python库',
    license = 'MIT License',
    url = 'https://github.com/UpMing19/python_library',
    author='mingyu.wang',
    author_email = 'mingyu.wang@appshahe.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = [],
)