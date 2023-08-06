from setuptools import setup, find_packages
'''
python setup.py sdist
twine upload dist/* 
1120191060
dh20001108
'''


setup(
    name = 'mylib_donghao',
    version = '0.2.2',
    keywords='mylib_donghao',
    description = 'A pythono package by DONG HAO about machine learing and other math problems, which is just in test.\n'
                  + 'all classes have print function if needed and print it is of no use'
                  + '\nIn version 0.2.2, I repaired the problem in dropout. Now you can see AddADropoutPlease.',
    license = 'MIT License',
    url = 'https://github.com/',
    author = 'Hao Dong',
    author_email = '1440027762@qq.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = ['numpy', 'pulp', 'scipy', 'matplotlib', 'torch', 'torchvision'],
)