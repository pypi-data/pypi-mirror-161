from setuptools import setup, find_packages
exec(open("src/discord_joiner/_resources.py").read())

setup(
    name=__package_name__,
    version=__version__,
    author=__author__,
    author_email='battenetciz@gmail.com',
    description='Discord accounts joiner',
    install_requires=[
        'python-dotenv==0.19.2',
        'requests==2.27.1',
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

