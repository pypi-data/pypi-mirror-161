import re

import setuptools

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()


with open("disnake_ext_components/__init__.py", encoding="utf-8") as f:
    if match := re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.M):
        version = match.group(1)
    else:
        raise RuntimeError("Version has not been set.")

setuptools.setup(
    name="disnake-ext-components",
    author="Disnake Community",
    url="https://github.com/DisnakeCommunity/disnake-ext-components",
    version=version,
    package_dir={"disnake.ext.components": "disnake_ext_components"},
    license="MIT",
    description="A component listener wrapper for disnake",
    long_description=open("readme.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    install_requires=requirements,
    python_requires=">=3.8.0",
    include_package_data=True,
    package_data={"disnake.ext.components": ["py.typed"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
