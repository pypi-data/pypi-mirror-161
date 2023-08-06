# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['signald']

package_data = \
{'': ['*']}

install_requires = \
['Deprecated>=1.2.11,<2.0.0', 'attrs>=21.2,<22.0']

setup_kwargs = {
    'name': 'pysignald',
    'version': '0.1.0',
    'description': 'A library that allows communication via the Signal IM service using the signald daemon.',
    'long_description': 'pysignald\n=======\n\n[![PyPI](https://img.shields.io/pypi/v/pysignald.svg)](https://pypi.org/project/pysignald/)\n[![pipeline status](https://gitlab.com/stavros/pysignald/badges/master/pipeline.svg)](https://gitlab.com/stavros/pysignald/commits/master)\n\npysignald is a Python client for the excellent [signald](https://signald.org/) project, which in turn\nis a command-line client for the Signal messaging service.\n\npysignald allows you to programmatically send and receive messages to Signal.\n\nNOTE: Unfortunately, this library might be somewhat out of date or parts of it might not be working, as the upstream API\nkeeps changing, breaking compatibility. If you notice any breakage, MRs to fix it would be appreciated.\n\n\nInstallation\n------------\n\nYou can install pysignald with pip:\n\n```\n$ pip install pysignald\n```\n\n\nRunning\n-------\n\nJust make sure you have signald installed. Here\'s an example of how to use pysignald:\n\n\n```python\nfrom signald import Signal, Reaction\n\ns = Signal("+1234567890")\n\n# If you haven\'t registered/verified signald, do that first:\ns.register(voice=False)\ns.verify("sms code")\n\n# If you want to set your display name, mobilecoin payments address (if using payments), or avatar, you can call set_profile:\ns.set_profile(\n    display_name="My user name",\n    mobilecoin_address="...", # Base64-encoded PublicAddress, see https://github.com/mobilecoinfoundation/mobilecoin/blob/master/api/proto/external.proto\n    avatar_filename="/signald-data/avatar.png", # Must be accessible by signald\n)\n\ns.send(recipient="+1098765432", text="Hello there!")\ns.send(recipient_group_id="YXNkZkFTREZhc2RmQVNERg==", text="Hello group!")\n\n# Get the profile information of someone\nprofile_info = s.get_profile(recipient="+1098765432")\nprint(profile_info)\n\nfor message in s.receive_messages():\n    print(message)\n    s.react(message.source, Reaction("🥳", message.source, message.timestamp))\n\n    # Send a read receipt notification which shows the message read checkmark on the receipient side\n    s.send_read_receipt(recipient=message.source["number"], timestamps=[message.timestamp])\n```\n\nYou can also use the chat decorator interface:\n\n```python\nfrom signald import Signal\n\ns = Signal("+1234567890")\n\n@s.chat_handler("hello there", order=10)  # This is case-insensitive.\ndef hello_there(message, match):\n    # Returning `False` as the first argument will cause matching to continue\n    # after this handler runs.\n    stop = False\n    reply = "Hello there!"\n    return stop, reply\n\n\n# Matching is case-insensitive. The `order` argument signifies when\n# the handler will try to match (default is 100), and functions get sorted\n# by order of declaration secondly.\n@s.chat_handler("hello", order=10)\ndef hello(message, match):\n    # This will match on "hello there" as well because of the "stop" return code in\n    # the function above. Both replies will be sent.\n    return "Hello!"\n\n\n@s.chat_handler("wave", order=20)\ndef react_with_waving_hand(message, match):\n    # This will only react to the received message.\n    # But it would be possible to send a reply and a reaction at the same time.\n    stop = True\n    reply = None\n    reaction = "👋"\n    return stop, reply, reaction\n\n\n@s.chat_handler(re.compile("my name is (.*)"))  # This is case-sensitive.\ndef name(message, match):\n    return "Hello %s." % match.group(1)\n\n\n@s.chat_handler("")\ndef catch_all(message, match):\n    # This will only be sent if nothing else matches, because matching\n    # stops by default on the first function that matches.\n    return "I don\'t know what you said."\n\ns.run_chat()\n```\n\n### Identity handling:\n\n```python\nfrom signald import Signal\nfrom signald.types import TrustLevel\n\ns = Signal("+1234567890")\n\n# Revoke trust for all identities of a given number\nfor identity in s.get_identities("+1234001100"):\n    s.trust(\n        "+1234001100",\n        identity.safety_number,\n        TrustLevel.UNTRUSTED,\n    )\n\n# Generate QR code data for identity validation\nids = s.get_identities("+1234001177")\nids.sort(key=lambda x: x.added, reverse=True)\n# prints base64 encoded validation code of the latest identity of the given number\nprint(ids[0].qr_code_data)\n```\nYou can pipe the content of `ids[0].qr_code_data`  to `| base64 -D | qrencode -t ansi` to validate the identity via the Singal app QR scanner.\n\n\n### Group information:\n```python\nfrom signald import Signal\n\ns = Signal("+1234567890")\n\n# list all groups and members\nfor group in s.list_groups():\n    print(group.title)\n    for member in group.members:\n        print(member.get("uuid"))\n```\n\nVarious\n-------\n\npysignald also supports different socket paths:\n\n```python\ns = Signal("+1234567890", socket_path="/var/some/other/socket.sock")\n```\n\nIt supports TCP sockets too, if you run a proxy. For example, you can proxy signald\'s UNIX socket over TCP with socat:\n\n```bash\n$ socat -d -d TCP4-LISTEN:15432,fork UNIX-CONNECT:/var/run/signald/signald.sock\n```\n\nThen in pysignald:\n\n```python\ns = Signal("+1234567890", socket_path=("your.serveri.ip", 15432))\n```\n',
    'author': 'Stavros Korokithakis',
    'author_email': 'hi@stavros.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/stavros/pysignald/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
