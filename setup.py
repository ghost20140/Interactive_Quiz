from setuptools import setup, find_packages
setup(
    name="chapter-quiz-app",
    version="0.1.0",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "Flask>=3.0.0,<4.0.0",
        "Flask-Cors>=4.0.0,<5.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={"console_scripts": ["quiz-server=server:app"]},
)
