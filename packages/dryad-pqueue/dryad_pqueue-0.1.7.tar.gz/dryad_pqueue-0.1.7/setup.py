# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['pqueue', 'config']
install_requires = \
['psycopg[binary,pool]>=3.0.10,<4.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'dryad-pqueue',
    'version': '0.1.7',
    'description': 'run models with parameters from a queue and upload to s3 + webhooks',
    'long_description': 'inherit from Maestro and override `create_generator` and/or `handle_item`\n\nsecrets:\n- `DATABASE_URL`\n- `SUPABASE_API_KEY` \n\noptions:\n- `MODEL`\n- `SUPABASE_URL`\n- `ADMIN_URL`\n\nflags:\n- `FREE`\n- `EXIT`\n- `EXIT_ON_LOAD`\n- `POWEROFF`\n- `TWITTER`: post tweets, requires comma-seperated TWITTER_CREDS and TwitterAPI to be installed\n',
    'author': 'technillogue',
    'author_email': 'technillogue@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9',
}


setup(**setup_kwargs)
