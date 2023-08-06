# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbt_dry_run',
 'dbt_dry_run.models',
 'dbt_dry_run.node_runner',
 'dbt_dry_run.sql_runner',
 'dbt_dry_run.test',
 'dbt_dry_run.test.models',
 'dbt_dry_run.test.node_runner',
 'dbt_dry_run.test.sql_runner']

package_data = \
{'': ['*']}

install_requires = \
['agate>=1.6,<2.0',
 'google-cloud-bigquery>=2,<3',
 'networkx>=2.6,<3.0',
 'pydantic>=1.9.0,<2.0.0',
 'pyyaml>=6,<7',
 'tenacity>=8.0.1,<9.0.0']

entry_points = \
{'console_scripts': ['dbt-dry-run = dbt_dry_run.__main__:main']}

setup_kwargs = {
    'name': 'dbt-dry-run',
    'version': '0.3.1',
    'description': 'Dry run dbt projects',
    'long_description': '# dbt-dry-run\n\n[dbt][dbt-home] is a tool that helps manage data transformations using templated SQL queries. These SQL queries are \nexecuted against a target data warehouse. It doesn\'t check the validity of SQL queries before it executes your project.\nThis dry runner uses BigQuery\'s [dry run][bq-dry-run] capability to allow you to check that SQL queries are valid before\ntrying to execute them.\n\nSee the [blog post][blog-post] for more information on how the dry runner works.\n\n![Terminal Recording of failing dry run](./terminal-demo.gif)\n\n## Quickstart\n\n### Installation\n\nThe dry runner can be installed via pip:\n\n`\npip install dbt-dry-run\n`\n\n### Running\n\nThe dry runner has a single command called `dbt-dry-run` in order for it to run you must \nfirst compile a dbt manifest using `dbt compile` as you normally would.\n\nThen on the same machine (So that the dry runner has access to your dbt project source and the \n`manifest.yml`) you can run the dry-runner with:\n\n```\ndbt-dry-run <PROFILE>\n```\n\nWhere `PROFILE` should match the profile specified in your `dbt_project.yml`:\n\n```\n# This setting configures which "profile" dbt uses for this project.\n# This will get overridden by the root project\nprofile: \'default\'\n```\n\nLike dbt it will search for `profiles.yml` in `~/.dbt/` and use the default target specified.\nIt will also look for the `manifest.yml` in the current working directory. \nJust like in the dbt CLI you can override these defaults:\n\n```\ndbt-dry-run default --profiles-dir /my_org_dbt/profiles/ --target local --manifest-path target/manifest.json\n```\n\n## Reporting Results & Failures\n\nIf the result is successful it will output the number of \nmodels that were tested like so:\n\n```\nDry running 3 models\n\nDRY RUN SUCCESS!\n```\n\nThe process will also return exit code 0\n\nIf there are failures it will print a summary table of the nodes that failed:\n\n```\nDry running 3 models\nNode model.test_models_with_invalid_sql.second_layer failed with exception:\n400 POST https://bigquery.googleapis.com/...: Column d in USING clause not found on left side of join at [6:88]\n\n(job ID: 5e336f32-273d-480a-b8bb-cdf4fca66a98)\n\nTotal 1 failures:\n1       :       model.test_models_with_invalid_sql.second_layer :       BadRequest      :       ERROR\nDRY RUN FAILURE!`\n```\n\nThe process will also return exit code 1\n\n### Report Artefact\n\nIf you specify `---report-path` a JSON file will be outputted regardless of dry run success/failure with detailed \ninformation of each node\'s predicted schema or error message if it has failed:\n\n```json\n{\n  "success": false,\n  "node_count": 3,\n  "failure_count": 1,\n  "failed_node_ids": [\n    "model.test_models_with_invalid_sql.second_layer"\n  ],\n  "nodes": [\n    {\n      "unique_id": "seed.test_models_with_invalid_sql.my_seed",\n      "success": true,\n      "error_message": null,\n      "table": {\n        "fields": [\n...\n        ]\n      }\n    },\n    {\n      "unique_id": "model.test_models_with_invalid_sql.first_layer",\n      "success": true,\n      "error_message": null,\n      "table": {\n        "fields": [\n...\n        ]\n      }\n    },\n    {\n      "unique_id": "model.test_models_with_invalid_sql.second_layer",\n      "success": false,\n      "error_message": "BadRequest",\n      "table": null\n    }\n  ]\n}\n```\n\n## Contributing/Running locally\n\nTo setup a dev environment you need [poetry][get-poetry], first run `poetry install` to install all dependencies. Then\nthe `Makefile` contains all the commands needed to run the test suite and linting.\n\n- verify: Formats code with `black`, type checks with `mypy` and then runs the unit tests with coverage.\n- run-local: Runs one of the integration tests locally. _Requires BigQuery Instance_ (See Integration Tests)\n- integration: Runs the integration tests against BigQuery (See Integration Tests)\n\n### Running Integration Tests\n\nIn order to run integration tests locally you will need access to a BigQuery project/instance in which your gcloud application \ndefault credentials has the role `Big Query Data Owner`. The BigQuery instance should have an empty dataset called `dry_run`.\n\nSetting the environment variable `DBT_PROJECT=<YOUR GCP PROJECT HERE>` will tell the integration tests which GCP \nproject to run the test suite against. The test suite does not currently materialize any data into the project.\n\nThe integration tests will run on any push to `main` to ensure the package\'s core functionality is still in place.\n\n__Auto Trader employees can request authorisation to access the `at-dry-run-integration-dev` project for this purpose__\n\n## Capabilities and Limitations\n\n### Things this can catch\n\nThe dry run can catch anything the BigQuery planner can identify before the query has run. Which \nincludes:\n\n1. Typos in SQL keywords:  `selec` instead of `select`\n2. Typos in columns names: `orders.produts` instead of `orders.products`\n3. Problems with incompatible data types: Trying to execute "4" + 4\n4. Incompatible schema changes to models: Removing a column from a view that is referenced\nby a downstream model explicitly\n5. Incompatible schema changes to sources: Third party modifies schema of source tables without \nyour knowledge\n6. Permission errors: The dry runner should run under the same service account your production \njob runs under. This allows you to catch problems with table/project permissions as dry run queries\nneed table read permissions just like the real query\n7. Incorrect configuration of snapshots: For example a typo in the `unique_key` config. Or `check_cols` which do not \nexist in the snapshot\n   \n### Things this can\'t catch\n\nThere are certain cases where a syntactically valid query can fail due to the data in \nthe tables:\n\n1. Queries that run but do not return intended/correct result. This is checked using [tests][dbt-tests]\n2. `NULL` values in `ARRAY_AGG` (See [IGNORE_NULLS bullet point][bq-ignore-nulls])\n3. Bad query performance that makes it too complex/expensive to run\n\n### Things still to do...\n\nImplementing the dry runner required re-implementing some areas of dbt. Mainly how the \nadapter sets up connections and credentials with the BigQuery client, we have only \nimplemented the methods of how we connect to our warehouse so if you don\'t use OAUTH or \nservice account JSON files then this won\'t be able to read `profiles.yml` correctly.\n\nThe implementation of seeds is incomplete as well as we don\'t use them very much in our \nown dbt projects. The dry runner will just use the datatypes that `agate` infers from the CSV \nfiles.\n\n[dbt-home]: https://www.getdbt.com/\n[bq-dry-run]: https://cloud.google.com/bigquery/docs/dry-run-queries\n[dbt-tests]: https://docs.getdbt.com/docs/building-a-dbt-project/tests\n[bq-ignore-nulls]: https://cloud.google.com/bigquery/docs/reference/standard-sql/aggregate_functions#array_agg\n[blog-post]: https://engineering.autotrader.co.uk/2022/04/06/dry-running-our-data-warehouse-using-bigquery-and-dbt.html\n[get-poetry]: https://python-poetry.org/\n\n## License\n\nCopyright 2022 Auto Trader Limited\n\nLicensed under the Apache License, Version 2.0 (the "License");\nyou may not use this file except in compliance with the License.\nYou may obtain a copy of the License at\n\n   http://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n',
    'author': 'Connor Charles',
    'author_email': 'connor.charles@autotrader.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/autotraderuk/dbt-dry-run',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
