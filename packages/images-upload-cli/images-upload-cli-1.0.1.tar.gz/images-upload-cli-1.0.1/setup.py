# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['images_upload_cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.2,<9.0.0',
 'pillow>=9.1.1,<10.0.0',
 'pyperclip>=1.8.2,<2.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'requests>=2.25.1,<3.0.0']

entry_points = \
{'console_scripts': ['images-upload-cli = images_upload_cli.cli:cli']}

setup_kwargs = {
    'name': 'images-upload-cli',
    'version': '1.0.1',
    'description': 'Upload images via APIs',
    'long_description': '# images-upload-cli\n\n> Upload images via APIs\n\n[![PyPI version](https://img.shields.io/pypi/v/images-upload-cli)](https://pypi.org/project/images-upload-cli)\n[![AUR version](https://img.shields.io/aur/version/python-images-upload-cli)](https://aur.archlinux.org/packages/python-images-upload-cli)\n[![CI/CD](https://github.com/DeadNews/images-upload-cli/actions/workflows/python-app.yml/badge.svg)](https://github.com/DeadNews/images-upload-cli/actions/workflows/python-app.yml)\n[![pre-commit.ci](https://results.pre-commit.ci/badge/github/DeadNews/images-upload-cli/main.svg)](https://results.pre-commit.ci/latest/github/DeadNews/images-upload-cli/main)\n[![codecov](https://codecov.io/gh/DeadNews/images-upload-cli/branch/main/graph/badge.svg?token=OCZDZIYPMC)](https://codecov.io/gh/DeadNews/images-upload-cli)\n\n## Installation\n\nPyPI\n\n```sh\npip install images-upload-cli\n# or\npipx install images-upload-cli\n```\n\nAUR\n\n```sh\nyay -S python-images-upload-cli\n```\n\n## Hostings\n\n| host                                           | key required | return example                                       |\n| :--------------------------------------------- | :----------: | :--------------------------------------------------- |\n| [catbox](https://catbox.moe/)                  |      -       | `https://files.catbox.moe/{id}`                      |\n| [fastpic](https://fastpic.org/)                |      -       | `https://i120.fastpic.org/big/2022/0730/d9/{id}.png` |\n| [filecoffee](https://file.coffee/)             |      -       | `https://file.coffee/u/{id}.png`                     |\n| [freeimage](https://freeimage.host/)           |      -       | `https://iili.io/{id}.png`                           |\n| [geekpic](https://geekpic.net/)                |      -       | `https://s01.geekpic.net/{id}.png`                   |\n| [gyazo](https://gyazo.com/)                    |      +       | `https://i.gyazo.com/{id}.png`                       |\n| [imageban](https://imageban.ru/)               |      +       | `https://i2.imageban.ru/out/2022/07/30/{id}.png`     |\n| [imgbb](https://imgbb.com/)                    |      +       | `https://i.ibb.co/{id}/image.png`                    |\n| [imgchest](https://imgchest.com/)              |      +       | `https://cdn.imgchest.com/files/{id}.png`            |\n| [imgur](https://imgur.com/)                    |      -       | `https://i.imgur.com/{id}.png`                       |\n| [pictshare](https://pictshare.net/)            |      -       | `https://pictshare.net/{id}.png`                     |\n| [pixeldrain](https://pixeldrain.com/)          |      -       | `https://pixeldrain.com/api/file/{id}`               |\n| [pixhost](https://pixhost.to/)                 |      -       | `https://img75.pixhost.to/images/69/{id}_img.png`    |\n| [ptpimg](https://ptpimg.me/)                   |      +       | `https://ptpimg.me/{id}.png`                         |\n| [screenshotting](https://screenshotting.site/) |      -       | `https://screenshotting.site/i/{id}.png`             |\n| [smms](https://sm.ms/)                         |      +       | `https://s2.loli.net/2022/07/30/{id}.png`            |\n| [sxcu](https://sxcu.net/)                      |      -       | `https://sxcu.net/{id}.png`                          |\n| [telegraph](https://telegra.ph/)               |      -       | `https://telegra.ph/file/{id}.png`                   |\n| [up2sha](https://up2sha.re/)                   |      +       | `https://up2sha.re/media/raw/{id}.png`               |\n| [uplio](https://upl.io/)                       |      +       | `https://upl.io/i/{id}.png`                          |\n| [uploadcare](https://uploadcare.com/)          |      +       | `https://ucarecdn.com/{id}/img.png`                  |\n\n## Usage\n\n```sh\nUsage: images-upload-cli [OPTIONS] IMAGES...\n\n  Upload images via APIs.\n\nOptions:\n  -h, --hosting [catbox|fastpic|filecoffee|freeimage|geekpic|gyazo|imageban|imgbb|imgchest|imgur|pictshare|pixeldrain|pixhost|ptpimg|screenshotting|smms|sxcu|telegraph|up2sha|uplio|uploadcare]\n                                  [default: imgur]\n  -b, --bbcode                    Add bbcode tags.\n  -t, --thumbnail                 Add thumbnails and bbcode tags.\n  -c, --clipboard / -C, --no-clipboard\n                                  Copy result to clipboard.  [default: c]\n  --version                       Show the version and exit.\n  --help                          Show this message and exit.\n```\n\n## Env variables\n\n```ini\nCAPTION_FONT= # The default font is system dependent.\n\nBEEIMG_KEY=\nFREEIMAGE_KEY=\nGYAZO_TOKEN=\nIMAGEBAN_TOKEN=\nIMGBB_KEY=\nIMGCHEST_KEY=\nIMGUR_CLIENT_ID=\nPTPIMG_KEY=\nSMMS_KEY=\nUP2SHA_KEY=\nUPLIO_KEY=\nUPLOADCARE_KEY=\n```\n\nYou can set these in environment variables, or in `.env` file:\n\n- Unix: `~/.config/images-upload-cli/.env`\n- MacOS: `~/Library/Application Support/images-upload-cli/.env`\n- Windows: `C:\\Users\\<user>\\AppData\\Roaming\\images-upload-cli\\.env`\n',
    'author': 'DeadNews',
    'author_email': 'uhjnnn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DeadNews/images-upload-cli',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
