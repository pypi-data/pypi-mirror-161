# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'generated'}

packages = \
['generated',
 'generated.openapi_client',
 'generated.openapi_client.api',
 'generated.openapi_client.apis',
 'generated.openapi_client.model',
 'generated.openapi_client.models',
 'generated.test',
 'groundlight']

package_data = \
{'': ['*'], 'generated': ['.openapi-generator/*', 'docs/*']}

install_requires = \
['certifi>=2021.10.8,<2022.0.0',
 'frozendict>=2.3.2,<3.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'urllib3>=1.26.9,<2.0.0']

setup_kwargs = {
    'name': 'groundlight',
    'version': '0.4.0',
    'description': 'Call the Groundlight API from python',
    'long_description': '# User Guide\n\n`groundlight` is a python SDK for working with the Groundlight API. You can send image queries and receive predictions powered by a mixture of machine learning models and human labelers in-the-loop.\n\n*Note: The SDK is currently in "alpha" phase.*\n\n## Pre-reqs\n\n1. Install the `groundlight` sdk.\n\n    ```Bash\n    $ pip install groundlight\n    ```\n\n1. To access the API, you need an API token. You can create one on the\n   [groundlight website](https://app.groundlight.ai/reef/my-account/api-tokens).\n\n1. Use the `Groundlight` client!\n\n    ```Python\n    from groundlight import Groundlight\n    gl = Groundlight(api_token="<YOUR_API_TOKEN>")\n    ```\n\n    The API token should be stored securely - do not commit it to version control! Alternatively, you can use the token by setting the `GROUNDLIGHT_API_TOKEN` environment variable.\n\n## Basics\n\n#### Create a new detector\n\n```Python\ndetector = gl.create_detector(name="Dog", query="Is it a dog?")\n```\n\n#### Retrieve a detector\n\n```Python\ndetector = gl.get_detector(id="YOUR_DETECTOR_ID")\n```\n\n#### List your detectors\n\n```Python\n# Defaults to 10 results per page\ndetectors = gl.list_detectors()\n\n# Pagination: 3rd page of 25 results per page\ndetectors = gl.list_detectors(page=3, page_size=25)\n```\n\n#### Submit an image query\n\n```Python\nimage_query = gl.submit_image_query(detector_id="YOUR_DETECTOR_ID", image="path/to/filename.jpeg")\n```\n\n#### Retrieve an image query\n\nIn practice, you may want to check for a new result on your query. For example, after a cloud reviewer labels your query. For example, you can use the `image_query.id` after the above `submit_image_query()` call.\n\n```Python\nimage_query = gl.get_image_query(id="YOUR_IMAGE_QUERY_ID")\n```\n\n#### List your previous image queries\n\n```Python\n# Defaults to 10 results per page\nimage_queries = gl.list_image_queries()\n\n# Pagination: 3rd page of 25 results per page\nimage_queries = gl.list_image_queries(page=3, page_size=25)\n```\n\n## Advanced\n\n### Handling HTTP errors\n\nIf there is an HTTP error during an API call, it will raise an `ApiException`. You can access different metadata from that exception:\n\n```Python\nfrom groundlight import ApiException, Groundlight\n\ngl = Groundlight()\ntry:\n    detectors = gl.list_detectors()\nexcept ApiException as e:\n    print(e)\n    print(e.args)\n    print(e.body)\n    print(e.headers)\n    print(e.reason)\n    print(e.status)\n```\n',
    'author': 'Groundlight AI',
    'author_email': 'support@groundlight.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://groundlight.ai',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
