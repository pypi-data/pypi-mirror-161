# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aladdin',
 'aladdin.data_source',
 'aladdin.feature_view',
 'aladdin.feature_view.tests',
 'aladdin.local',
 'aladdin.psql',
 'aladdin.redis',
 'aladdin.redshift',
 'aladdin.request',
 'aladdin.s3',
 'aladdin.tests']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'click>=8.1.3,<9.0.0',
 'dill>=0.3.4,<0.4.0',
 'mashumaro>=3.0.1,<4.0.0',
 'nest-asyncio>=1.5.5,<2.0.0',
 'pandas>=1.3.1,<2.0.0',
 'pyarrow>=8.0.0,<9.0.0']

extras_require = \
{'aws': ['aioaws>=0.12,<0.13', 'databases>=0.5.5,<0.6.0'],
 'dask': ['dask[dataframe]>=2022.7.0,<2023.0.0'],
 'psql': ['databases>=0.5.5,<0.6.0', 'asyncpg>=0.25.0,<0.26.0'],
 'redis': ['redis>=4.3.1,<5.0.0'],
 'server': ['fastapi>=0.77.1,<0.78.0',
            'uvicorn>=0.17.6,<0.18.0',
            'asgi-correlation-id>=3.0.0,<4.0.0']}

entry_points = \
{'console_scripts': ['aladdin = aladdin.cli:cli']}

