import setuptools

setuptools.setup(
    name = "py_math_help",
    author = "Harsh Gupta",
    version='0.0.6',
    author_email = "harshnkgupta@gmail.com",
    description = "A Perfect Math Module For Beginners. ",
    long_description="This module is extensively designed for non-math coders and beginners. The user need not know math to solve complex math problems. This module does it all for you.The most special feature of this module is its search() function. Now Just search your query after importing the module and it would be resolved. This module consists over 50+ math formulas and is still developing.\n\n Syntax: \n\n >>>import py_math_help \n\n >>>py_math_help.search(<Type your problem here>) \n\n Example: >>>py_math_help.search(\'area of triangle\') \n\n Example: >>>py_math_help.search(\'convert binary to hexadecimal\') \n\n Example: >>>py_math_help.search(\'is 3557 a prime number\') \n\n\nType >>>py_math_help.help() for further help.",
    packages=['py_math_help'],
    install_requires=[]
    )
