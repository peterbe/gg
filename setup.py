from setuptools import setup

setup(
    name='gg',
    version='0.1',
    # py_modules=['gg'],
    install_requires=[
        'click',
    ],
    entry_points="""
        [console_scripts]
        gg=gg.main:cli
    """,
)
