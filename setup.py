from setuptools import setup

setup(
    name='gg',
    version='0.0.1',
    author='Peter Bengtsson',
    author_email='mail@peterbe.com',
    url='https://github.com/peterbe/gg',
    description='Git and GitHub command line swiss army knife',
    # py_modules=['gg'],
    install_requires=[
        'click',
        'colorama',
    ],
    entry_points="""
        [console_scripts]
        gg=gg.main:cli
    """,
)
