from setuptools import setup

name = "types-regex"
description = "Typing stubs for regex"
long_description = '''
## Typing stubs for regex

This is a PEP 561 type stub package for the `regex` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `regex`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/regex. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `81a8e116385a823d690843d69a80bf85baf914c0`.
'''.lstrip()

setup(name=name,
      version="2022.7.25.0",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/regex.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['regex-stubs'],
      package_data={'regex-stubs': ['__init__.pyi', '_regex.pyi', '_regex_core.pyi', 'regex.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
