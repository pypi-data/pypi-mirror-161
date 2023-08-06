# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['arangodantic', 'arangodantic.tests']

package_data = \
{'': ['*']}

install_requires = \
['aioarangodb>=0.1.2,<0.2.0',
 'inflection>=0.5.1,<0.6.0',
 'pydantic>=1.9.1,<2.0.0']

extras_require = \
{'shylock': ['shylock[aioarangodb]>=1.1.1,<2.0.0']}

setup_kwargs = {
    'name': 'arangodantic',
    'version': '0.3.0',
    'description': 'Database models for ArangoDB using Pydantic base models.',
    'long_description': '# Arangodantic\n\n[![Build Status](https://travis-ci.com/ioxiocom/arangodantic.svg?branch=main)](https://travis-ci.com/ioxiocom/arangodantic)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![PyPI](https://img.shields.io/pypi/v/arangodantic)](https://pypi.org/project/arangodantic/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/arangodantic)](https://pypi.org/project/arangodantic/)\n[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)\n\nDatabase models for ArangoDB using Pydantic base models.\n\n## Installation\n\nThe package is available on PyPI:\n\n```bash\npip install arangodantic\n\n# Or with Shylock\npip install arangodantic[shylock]\n```\n\n## Usage\n\nDefine your database models by extending either `DocumentModel` or `EdgeModel`. Nested\nstructures can be created by extending pydantic.BaseModel.\n\nConfigure Arangodantic. You can optionally define a collection name prefix, a key\ngeneration function and a lock (needed if you want to use the locking functionality;\n[Shylock](https://github.com/lietu/shylock) is supported out of the box, any other\nlocking service such as [Sherlock](https://pypi.org/project/sherlock/) should at least\nin theory also work).\n\nEnsure you have an ArangoDB server available with known credentials\n\n```bash\ndocker run --rm -p 8529:8529 -e ARANGO_ROOT_PASSWORD="" arangodb/arangodb:3.7.2.1\n```\n\n```python\nimport asyncio\nfrom uuid import uuid4\n\nfrom aioarangodb import ArangoClient\nfrom pydantic import BaseModel\nfrom shylock import AsyncLock as Lock\nfrom shylock import ShylockAioArangoDBBackend\nfrom shylock import configure as configure_shylock\n\nfrom arangodantic import ASCENDING, DocumentModel, EdgeModel, configure\n\n\n# Define models\nclass Owner(BaseModel):\n    """Dummy owner Pydantic model."""\n\n    first_name: str\n    last_name: str\n\n\nclass Company(DocumentModel):\n    """Dummy company Arangodantic model."""\n\n    company_id: str\n    owner: Owner\n\n\nclass Link(EdgeModel):\n    """Dummy Link Arangodantic model."""\n\n    type: str\n\n\nasync def main():\n    # Configure the database settings\n    hosts = "http://localhost:8529"\n    username = "root"\n    password = ""\n    database = "example"\n    prefix = "example-"\n\n    client = ArangoClient(hosts=hosts)\n    # Connect to "_system" database and create the actual database if it doesn\'t exist\n    # Only for demo, you likely want to create the database in advance.\n    sys_db = await client.db("_system", username=username, password=password)\n    if not await sys_db.has_database(database):\n        await sys_db.create_database(database)\n\n    # Configure Arangodantic and Shylock\n    db = await client.db(database, username=username, password=password)\n    configure_shylock(await ShylockAioArangoDBBackend.create(db, f"{prefix}shylock"))\n    configure(db, prefix=prefix, key_gen=uuid4, lock=Lock)\n\n    # Create collections if they don\'t yet exist\n    # Only for demo, you likely want to create the collections in advance.\n    await Company.ensure_collection()\n    await Link.ensure_collection()\n\n    # Let\'s create some example entries\n    owner = Owner(first_name="John", last_name="Doe")\n    company = Company(company_id="1234567-8", owner=owner)\n    await company.save()\n    print(f"Company saved with key: {company.key_}")\n\n    second_owner = Owner(first_name="Jane", last_name="Doe")\n    second_company = Company(company_id="2345678-9", owner=second_owner)\n    await second_company.save()\n    print(f"Second company saved with key: {second_company.key_}")\n\n    link = Link(_from=company, _to=second_company, type="CustomerOf")\n    await link.save()\n    print(f"Link saved with key: {link.key_}")\n\n    # Hold named locks while loading and doing changes\n    async with Company.lock_and_load(company.key_) as c:\n        assert c.owner == owner\n        c.owner.first_name = "Joanne"\n        await c.save()\n\n    await company.reload()\n    print(f"Updated owner of company to \'{company.owner!r}\'")\n\n    # Let\'s explore the find functionality\n    # Note: You likely want to add indexes to support the queries\n    print("Finding companies owned by a person with last name \'Doe\'")\n    async with (await Company.find({"owner.last_name": "Doe"}, count=True)) as cursor:\n        print(f"Found {len(cursor)} companies")\n        async for found_company in cursor:\n            print(f"Company: {found_company.company_id}")\n\n    # Supported operators include: "==", "!=", "<", "<=", ">", ">="\n    found_company = await Company.find_one(\n        {"owner.last_name": "Doe", "_id": {"!=": company}}\n    )\n    print(f"Found the company {found_company.key_}")\n\n    # Find also supports sorting and the cursor can easily be converted to a list\n    companies = await (\n        await Company.find(\n            sort=[\n                ("owner.last_name", ASCENDING),\n                ("owner.first_name", ASCENDING),\n            ]\n        )\n    ).to_list()\n    print("Companies sorted by owner:")\n    for c in companies:\n        print(f"Company {c.company_id}, owner: {c.owner!r}")\n\n\nif __name__ == "__main__":\n    # Starting from Python 3.7 ->\n    # asyncio.run(main())\n\n    # Compatible with Python 3.6 ->\n    loop = asyncio.get_event_loop()\n    result = loop.run_until_complete(main())\n```\n\nYou might find [migrate-anything](https://github.com/cocreators-ee/migrate-anything)\nuseful for creating and managing collections and indexes.\n\n## More examples\n\n- The [graph example](examples/graph_example.py) shows how arangodantic can be used with\n  graphs. Please note that graph related functionality is at the moment really limited\n  and will likely be extended later and might even be restructured, so use with caution.\n\n## License\n\nThis code is released under the BSD 3-Clause license. Details in the\n[LICENSE](./LICENSE) file.\n',
    'author': 'Digital Living International Ltd',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ioxiocom/arangodantic',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
