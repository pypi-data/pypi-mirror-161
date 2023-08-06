# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['__init__']
install_requires = \
['disnake>=2.0,<3.0']

setup_kwargs = {
    'name': 'disnake-ext-formatter',
    'version': '0.1.0a1',
    'description': 'A simple string.Formatter for disnake types',
    'long_description': '# disnake.ext.formatter\n\n`disnake.ext.formatter` is a module with a single class: a [`string.Formatter`](https://docs.python.org/3/library/string.html#string.Formatter \'(in python v3.10)\') subclass.\n\nThis class, aptly named `DisnakeFormatter`, has special handling for disnake objects, in order to hide attributes that shouldn\'t be otherwise exposed.\n\n\n> This project is currently in an **alpha** state and should **not** be used in production code without understanding the risks.\n\n### Why is this needed?\n\nWith simple string format, user provided strings can easily give away your token if they know the attributes. There are some ways to get around these, but rely on hacks and validating the strings ahead of time, or scanning the output for known secrets, but this cannot catch all cases.\n\nFor example, the code below would reveal the bot token to the user.\n\n```python\nUSER_PROVIDED_STRING = "Welcome to {guild.name}, {member!s}! Also this bot\'s token is {member._state.http.token}!"\n\n\n@client.event\nasync def on_member_join(member: disnake.Member):\n    # process getting the guild and other config\n    result = USER_PROVIDED_STRING.format(member=member)\n    await member.send(result)\n```\n\n> This example has been shortened for brevity. The typical usecase would be when there a configurable bot message that a user can change the content, and has access to a user/channel/guild/role object.\n\nHowever, we require that none of the attributes that are attempted to access are private attributes, which mean this attack is not possible when using the  `DisnakeFormatter` class correctly.\n\nFuture plans include having a hardcoded list of attributes which can be accessed on objects, the option to set that list to a desired mapping, and limiting attributes to specific types, to name but a few.\n\n### Examples\n\nBecause `DisnakeFormatter` is a subclass of [`string.Formatter`](https://docs.python.org/3/library/string.html#string.Formatter \'(in python v3.10)\'), the behaviour is the same. However, this is *not* the same as using [`str.format`](https://docs.python.org/3/library/stdtypes.html#str.format \'(in python v3.10)\').\nTo use `DisnakeFormatter`, an instance of the class is required, of which there are no special arguments. From there, all that is necessary to do is use the `format` method, which follows the same behavior as [`string.Formatter.format()`](https://docs.python.org/3/library/string.html#string.Formatter.format \'(in python v3.10)\').\n\n```python\nfrom disnake.ext.formatter import DisnakeFormatter\n\nUSER_PROVIDED_STRING = "Welcome to {guild.name}, {member!s}! Also this bot\'s token is {member._state.http.token}!"\n\n\n@client.event\nasync def on_member_join(member: disnake.Member):\n    # process getting the guild and other config\n    formatter = DisnakeFormatter()\n    result = formatter.format(USER_PROVIDED_STRING, member=member)\n    await member.send(result)\n```\n\nInstead of exposing the token, this will helpfully raise an error mentioning the attribute cannot be accessed on `member`.\n\n#### Suppressing Errors\n\nIf desired, `BlockedAttributeError` errors can be suppressed without exposing the attribute. This can be done with the `suppress_blocked_errors` parameter to `DisnakeFormatter`.\nWhen enabled, rather than raising an error the formatter will not replace that specific attribute.\n\n```python\nfrom disnake.ext.formatter import DisnakeFormatter\n\nUSER_PROVIDED_STRING = "Welcome to {guild.name}, {member!s}! Also this bot\'s token is {member._state.http.token}!"\n\n\n@client.event\nasync def on_member_join(member: disnake.Member):\n    # process getting the guild and other config\n    formatter = DisnakeFormatter(suppress_blocked_errors=True)\n    result = formatter.format(USER_PROVIDED_STRING, member=member)\n    await member.send(result)\n    # this sent the following message:\n    # Welcome to disnake, Charlie#0000! Also this bot\'s token is {member._state.http.token}!\n```\n\n----\n\n<br>\n<p align="center">\n    <a href="https://docs.disnake.dev/">Documentation</a>\n    ⁕\n    <a href="https://guide.disnake.dev/">Guide</a>\n    ⁕\n    <a href="https://discord.gg/disnake">Discord Server</a>\n\n</p>\n<br>\n',
    'author': 'onerandomusername',
    'author_email': 'genericusername414@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
