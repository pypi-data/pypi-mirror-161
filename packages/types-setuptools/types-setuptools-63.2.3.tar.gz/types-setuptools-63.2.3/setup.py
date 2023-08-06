from setuptools import setup

name = "types-setuptools"
description = "Typing stubs for setuptools"
long_description = '''
## Typing stubs for setuptools

This is a PEP 561 type stub package for the `setuptools` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `setuptools`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/setuptools. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `bd7a02fad4ce7cac48cfff17a7eaac1d7047faa5`.
'''.lstrip()

setup(name=name,
      version="63.2.3",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/setuptools.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['setuptools-stubs', 'pkg_resources-stubs'],
      package_data={'setuptools-stubs': ['__init__.pyi', '_deprecation_warning.pyi', '_distutils/__init__.pyi', '_distutils/archive_util.pyi', '_distutils/bcppcompiler.pyi', '_distutils/ccompiler.pyi', '_distutils/cmd.pyi', '_distutils/command/__init__.pyi', '_distutils/command/bdist.pyi', '_distutils/command/bdist_dumb.pyi', '_distutils/command/bdist_msi.pyi', '_distutils/command/bdist_rpm.pyi', '_distutils/command/bdist_wininst.pyi', '_distutils/command/build.pyi', '_distutils/command/build_clib.pyi', '_distutils/command/build_ext.pyi', '_distutils/command/build_py.pyi', '_distutils/command/build_scripts.pyi', '_distutils/command/check.pyi', '_distutils/command/clean.pyi', '_distutils/command/config.pyi', '_distutils/command/install.pyi', '_distutils/command/install_data.pyi', '_distutils/command/install_egg_info.pyi', '_distutils/command/install_headers.pyi', '_distutils/command/install_lib.pyi', '_distutils/command/install_scripts.pyi', '_distutils/command/py37compat.pyi', '_distutils/command/register.pyi', '_distutils/command/sdist.pyi', '_distutils/command/upload.pyi', '_distutils/config.pyi', '_distutils/core.pyi', '_distutils/cygwinccompiler.pyi', '_distutils/debug.pyi', '_distutils/dep_util.pyi', '_distutils/dir_util.pyi', '_distutils/dist.pyi', '_distutils/errors.pyi', '_distutils/extension.pyi', '_distutils/fancy_getopt.pyi', '_distutils/file_util.pyi', '_distutils/filelist.pyi', '_distutils/log.pyi', '_distutils/msvccompiler.pyi', '_distutils/spawn.pyi', '_distutils/sysconfig.pyi', '_distutils/text_file.pyi', '_distutils/unixccompiler.pyi', '_distutils/util.pyi', '_distutils/version.pyi', 'archive_util.pyi', 'build_meta.pyi', 'command/__init__.pyi', 'command/alias.pyi', 'command/bdist_egg.pyi', 'command/bdist_rpm.pyi', 'command/build_clib.pyi', 'command/build_ext.pyi', 'command/build_py.pyi', 'command/develop.pyi', 'command/dist_info.pyi', 'command/easy_install.pyi', 'command/egg_info.pyi', 'command/install.pyi', 'command/install_egg_info.pyi', 'command/install_lib.pyi', 'command/install_scripts.pyi', 'command/py36compat.pyi', 'command/register.pyi', 'command/rotate.pyi', 'command/saveopts.pyi', 'command/sdist.pyi', 'command/setopt.pyi', 'command/test.pyi', 'command/upload.pyi', 'command/upload_docs.pyi', 'config.pyi', 'dep_util.pyi', 'depends.pyi', 'dist.pyi', 'errors.pyi', 'extension.pyi', 'extern/__init__.pyi', 'glob.pyi', 'installer.pyi', 'launch.pyi', 'monkey.pyi', 'msvc.pyi', 'namespaces.pyi', 'package_index.pyi', 'sandbox.pyi', 'unicode_utils.pyi', 'version.pyi', 'wheel.pyi', 'windows_support.pyi', 'METADATA.toml'], 'pkg_resources-stubs': ['__init__.pyi', 'py31compat.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
