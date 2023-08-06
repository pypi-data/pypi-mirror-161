from setuptools import setup

name = "types-pyvmomi"
description = "Typing stubs for pyvmomi"
long_description = '''
## Typing stubs for pyvmomi

This is a PEP 561 type stub package for the `pyvmomi` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `pyvmomi`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/pyvmomi. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `7953848101f734c590eaac2918034cebe609ab49`.
'''.lstrip()

setup(name=name,
      version="7.0.8",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/pyvmomi.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['pyVmomi-stubs'],
      package_data={'pyVmomi-stubs': ['__init__.pyi', 'vim/__init__.pyi', 'vim/event.pyi', 'vim/fault.pyi', 'vim/option.pyi', 'vim/view.pyi', 'vmodl/__init__.pyi', 'vmodl/fault.pyi', 'vmodl/query.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
