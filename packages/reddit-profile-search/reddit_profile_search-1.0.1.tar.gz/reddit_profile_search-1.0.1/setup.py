from setuptools import setup, find_packages


VERSION = '1.0.1'
DESCRIPTION = 'A basic profile search bot for Reddit'
LONG_DESCRIPTION = 'A basic profile search bot for Reddit'

# Setting up
setup(
    name="reddit_profile_search",
    version=VERSION,
    author="Abdessamad BAAHMED",
    author_email="baahmedabdessamad@outlook.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=["async-generator",
                        "attrs",
                        "beautifulsoup4",
                        "bs4",
                        "certifi",
                        "cffi",
                        "cryptography",
                        "h11",
                        "idna",
                        "outcome",
                        "pycparser",
                        "pyOpenSSL",
                        "PySocks",
                        "selenium",
                        "sniffio",
                        "sortedcontainers",
                        "soupsieve",
                        "trio",
                        "trio-websocket",
                        "urllib3",
                        "wsproto"
                        ],
    keywords=['python', 'reddit', 'profile', 'search'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)