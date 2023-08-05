import setuptools

setuptools.setup(
    name = "myfiglet",
    author = "Harsh Gupta",
    version='0.0.4',
    author_email = "harshnkgupta@gmail.com",
    description = "FIGlet Using Python",
    long_description="This program can be used to display FIGlet fonts using python. This is a simple,standalone and easy to understand module with zero dependency on external packages.Best use case is, it can be used in unison with different programs to make them more lively and attarctive.\n\n Syntax: \n\n >>>import myfiglet \n\n >>>myfiglet.display(<input_string>,<symbol>) \n\n Example: >>>myfiglet.display('Harsh Gupta','%') \n\n Example: >>>myfiglet.display('Harsh Gupta',pattern='name') \n\n\nType >>>myfiglet.help() for further help.",
    packages=['myfiglet'],
    install_requires=[]
    )
