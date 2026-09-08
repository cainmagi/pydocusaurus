# pyDocusaurus: Convert your Python docstrings to Docusaurus Documentation

{:toc}

## CHANGELOG

### 1.0.0 @ 09/08/2026

#### :mega: New

1. Integrate the resource files, including Jinja2 templates, into the package rendering.

#### :wrench: Fix

1. Fix: Correct the missing icon import when solving the rendered pages.
2. Fix: Bump the typescript annotations to the newest React version.
3. Fix: Correct the bugs of the broken sidebar and internal links.
4. Fix: Correct some MDX rendering and format issues, especially for text escaping configurations.
5. Fix: Correct the bad import of iconify icons.
6. Fix: Remove the unwanted namespace pacakges in the package member list.
7. Fix: Add two missing names in the `__all__` list of submodules.
8. Fix: Add missing docstring of `core.modules.DocModuleMetadata.from_long_descr`.
9. Fix: Add the missing icon of the `isEnum` case.
10. Fix: Correct the test package to match the namespace skipping rules (see Fix 6 of this update).

#### :floppy_disk: Change

1. Set the exposed port `3000` for the docker project.
2. Split the `renderer.package.Saver*` into a separated module `renderer.saver`.
3. Remove the legacy option `onBrokenMarkdownLinks`.
4. Temporarilly drop the escaping of `{}` symbols. These symbols can be manually dealt with code wrappers.
5. Add the customization option of `--user`/`-u` in CLIs and examples.

### 1.0.0 @ 09/03/2026

#### :mega: New

1. Create this project.
2. Finish the `core` package with package analysis functionalities.
3. Finish the `components` package with component-rendering functionalities.
4. Finish the `renderer` package for rendering documentation pages.
5. Finish the CLIs.
6. Finish GitHub configurations and actions.

#### :floppy_disk: Change

1. Drop the support for `Python 3.13` because it does not support `annotationlib`.
2. Improve the code structure for maintaing the implementation complexity.
