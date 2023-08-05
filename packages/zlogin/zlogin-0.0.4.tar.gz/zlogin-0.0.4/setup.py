# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zlogin']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.24.39,<2.0.0',
 'kiteconnect>=4.1.0,<5.0.0',
 'selenium>=4.3.0,<5.0.0',
 'undetected-chromedriver>=3.1.5,<4.0.0']

setup_kwargs = {
    'name': 'zlogin',
    'version': '0.0.4',
    'description': 'Zerodha Login Automation - Selenium Based',
    'long_description': '# Zerodha Login Automated - Selenium Based; Supported by Lambda function that processes the redirect rul and stores accessk key to DynamoDB\n\n## Context\nThis code is for a python package for automated login to Zerodha. The redirect URL is not handled here - Separate Repo with a container that runs as a lambda function saves the access token to dynamoDB\n\n## How to productionalize\n- Get Zerodha (kite.trade) account for API based access to the platform.\n- Create a \'.zerodha\' file in your home directory (Sample provided - check .zerodha.sample file)\n    - Needed Variables in File are Zerodha API keys/secret and login credentials (Userid, Password, PIN)\n    - One additional variable defined - ZAPI_AUTH: This can be any string that you choose. This string gets added as a query parameter in Zerodha reddirect response. The redirect response handler can test this \'api_auth\' query parameter to ensure the response is from zerodha and is in response to call from this package\n\n    The url for logging in being used is - f\'https://kite.trade/connect/login?v=3&api_key={api_key}&redirect_params={quote_plus(f"api_auth={api_auth}")}\' which sends the ZAPI_AUTH parameter as redirect query parameter \'api_auth\'\n- Set up a dynamodb table "save_access" with partition key as \'date\' (string variable) and sort key as \'datetime\' (also a string)\n- Check out the zerodha-dynamodb-save-accesstoken repository to set up a lambda function to handle Zerodha redirect url (it saves the access token in the save_access table in dynamodb)\n- Install zlogin package from pypi, "pip install zlogin"\n\n```python\nimport zlogin\naccess_token = zlogin.fetch_access_token()\n```\n\n    When logging in - send this as a redirect parameter \'api_auth\'. For this, your Zerodha login URL will be\n    f\'https://kite.trade/connect/login?v=3&api_key={api_key}&redirect_params={quote_plus(f"api_auth={api_auth}")}\'\n\n## This repo is a sister repo with zerodha-dynamodb-save-accesstoken tool which has a container code for lambda function that handles storage of access token to dynamodb; \nThat tool creates the redirect to the API gateway. For both to work properly, please use the same  ZAPI_AUTH environment variable value in both places\n',
    'author': 'Prabhat Rastogi',
    'author_email': 'prabhatrastogik@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/prabhatrastogik/zlogin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