setup_kwargs = {
    'name': 'aladdinml',
    'version': '0.0.17a0',
    'description': 'A scalable feature store that makes it easy to productionise and manage ML and AI projects',
    'long_description': '# Aladdin\n\nA feature store simplifying feature managment, serving and quality control.\nDescribe your features, and the feature store grants your wishes so you become the feature king.\n\n## Feature Views\n\nWrite features as the should be, as data models.\nThen get code completion and typesafety by referencing them in other features.\n\nThis makes the features light weight, data source indipendent, and flexible.\n\n```python\nclass Match(FeatureView):\n\n    metadata = FeatureViewMetadata(\n        name="match",\n        description="Features about football matches",\n        batch_source=...\n    )\n\n    # Raw data\n    home_team = Entity(dtype=String())\n    away_team = Entity(dtype=String())\n\n    date = EventTimestamp(max_join_with=timedelta(days=365))\n\n    half_time_score = String()\n    full_time_score = String().description("the scores at full time, in the format \'home-away\'. E.g: \'2-1\'")\n\n\n    # Transformed features\n    is_liverpool = (home_team == "Liverpool").description("If the home team is Liverpool")\n\n    score_as_array = full_time_score.split("-")\n\n    # Custom pandas df method, which get first and second index in `score_as_array`\n    home_team_score = score_as_array.transformed(lambda df: df["score_as_array"].str[0].replace({np.nan: 0}).astype(int))\n    away_team_score = score_as_array.transformed(...)\n\n    score_differance = home_team_score - away_team_score\n    total_score = home_team_score + away_team_score\n```\n\n## Data sources\n\nAladdin makes handling data sources easy, as you do not have to think about how it is done.\nOnly define where the data is, and we handle the dirty work.\n\n```python\nmy_db = PostgreSQLConfig(env_var="DATABASE_URL")\n\nclass Match(FeatureView):\n\n    metadata = FeatureViewMetadata(\n        name="match",\n        description="...",\n        batch_source=my_db.table(\n            "matches",\n            mapping_keys={\n                "Team 1": "home_team",\n                "Team 2": "away_team",\n            }\n        )\n    )\n\n    home_team = Entity(dtype=String())\n    away_team = Entity(dtype=String())\n```\n\n### Fast development\n\nMaking iterativ and fast exploration in ML is important. This is why Aladdin also makes it super easy to combine, and test multiple sources.\n\n```python\nmy_db = PostgreSQLConfig.localhost()\n\naws_bucket = AwsS3Config(...)\n\nclass SomeFeatures(FeatureView):\n\n    metadata = FeatureViewMetadata(\n        name="some_features",\n        description="...",\n        batch_source=my_db.table("local_features")\n    )\n\n    # Some features\n    ...\n\nclass AwsFeatures(FeatureView):\n\n    metadata = FeatureViewMetadata(\n        name="aws",\n        description="...",\n        batch_source=aws_bucket.file_at("path/to/file.parquet")\n    )\n\n    # Some features\n    ...\n```\n\n## Model Service\n\nUsually will you need to combine multiple features for each model.\nThis is where a `ModelService` comes in.\nHere can you define which features should be exposed.\n\n```python\n# Uses the variable name, as the model service name.\n# Can also define a custom name, if wanted.\nmatch_model = ModelService(\n    features=[\n        Match.select_all(),\n\n        # Select features with code completion\n        LocationFeatures.select(lambda view: [\n            view.distance_to_match,\n            view.duration_to_match\n        ]),\n    ]\n)\n```\n\n\n## Data Enrichers\n\nIn manny cases will extra data be needed in order to generate some features.\nWe therefore need some way of enriching the data.\nThis can easily be done with Aladdin\'s `DataEnricher`s.\n\n```python\nmy_db = PostgreSQLConfig.localhost()\nredis = RedisConfig.localhost()\n\nuser_location = my_db.data_enricher( # Fetch all user locations\n    sql="SELECT * FROM user_location"\n).cache( # Cache them for one day\n    ttl=timedelta(days=1),\n    cache_key="user_location_cache"\n).lock( # Make sure only one processer fetches the data at a time\n    lock_name="user_location_lock",\n    redis_config=redis\n)\n\n\nasync def distance_to_users(df: DataFrame) -> Series:\n    user_location_df = await user_location.load()\n    ...\n    return distances\n\nclass SomeFeatures(FeatureView):\n\n    metadata = FeatureViewMetadata(...)\n\n    latitude = Float()\n    longitude = Float()\n\n    distance_to_users = Float().transformed(distance_to_users, using_features=[latitude, longitude])\n```\n\n\n## Access Data\n\nYou can easily create a feature store that contains all your feature definitions.\nThis can then be used to genreate data sets, setup an instce to serve features, DAG\'s etc.\n\n```python\nstore = FeatureStore.from_dir(".")\n\n# Select all features from a single feature view\ndf = await store.all_for("match", limit=2000).to_df()\n```\n\n### Centraliced Feature Store Definition\nYou would often share the features with other coworkers, or split them into different stages, like `staging`, `shadow`, or `production`.\nOne option is therefore to reference the storage you use, and load the `FeatureStore` from there.\n\n```python\naws_bucket = AwsS3Config(...)\nstore = await aws_bucket.file_at("production.json").feature_store()\n\n# This switches from the production online store to the offline store\n# Aka. the batch sources defined on the feature views\nexperimental_store = store.offline_store()\n```\nThis json file can be generated by running `aladdin apply`.\n\n### Select multiple feature views\n\n```python\ndf = await store.features_for({\n    "home_team": ["Man City", "Leeds"],\n    "away_team": ["Liverpool", "Arsenal"],\n}, features=[\n    "match:home_team_score",\n    "match:is_liverpool",\n\n    "other_features:distance_traveled",\n]).to_df()\n```\n\n### Model Service\n\nSelecting features for a model is super simple.\n\n\n```python\ndf = await store.model("test_model").features_for({\n    "home_team": ["Man City", "Leeds"],\n    "away_team": ["Liverpool", "Arsenal"],\n}).to_df()\n```\n\n### Feature View\n\nIf you want to only select features for a specific feature view, then this is also possible.\n\n```python\nprev_30_days = await store.feature_view("match").previous(days=30).to_df()\nsample_of_20 = await store.feature_view("match").all(limit=20).to_df()\n```\n\n## Data quality\nAladdin will make sure all the different features gets formatted as the correct datatype.\nIn this way will there be no incorrect format, value type errors.\n\n## Feature Server\n\nThis expectes that you either run the command in your feature store repo, or have a file with a `RepoReference` instance.\nYou can also setup an online source like Redis, for faster storage.\n\n```python\nredis = RedisConfig.localhost()\n\naws_bucket = AwsS3Config(...)\n\nrepo_files = RepoReference(\n    env_var_name="ENVIRONMENT",\n    repo_paths={\n        "production": aws_bucket.file_at("feature-store/production.json"),\n        "shadow": aws_bucket.file_at("feature-store/shadow.json"),\n        "staging": aws_bucket.file_at("feature-store/staging.json")\n        # else generate the feature store from the current dir\n    }\n)\n\n# Use redis as the online source, if not running localy\nif repo_files.selected != "local":\n    online_source = redis.online_source()\n```\n\nThen run `aladdin serve`, and a FastAPI server will start. Here can you push new features, which then transforms and stores the features, or just fetch them.\n',
    'author': 'Mats E. Mollestad',
    'author_email': 'mats@mollestad.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/otovo/aladdin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
