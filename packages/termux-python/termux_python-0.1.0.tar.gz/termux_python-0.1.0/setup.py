# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['termux', 'termux.common']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'termux-python',
    'version': '0.1.0',
    'description': 'termux python bindings',
    'long_description': '# termux_python\n\n`termux_python` provides python bindings for https://wiki.termux.com/wiki/Termux:API\nand other termux scripts.\n\n## Install\n\nThis package is available via pip:\n```\npip install termux-python\n```\n\nFor development purposes, use [poetry](https://python-poetry.org/):\n```bash\ngit clone https://github.com/mlvl42/termux_python\ncd termux_python\npoetry install\n```\n\n## Example\n\nThe following example shows how some bindings could be used in a python script. Check [the list of supported\nAPIs](https://github.com/mlvl42/termux_python/blob/master/termux/termux.py) as well\nas the content of [the original termux-api scripts](https://github.com/termux/termux-api-package/tree/master/scripts)\nto understand how to use the bindings.\n\n```python\nimport termux\nimport textwrap\n\n# retrieve various device infos\nprint(termux.wifi_connectioninfo())\nprint(termux.camera_info())\nprint(termux.telephony_deviceinfo())\n\n# pretty print last 100 sms\nmessages = termux.sms_list(limit=100)\n\nfor m in messages:\n    if \'sender\' in m:\n        print(f"{m[\'sender\']}:")\n    else:\n        print(f"{m[\'number\']}:")\n    wrap = textwrap.TextWrapper(initial_indent=\'\\t\', subsequent_indent=\'\\t\')\n    body = wrap.fill(m["body"])\n    print(body)\n\n# send a message\ntermux.sms_send("sending an sms from python", "+01020304050")\n\n# perform an action if the fingerprint matches\nret = termux.fingerprint(title="Restricted action", desc="Analyze your fingerprint")\nif ret[\'auth_result\'] == \'AUTH_RESULT_SUCCESS\':\n    print("Access granted")\nelse:\n    print("Access denied")\n\n# text to speech\ntermux.tts_speak("job\'s done !")\n```\n',
    'author': 'mlvl42',
    'author_email': 'melvil.guillaume@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mlvl42/termux_python',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
