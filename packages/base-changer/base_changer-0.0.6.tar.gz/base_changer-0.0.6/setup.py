import setuptools

setuptools.setup(
    name = "base_changer",
    author = "Harsh Gupta",
    version='0.0.6',
    author_email = "harshnkgupta@gmail.com",
    description = "Number System converter",
    long_description="This module can be used to convert one Number System to another.\n\n Syntax: \n\n >>>import base_changer \n\n To convert Octal to Decimal …Type: \n\n >>>base_changer.converter.oct_to_dec(734) \n\n To view all the available functions.. Type >>>base_changer.index() \n\n\nType >>>base_changer.help() for further help.",
    packages=['base_changer'],
    install_requires=[]
    )
