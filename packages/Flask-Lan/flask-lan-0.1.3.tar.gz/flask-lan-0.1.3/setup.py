# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_lan']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.1.3,<3.0.0', 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'flask-lan',
    'version': '0.1.3',
    'description': 'Flask-Lan is a schema validator and swagger generator but more modernized',
    'long_description': '# Flask-Lan\n\n`Flask-Lan` is a schema validator and swagger generator but more modernized.\n\n!!! Warning\n\n    Currently, `flask-lan` is still under active development(before verion 1.0.0). Don\'t use it in production.\n\nIt\'s kind of like the famous library `FastAPI`, bringing part of brilliant features of `FastAPI` to your Flask application.\nFor example, it uses [Pydantic](https://github.com/samuelcolvin/pydantic) for Request/Response params validation and auto-generates `swagger` docs.\n\n## Feature\n\n-   Intuitive and easy to use.\n-   Use type hinting to validate request/response params.\n-   Auto-generate `swagger` docs.\n\n## Quick start\n\n```bash\npip install flask-lan\n```\n\nA simple example:\n\n```python\nfrom flask import Flask\nfrom pydantic import BaseModel\nfrom flask_lan import validator, docs\n\napp = Flask(__name__)\n\n\n@docs(tag="books", desc="Get books")\n@app.get("/books/<id>/")\n@validator\ndef home(id:int, q: str, star: float=10):\n    return {"id":id, "q": q, "star": star}\n\nif __name__ == "__main__":\n    app.run(debug=True)\n\n```\n\n## License\n\nThis project is licensed under the terms of the MIT license.\n',
    'author': 'chaojie',
    'author_email': 'zhuzhezhe95@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
