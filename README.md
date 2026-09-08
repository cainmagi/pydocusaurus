# pyDocusaurus: Convert your Python docstrings to Docusaurus Documentation

<p><img alt="Banner" src="https://github.com/cainmagi/pydocusaurus/blob/main/display/logo-banner.webp?raw=true"></p>

<p align="center">
  <a href="https://github.com/cainmagi/pydocusaurus/releases/latest"><img alt="GitHub release (latest SemVer)" src="https://img.shields.io/github/v/release/cainmagi/pydocusaurus?logo=github&sort=semver&style=flat-square"></a>
  <a href="https://github.com/cainmagi/pydocusaurus/releases"><img alt="GitHub all releases" src="https://img.shields.io/github/downloads/cainmagi/pydocusaurus/total?logo=github&style=flat-square"></a>
  <a href="https://github.com/cainmagi/pydocusaurus/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/cainmagi/pydocusaurus?style=flat-square&logo=opensourceinitiative&logoColor=white"></a>
  <a href="https://pypi.org/project/pydocusaurus"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/pydocusaurus?style=flat-square&logo=pypi&logoColor=white&label=pypi"/></a>
</p>
<p align="center">
  <a href="https://github.com/cainmagi/pydocusaurus/actions/workflows/python-package.yml"><img alt="GitHub Actions (Build)" src="https://img.shields.io/github/actions/workflow/status/cainmagi/pydocusaurus/python-package.yml?style=flat-square&logo=githubactions&logoColor=white&label=build"></a>
  <a href="https://github.com/cainmagi/pydocusaurus/actions/workflows/python-publish.yml"><img alt="GitHub Actions (Release)" src="https://img.shields.io/github/actions/workflow/status/cainmagi/pydocusaurus/python-publish.yml?style=flat-square&logo=githubactions&logoColor=white&label=release"></a>
</p>

This package is inspired by Sphinx, which is usually thought of as the "official" solution for auto-generated Python documentation. According to Sphinx's documentation, the automatic generation can be described as:

> <p>Generate API documentation for Python, C++ and other software domains, manually or automatically from docstrings, ensuring your code documentation stays up-to-date with minimal effort.</p>
> <cite><p align="right">——Sphinx</p></cite>

Overall, this package offers similar functionalities to Sphinx. It goes through the docstrings in the whole package and reorganizes them as an automatically generated API document. However, **pyDocusaurus is not an extension of Sphinx**, because

1. Sphinx is old. It was designed in an era when typing or type hints were not part of the Python standard library (STL). Therefore, Sphinx needs to infer the types from the docstrings. In modern Python code, this feature is redundant.
2. Sphinx is essentially proposed for reStructuredText (rst). Certainly, it supports Markdown with specific extensions. However, the Markdown features, especially those related to variable types, are not well integrated with the automatically generated API documents. Users may still suffer a lot of rst code in the generated document.
3. Limited by the old-school template, Sphinx does not produce a "modern" website.

Essentially, this package will produce a "patch" for a Docusaurus project. Like Sphinx, **pyDocusaurus will go through the whole package and convert the docstring into a Docusaurus-compatible API document**, while requiring minimal modifications when integrating the auto-generated document with an existing Docusaurus project (e.g., an existing tutorial site).

## 1. Install

Intall the **latest released version** of this package by using the PyPI source:

```sh
python -m pip install pydocusaurus
```

## 2. Usage

A simple usage is to use the CLI directly:

```sh
python -m pydocusaurus render-doc <package-name> -o <out-dir> -u <user-name>
```

It allows customizations by adding CLI options. To find the details, review the documentation of this project or call

```sh
python -m pydocusaurus render-doc --help
```

pyDocusaurus can also be called by Python codes, for example:

```python
from pydocusaurus import render_package_as_mdx
import any_package

pydocusaurus.render_package_as_mdx(
    pydocusaurus, out_dir=out_dir, package_info="username"
)
```

## 3. Documentation

Check the documentation to find more details about the examples and APIs.

https://cainmagi.github.io/pydocusaurus/

## 4. Contributing

See [CONTRIBUTING.md :book:][link-contributing]

## 5. Changelog

See [Changelog.md :book:][link-changelog]

[link-contributing]: https://github.com/cainmagi/pydocusaurus/blob/main/CONTRIBUTING.md
[link-changelog]: https://github.com/cainmagi/pydocusaurus/blob/main/Changelog.md
