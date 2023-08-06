from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

setup(
    name='tabassist',
    version='0.2.0',
    platforms='any',
    author='Mikhail Korotchenkov',
    author_email='mr.mkc19@hotmail.com',
    description='Command line utility to work with Tableau workbook faster.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dev-mkc19/tabassist",
    project_urls={
        "Bug Tracker": "https://github.com/dev-mkc19/tabassist/issues",
    },
    packages=find_packages(include=['tabassist', 'tabassist.*']),
    package_data={'tabassist': ['data/*']},
    python_requires=">=3.6",
    install_requires=[req for req in requirements if req[:2] != "# "],
    entry_points={
        'console_scripts': [
            'tabassist = tabassist.__main__:cli',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers'
    ],
    keywords='tableau cli-app',
)
