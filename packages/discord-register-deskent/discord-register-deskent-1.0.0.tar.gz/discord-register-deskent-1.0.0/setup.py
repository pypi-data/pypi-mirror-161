from setuptools import setup, find_packages
exec(open("src/discord_register/_resources.py").read())

setup(
    name=__package_name__,
    version=__version__,
    author=__author__,
    author_email='battenetciz@gmail.com',
    description='Discord account register',
    install_requires=[
        'anticaptchaofficial==1.0.43',
        'aiohttp==3.8.1',
        'pydantic==1.9.1',
        'pydantic[email]',
        'python-dotenv==0.19.2',
        'myloguru-deskent==0.0.12',
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
)

