# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wxc_sdk',
 'wxc_sdk.common',
 'wxc_sdk.groups',
 'wxc_sdk.integration',
 'wxc_sdk.licenses',
 'wxc_sdk.locations',
 'wxc_sdk.people',
 'wxc_sdk.person_settings',
 'wxc_sdk.telephony',
 'wxc_sdk.telephony.callqueue',
 'wxc_sdk.telephony.location',
 'wxc_sdk.telephony.prem_pstn',
 'wxc_sdk.webhook',
 'wxc_sdk.workspace_settings',
 'wxc_sdk.workspaces']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'backoff>=2.0.1,<3.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'pytz',
 'requests-toolbelt>=0.9.1,<0.10.0',
 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'wxc-sdk',
    'version': '1.5.2',
    'description': 'SDK for Webex APIs with special focus on Webex Calling specific endpoints',
    'long_description': "=======\nwxc_sdk\n=======\n\nA simple SDK to work with `Webex APIs <https://developer.webex.com>`_, special focus on Webex Calling specific API\nendpoints.\n\n----------------------------------------------\n\nThis is how easy it is to use the SDK. The example code list all calling enabled users within the org.\n\n.. code-block:: Python\n\n    from wxc_sdk import WebexSimpleApi\n\n    api = WebexSimpleApi()\n\n    # if a user is enabled for calling, then the location_id attribute is set\n    calling_users = [user for user in api.people.list(calling_data=True)\n                     if user.location_id]\n    print(f'{len(calling_users)} users:')\n    print('\\n'.join(user.display_name for user in calling_users))\n\n\nInstallation\n------------\n\nInstalling and upgrading wxc_sdk is easy:\n\n**Install via PIP**\n\n.. code-block:: bash\n\n    $ pip install wxc-sdk\n\n**Upgrade to the latest version**\n\n.. code-block:: bash\n\n    $ pip install wxc-sdk --upgrade\n\nDocumentation\n-------------\n\nDocumentation is available at:\nhttp://wxc_sdk.readthedocs.io\n\nExamples\n--------\n\nSample scripts are available in the examples_ folder.\n\n.. _examples: https://github.com/jeokrohn/wxc_sdk/tree/master/examples\n\n\n",
    'author': 'Johannes Krohn',
    'author_email': 'jkrohn@cisco.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jeokrohn/wxc_sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
