from setuptools import setup, find_packages

author = 'Data & Analytics Research'
author_email = 'analytics.dar@take.net'
version = '0.0.6b2'
license = 'MIT License'
credits = ['Milo Utsch', 'Gabriel Oliveira']
name = 'take-text-preprocess'
maintainer = "daresearch"
maintainer_email = "anaytics.dar@take.net"
keywords = ['text', 'preprocessing']
description = 'Text Preprocesser'
long_description = open('README.md').read()
long_description_content_type = 'text/markdown'
classifiers = [
    'Programming Language :: Python :: 3',
    'Operating System :: OS Independent'
]

install_requires = [
    req
    for req in [
        line.split("#", 1)[0].strip()
        for line in open("requirements.txt", "r", encoding="utf-8")
    ]
    if req and not req.startswith("--")
]

setup(
    name=name,
    author=author,
    author_email=author_email,
    version=version,
    license=license,
    credits=credits,
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    keywords=keywords,
    description=description,
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    classifiers=classifiers,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=install_requires
)
