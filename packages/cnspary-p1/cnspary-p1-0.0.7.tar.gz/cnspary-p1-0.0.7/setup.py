from setuptools import find_packages, setup

setup(
    name='cnspary-p1',
    version='0.0.7',
    author='cnspary',
    author_email='cnspary@outlook.com',
    description='MC-PackageOne',
    packages=['mod1', 'mod1.submod' ,'mod2'],
    py_modules=['mod1'],
    python_requires='>=3.0'
)
