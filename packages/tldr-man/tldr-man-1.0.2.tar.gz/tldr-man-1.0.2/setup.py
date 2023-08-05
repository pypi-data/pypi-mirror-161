# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tldr_man']

package_data = \
{'': ['*']}

install_requires = \
['click-help-colors>=0.9.1,<0.10.0',
 'click>=8.1.3,<9.0.0',
 'requests>=2.28.1,<3.0.0',
 'xdg>=5.1.1,<6.0.0']

entry_points = \
{'console_scripts': ['tldr = tldr_man:cli', 'tldr-man = tldr_man:cli']}

setup_kwargs = {
    'name': 'tldr-man',
    'version': '1.0.2',
    'description': 'Command-line TLDR client that displays tldr-pages as manpages',
    'long_description': '<div>\n    <h1 align="center">tldr-man-client</h1>\n    <h5 align="center">A tldr-pages client that works just like <code>man</code></h5>\n</div>\n\n`tldr-man-client` is a command-line client for [tldr-pages][tldr-pages],\na collection of community-maintained help pages for command-line tools.\nIt differs from other clients because it displays its pages as `man` pages.\n\nThis client is also able to integrate with the `man` command to fall back to displaying a tldr-page for a command when\nno manpage exists.\n\nFeatures:\n- Fully abides by the [tldr-pages client specification][client-spec].\n- Supports all page languages, not just English pages.\n- Displays tldr-pages in the same style as manpages.\n- Integrates with `man` to provide a fallback for missing manpages.\n- Supports rendering markdown formatted tldr-pages with `--render`.\n- Local cache abides by the [XDG base directory specification][xdg].\n- And much more!\n\n\n## Installation\n\n### With Homebrew\n\nInstall `tldr-man-client` with [Homebrew](https://brew.sh):\n\n```shell\nbrew install superatomic/tap/tldr-man\n```\n\n### With Pip\n\nInstall `tldr-man-client` with pip (version 3.10+):\n\n```shell\npip install tldr-man\n```\n\n`tldr-man-client` additionally depends on [`pandoc`](https://pandoc.org/installing.html) being installed.\n\nAfter installation, you can view a tldr-page with the `tldr` command.\n\n\n## Usage\n\n**Display a tldr-page for a command:**\n\n```shell\ntldr <COMMAND>\n```\n\n**Update the local page cache:**\n\n```shell\ntldr --update\n```\n\n**Render a page locally:**\n\n```shell\ntldr --render path/to/page.md\n```\n\n**Print tldr manpage paths as a colon-separated list (see the [Manpage Integration](#Manpage-Integration) section):**\n\n```shell\ntldr --manpath\n```\n\n**Display usage information:**\n\n```shell\ntldr --help\n```\n\n\n### Setting languages\n\n[As specified by the tldr-pages client specification][client-spec-language],\ntldr-pages from other languages can be displayed by this client\n(falling back to English if the page doesn\'t exist for that language).\n\nTo do so, set any of the environment variables `$LANG`, `$LANGUAGE`, or `$TLDR_LANGUAGE` to the two-letter language code\nfor your language (e.g. `export LANGUAGE=es`),\nor set the `--language` option when running `tldr` (e.g. `tldr <COMMAND> --language es`).\n\n\n### Setting platforms\n\nBy default, tldr-pages will be displayed based on your current platform.\nTo directly specify what platform\'s page to use, use the `--platform` flag.\n\nFor example, to display the macOS version of the `top` command\'s tldr-page, run `tldr top --platform macos`.\nThis is the default behavior on macOS,\nbut `--platform macos` is required to show the macOS version of this page on other platforms.\n\n\n## Manpage Integration\n\nThe command `man` can be set up to fall back to displaying tldr-pages if no manpages are found.\n\nTo do so,\nadd the provided line to your shell\'s startup script (e.g. `~/.bash_profile`, `~/.zshenv`, `~/.config/fish/config.fish`)\nto add this behavior to `man`:\n\n### Bash and Zsh\n\n```shell\nexport MANPATH="$MANPATH:$(tldr --manpath)"\n```\n\n### Fish\n\n```shell\nset -gxa MANPATH (tldr --manpath)\n```\n\n[tldr-pages]: https://github.com/tldr-pages/tldr\n[client-spec]: https://github.com/tldr-pages/tldr/blob/main/CLIENT-SPECIFICATION.md\n[client-spec-language]: https://github.com/tldr-pages/tldr/blob/main/CLIENT-SPECIFICATION.md#language\n[xdg]: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html\n',
    'author': 'Ethan Kinnear',
    'author_email': 'contact@superatomic.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://tldr-man.superatomic.dev/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
