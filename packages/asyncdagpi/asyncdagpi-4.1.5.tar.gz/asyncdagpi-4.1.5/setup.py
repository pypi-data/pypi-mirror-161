# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asyncdagpi']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0']

setup_kwargs = {
    'name': 'asyncdagpi',
    'version': '4.1.5',
    'description': 'An Asynchronos API wrapper for https://dagpi.xyz',
    'long_description': '# asyncdagpi\n\n[![Build Status](https://travis-ci.com/Daggy1234/asyncdagpi.svg?branch=master)](https://travis-ci.com/Daggy1234/asyncdagpi) [![License](https://img.shields.io/github/license/daggy1234/asyncdagpi)](https://mit-license.org/) ![version](https://img.shields.io/pypi/v/asyncdagpi) [![python](https://img.shields.io/pypi/pyversions/asyncdagpi)](https://pypi.org/p/asyncdagpi) [![Documentation Status](https://readthedocs.org/projects/asyncdagpi/badge/?version=latest)](https://asyncdagpi.readthedocs.io/en/latest/?badge=latest) [![Codecov](https://img.shields.io/codecov/c/github/daggy1234/asyncdagpi?logo=codecov)](https://codecov.io/gh/daggy1234/asyncdagpi) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/ad36f1ea6211444792e84f32a14326dd)](https://www.codacy.com/gh/Daggy1234/asyncdagpi/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Daggy1234/asyncdagpi&amp;utm_campaign=Badge_Grade)\n\nPowerful Asynchronous Wrapper for dagpi [dagpi.xyz](https://dagpi.xyz)\n\n## Installation\n\n```shell script\npip install asyncdagpi\n```\n\n## Data API\n\nSome endpoints like WTP, PickupLine and Logo will return Objects while Waifu will return a Dictionary. Everything else will return a string.\n\n```python\nfrom asyncdagpi import Client\ndagpi = Client("dagpi token")\n# For WTP Object\nwtp = await dagpi.wtp()\n#For Roast\nroast = await dagpi.roast()\n```\n\n## Image Manipulation\n\nAll Image endpoints return an Image object. This has many properties that can be useful for developers. For Basic implementations are displayed\n\n### Discord.py\n\n```python\nfrom discord.ext import commands\nimport discord\nfrom asyncdagpi import Client, ImageFeatures\n\nbot = commands.Bot(command_prefix="!")\ndagpi = Client("dagpi token")\n\n@bot.command()\nasync def pixel(ctx, member: discord.Member):\n    url = str(member.display_avatar.with_format("png").with_size(1024))\n    img = await dagpi.image_process(ImageFeatures.pixel(), url)\n    file = discord.File(fp=img.image,filename=f"pixel.{img.format}")\n    await ctx.send(file=file)\n\n```\n\n### Pycord\n\n```python\nfrom discord.ext import commands\nimport discord\nfrom asyncdagpi import Client, ImageFeatures\n\nbot = discord.Bot()\ndagpi = Client("dagpi token")\n\n@bot.slash_command(guild_ids=[...])\nasync def pixel(\n    ctx, member: discord.Member = None\n):  # Passing a default value makes the argument optional\n    user = member or ctx.author\n    url = str(member.display_avatar.with_format("png").with_size(1024))\n    img = await dagpi.image_process(ImageFeatures.pixel(), url)\n    file = discord.File(fp=img.image,filename=f"pixel.{img.format}")\n\n\n```\n\n### Writing To File\n\n```python\nfrom asyncdagpi import Client, ImageFeatures\ndagpi = Client("dagpi token")\nimg = await dagpi.image_process(ImageFeatures.pixel(), "https://dagbot-is.the-be.st/logo.png")\n#it will auto chose the right format and write to current directory\nimg.write("pixel")\n#will create pixel.png in this case\n```\n\n### Python Pillow\n\n```python\nfrom asyncdagpi import ImageFeatures, Client\nfrom PIL import Image\n\ndagpi = Client("dagpi token")\nimg = await dagpi.image_process(ImageFeatures.pixel(), "https://dagbot-is.the-be.st/logo.png")\nim = Image.open(img.image)\n```\n\n### Kwargs Example\n\n```python\nfrom asyncdagpi import ImageFeatures, Client\n\ndagpi = Client("dagpi token")\nimg = await dagpi.image_process(ImageFeatures.tweet(), "https://dagbot-is.the-be.st/logo.png", text="This is asyncdagpi tweeting live from dagpi.xyz!", username="Asyncdagpi")\n```\n\n### For More Thorough Examples and Feature list read the documentation\n\n[Docs](https://asyncdagpi.rtfd.io)\n\n[Dagpi Docs](https://dagpi.docs.apiary.io)\n',
    'author': 'Daggy1234',
    'author_email': 'daggy@daggy.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Daggy1234/asyncdagpi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
