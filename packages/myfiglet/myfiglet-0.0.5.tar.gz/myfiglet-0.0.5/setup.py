import setuptools

setuptools.setup(
    name = "myfiglet",
    author = "Harsh Gupta",
    version='0.0.5',
    author_email = "harshnkgupta@gmail.com",
    description = "FIGlet Using Python",
    long_description="This module can be used to display FIGlet fonts using python. This is a simple,standalone and easy to understand module with zero dependency on external packages.Best use case is, it can be used in unison with different programs to make them more lively and attarctive.\n\n Syntax: \n\n >>>import myfiglet \n\n >>>myfiglet.display(<input_string>,<symbol>) \n\n Example: >>>myfiglet.display( 'Python' , '%') \n\n Example: >>>myfiglet.display( 'Harsh' , pattern='name') \n\n\nType >>>myfiglet.help() for further help.",
    packages=['myfiglet'],
    install_requires=[]
    )
