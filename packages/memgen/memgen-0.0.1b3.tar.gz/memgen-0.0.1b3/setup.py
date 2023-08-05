# -*- coding: utf-8 -*-
import re
from setuptools import setup, find_packages


def fix_images(content, project_url):
    return re.sub(r"\[([^\]]*)\]\(doc\/([^)]*)\.png\)", r"[\1]({}/-/raw/main/doc/\2.png)".format(project_url), content)


def fix_local_markdown_links(content, project_url):
    return re.sub(r"\[([^\]]*)\]\(doc\/([^)]*)\.md\)", r"[\1]({}/-/blob/main/doc/\2.md)".format(project_url), content)


def get_altered_readme(project_url):
    with open("README.md", "r", encoding="utf-8") as fp:
        return fix_local_markdown_links(fix_images(fp.read(), project_url), project_url)


project_url = "https://gitlab.com/cbjh/memgen/py-memgen"


setup(
    name="memgen",
    description="Calls MemGen service located at http://memgen.uni-saarland.de/api",
    url=project_url,
    long_description=get_altered_readme(project_url),
    long_description_content_type="text/markdown",
    author="Maciej Wójcik",
    author_email="w8jcik@gmail.com",
    classifiers=["Operating System :: POSIX :: Linux"],
    install_requires=['numpy'],
    use_scm_version=True,

    packages=find_packages(where="."),

    extras_require={
        "dev": ['mdanalysis', 'pytest'],
        "local": ['acpype ~= 2022.6.6'],
        "external": ['gmxapi', 'openbabel']
    },

    entry_points={
        'console_scripts': [
            'memgen=memgen:main',
        ]
    },

    setup_requires=['setuptools_scm']
)
