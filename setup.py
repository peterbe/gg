from os import path
from setuptools import setup, find_packages

_here = path.dirname(__file__)


setup(
    name='gg',
    version='0.0.13',
    author='Peter Bengtsson',
    author_email='mail@peterbe.com',
    url='https://github.com/peterbe/gg',
    description='Git and GitHub for the productivity addicted',
    long_description=open(path.join(_here, 'README.rst')).read(),
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'click',
        'colorama',
        'requests',
        'GitPython',
    ],
    entry_points="""
        [console_scripts]
        gg=gg.main:cli
    """,
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-mock'],
)
