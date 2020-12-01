# -*- coding: utf-8 -*-

import os
import setuptools

def get_requirements():

    req_files = ["./requirements.txt"]
    dirname = os.path.abspath(os.path.dirname(__file__))

    install_requires = []
    for req_file in req_files:
        with open(os.path.join(dirname, req_file), 'rt') as f:
            for line in f:
                try:
                    req = line[: line.index('#')].strip()
                except:
                    req = line.strip()
                if req:
                    install_requires.append(req)
    return install_requires

with open("./README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="mytwitter",
    version="0.1.1",
    author="Borja Gil Pérez",
    author_email="borjagilperez@outlook.com",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering'],
    description="Twitter utilities",
    include_package_data=True,
    install_requires=get_requirements(),
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    url="www.github.com/borjagilperez/twitter",
    zip_safe=False
)
