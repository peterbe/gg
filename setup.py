from setuptools import setup

setup(
    name='gg',
    version='0.0.1',
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
