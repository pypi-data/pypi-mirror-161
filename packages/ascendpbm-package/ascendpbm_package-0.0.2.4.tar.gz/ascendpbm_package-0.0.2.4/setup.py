from setuptools import setup, find_packages

VERSION = '0.0.2.04'
DESCRIPTION = "Common methods for handling ascendpbm's IT needs."
LONG_DESCRIPTION = ('This is a growing library intended to make use of other python packages streamlined and scaleable for ascendpbm.'
                    + ' It is to include tools for interfacing with FTP, SFTP, FTPS, email, Microsoft Graph API, PostgreSQL, bash scripts,'
                    + ' reporting infrastructure/packages, and much more. Please note that it will require several unlisted dependencies and'
                    + ' requirements such as our business environments, Anaconda installations, and many python packages.')

# Setting up
setup(name="ascendpbm_package",
      version=VERSION,
      author="Ian Kapenga",
      author_email="<ikapenga@optimedhp.com>",
      maintainers=["Lucas Dominick"],
      maintainer_email="<l.dominick@ascendpbm.com>",
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      packages=find_packages(),
      install_requires=['pandas', 'datetime', 'O365', 'pyodbc', 'numpy', 'requests_ntlm'],
      keywords=['python', 'pbm', 'pharmacy', 'employer insurance', 'ascendpbm', 'business logic'],
      classifiers= ["Development Status :: 3 - Alpha",
                    "Intended Audience :: Other Audience",
                    "Programming Language :: Python :: 3",
                    "Operating System :: Microsoft :: Windows",
                    ]
     )
