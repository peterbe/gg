from setuptools import setup, find_packages

setup(
    name='gg',
    version='0.0.2',
    author='Peter Bengtsson',
    author_email='mail@peterbe.com',
    url='https://github.com/peterbe/gg',
    description='Git and GitHub command line swiss army knife',
    license='MIT',
    # py_modules=['gg'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'colorama',
    ],
    entry_points="""
        [console_scripts]
        gg=gg.main:cli
    """,
)
