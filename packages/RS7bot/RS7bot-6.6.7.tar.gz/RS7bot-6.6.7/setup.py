import setuptools
    
setuptools.setup(
    name="RS7bot",
    version="6.6.7",
    author="Aeroz",
    description="Lobby bot.",
    url="https://www.youtube.com/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'crayons',
        'fortnitepy',
        'BenBotAsync',
        'FortniteAPIAsync',
        'uvloop',
        'sanic==21.6.2',
        'colorama',
        'aiohttp'
    ],
)
