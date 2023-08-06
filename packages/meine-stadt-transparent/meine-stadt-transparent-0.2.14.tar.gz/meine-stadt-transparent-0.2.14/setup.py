# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cms',
 'cms.migrations',
 'importer',
 'importer.management',
 'importer.management.commands',
 'importer.migrations',
 'importer.tests',
 'mainapp',
 'mainapp.documents',
 'mainapp.functions',
 'mainapp.management',
 'mainapp.management.commands',
 'mainapp.migrations',
 'mainapp.models',
 'mainapp.tests',
 'mainapp.tests.elasticsearch',
 'mainapp.tests.live',
 'mainapp.tests.main',
 'mainapp.views',
 'mainapp.views.feeds',
 'meine_stadt_transparent',
 'meine_stadt_transparent.settings']

package_data = \
{'': ['*'],
 'cms': ['fixtures/*',
         'locale/de/LC_MESSAGES/*',
         'templates/*',
         'templates/cms/*'],
 'importer': ['fixtures/*', 'locale/de/LC_MESSAGES/*', 'test-data/*'],
 'mainapp': ['fixtures/*',
             'locale/de/LC_MESSAGES/*',
             'templates/*',
             'templates/account/*',
             'templates/email/*',
             'templates/error/*',
             'templates/info/*',
             'templates/mainapp/*',
             'templates/mainapp/file/*',
             'templates/mainapp/index/*',
             'templates/mainapp/index_v2/*',
             'templates/mainapp/search/*',
             'templates/partials/*',
             'templates/socialaccount/*',
             'templates/socialaccount/snippets/*']}

install_requires = \
['Django>=4.0.6,<4.1.0',
 'PyPDF2>=2.9.0,<3.0.0',
 'Wand>=0.6.0,<0.7.0',
 'django-allauth>=0.51,<0.52',
 'django-anymail[mailjet,sendgrid]>=8.1,<9.0',
 'django-decorator-include>=2.1,<4.0',
 'django-elasticsearch-dsl>=7.1,<7.3',
 'django-environ>=0.9.0,<0.10.0',
 'django-geojson>=3.0,<4.0',
 'django-q[sentry]>=1.3.9,<2.0.0',
 'django-settings-export>=1.2,<2.0',
 'django-simple-history>=3.0,<4.0',
 'django-webpack-loader>=1.6.0,<1.7.0',
 'django-widget-tweaks>=1.4,<2.0',
 'django_csp>=3.4,<4.0',
 'elasticsearch-dsl>=7.3,<8.0',
 'elasticsearch==7.10.1',
 'geoextract>=0.3.1,<0.4.0',
 'geopy>=2.0.0,<3.0.0',
 'gunicorn>=20.0,<21.0',
 'html2text>=2019.8,<2021.0',
 'icalendar>=4.0,<5.0',
 'jsonfield>=3.1,<4.0',
 'minio>=5,<8',
 'mysqlclient>=1.3,<3.0',
 'osm2geojson>=0.2.0,<0.3.0',
 'psycopg2>=2.9.3,<3.0.0',
 'python-dateutil>=2.7,<3.0',
 'python-slugify>=5,<7',
 'requests>=2.22,<3.0',
 'sentry-sdk>=1.0.0,<2.0.0',
 'splinter>=0.14,<0.18',
 'tqdm>=4.29,<5.0',
 'wagtail>=3.0,<3.1']

extras_require = \
{'import-json': ['cattrs>=22.1.0,<23.0.0'], 'pgp': ['pgpy>=0.5.2,<0.6.0']}

entry_points = \
{'console_scripts': ['mst-manage = manage:main']}

setup_kwargs = {
    'name': 'meine-stadt-transparent',
    'version': '0.2.14',
    'description': 'A website to bring municipal politics to citizens',
    'long_description': '# Meine Stadt Transparent\n\n![Tests](https://github.com/meine-stadt-transparent/meine-stadt-transparent/workflows/Tests/badge.svg)\n[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmeine-stadt-transparent%2Fmeine-stadt-transparent.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fmeine-stadt-transparent%2Fmeine-stadt-transparent?ref=badge_shield)\n![Docker build](https://github.com/meine-stadt-transparent/meine-stadt-transparent/workflows/Docker%20build/badge.svg)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/ambv/black)\n\nMeine Stadt Transparent is a free council information system. Its current main focus is presenting data from offical German council information systems, so called "Ratsinformationssysteme". Those are imported using the [OParl](https://oparl.org) API, which can easily customized. You can even write your own importer for arbitrary data sources.\n\nOur sample live system using the data of the city [Krefeld](https://www.krefeld.de/) is available at: [https://krefeld.meine-stadt-transparent.de/](https://krefeld.meine-stadt-transparent.de/). We provide a public chat on riot at `#meine-stadt-transparent:matrix.org`, which you can join on [matrix](https://matrix.to/#/#meine-stadt-transparent:matrix.org?via=matrix.org).\n\nThe project was sponsored by the [Prototype Fund](https://prototypefund.de/).\n\n![Logo of the Prototype Fund](etc/prototype-fund-logo.svg) ![Gefördert von Bundesministetrium für Bilduung und Forschung](etc/bmbf-logo.svg) ![Logo of the Open Knowledge Foundation Germany](etc/okfde-logo.svg)\n\n## About this project\n\nMeine Stadt Transparent makes decision-making in city councils and administrations more transparent by providing easy access to information about the city council, including published documents, motions and meeting agendas. As a successor to Munich\'s [München Transparent](https://www.muenchen-transparent.de/), its aim is to be easily deployable for as many cities as possible.\n\nIt includes many features regarding data research and staying up to date, targeted both towards citizens and journalists:\n\n- Information about city councillors, administrative organizations and meetings of the city council are provided.\n- All published documents are searchable in a flexible manner, be it motions, resolutions, meeting agendas or protocols. The search supports both simple full-text searches and flexible criteria-based filters.\n- Documents are automatically searched for mentioned places. A map is provided indicating places that are mentioned. Thus, it is easy to identify documents that affect places in your living neighborhood.\n- You can subscribe to topics / search expressions to get notified by e-mail, once new documents matching your query are published.\n- It supports several ways of subscribing to new content: different kinds of RSS-feeds and subscribing to the meeting calendar using the iCal-format.\n- We try to make Meine Stadt Transparent accessible by everyone: the layout is responsive to provide a good experience on mobile device, and we follow accessibility standards (WCAG 2.0 AA, ARIA) as close as possible.\n\nMeine Stadt Transparent is *not* a complete replacement for traditional council information systems, however: it focuses on displaying already published information to the public. It does not provide a user-accessible backend for content authoring. It relies on the availability of an API provided by a council information system backend. Currently, the open [Oparl-Standard](https://oparl.org/) is supported.\n\n## Production setup with docker compose\n\nPrerequisites: A host with root access and enough ram for elasticsearch and mariadb. If you don\'t have much ram, create a big swapfile for memory spikes in the import.\n\nAll services will run in docker containers orchestrated by docker compose, with nginx as reverse proxy in front of them which also serves static files.\n\nFirst, install [docker](https://docs.docker.com/install/) and [docker compose](https://docs.docker.com/compose/install/). Then [adjust max_map_count](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#docker-cli-run-prod-mode) on the host system for elasticsearch.\n\nDownload [etc/docker-compose.yml](etc/docker-compose.yml) from the root of this repository. Replace all `changeme` with real random passwords (Hint: `openssl rand -hex 32`).\n\nDownload [etc/template.env](etc/template.env) to `.env`. Change `REAL_HOST` to your domain, `SECRET_KEY` to a randomly generated secret and use the same passwords as in `docker-compose.yml` for `DATABASE_URL`, and `MINIO_SECRET_KEY`. You most likely want to configure third-party services as described later, but you can postpone that until after the base site works.\n\nTo deliver the assets through nginx, we need to mount them to a local container:\n\n```\nmkdir log\nchown 33:33 log\nrm -rf /var/www/meine-stadt-transparent-static # Delete existing or it will land in a subdirectory \ndocker cp django:/static /var/www/meine-stadt-transparent-static\n```\n\nYou can change the directory to any other as long as you match that later in your nginx conf.\n\nStart everything:\n\n```\ndocker-compose up\n```\n\nWait until the elasticsearch log says `Cluster health status changed from [RED] to [YELLOW]` and open another terminal. You can later start the services as daemons with `-d` or stop them with `docker-compose down`.\n\nThen we can run the migrations, create the buckets for minio (our file storage) and create the elasticsearch indices. If something failed you can rerun the setup command, it will only create missing indices.\n\n```\ndocker-compose run --rm django ./manage.py setup\n```\n\nLet\'s load some dummy data to check everythings wokring:\n\n```\ndocker-compose run --rm django ./manage.py loaddata mainapp/fixtures/initdata.json\n```\n\nYou should now get a 200 response from [localhost:8000](http://localhost:8000).\n\nIf you\'ve not familiar with nginx, you should start with [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04). Install nginx, [certbot](https://certbot.eff.org/) and the certbot nginx integration. For ubuntu it is e.g.\n\n```\nsudo add-apt-repository ppa:certbot/certbot\nsudo apt update\nsudo apt install nginx certbot python3-certbot-nginx\n```\n\nDownload [etc/nginx-http.conf](etc/nginx-http.conf), add it to your nginx sites and replace `changeme.tld` with your domain. Then run certbot and follow the instructions:\n\n```\ncertbot --nginx\n```\n\nCertbot will rewrite the nginx configuration to a version with strong encryption. You might also want to activate http/2 by adding `http2` after both `443 ssl`.\n\nYou now have a proper site at your domain!\n\nNow that everything is in place, drop the dummy data:\n\n```\ndocker-compose run --rm django ./manage.py flush\n```\n\nInstead, import real data by replacing `Springfield` with the name of your city. See [docs/Import.md](docs/Import.md) for details.\n\n```\ndocker-compose run --rm django ./manage.py import Springfield\n```\n\nYou should now have a usable instance!\n\nFinally, create a daily cronjob with the following. This will import changed objects from the oparl api and then notify the users. Also make sure that there is a cronjob for certbot.\n\n```\ndocker-compose run --rm django ./manage.py cron\n```\n\nYou can execute all the other commands from this readme by prepending them with `docker-compose run --rm django` (or starting a shell in the container). Note for advanced users: `.venv/bin/python` is configured as entrypoint.\n\nNext, have a look at [docs/Customization.md](docs/Customization.md).\n\n### Updates\n\nAfter pulling a new version of the docker container, you need to run the following commands to update the assets:\n\n```\ndocker-compose down\nrm -r /var/www/meine-stadt-transparent-static\nmkdir /var/www/meine-stadt-transparent-static\ndocker-compose run --rm django ./manage.py setup\ndocker-compose up -d\n```\n\n### Kubernetes\n\nIf you have a Kubernetes cluster, you can have a look at [this experimental setup](https://github.com/codeformuenster/kubernetes-deployment/tree/master/sources/meine-stadt-transparent) which is used by Münster.\n\n## Manual Setup\n\n### Requirements\n\n- Python 3.8, 3.9 or 3.10 with pip and [poetry](https://github.com/sdispater/poetry) 1.1\n- A recent node version (v16) with npm (v8)\n- A webserver (nginx or apache is recommended)\n- A Database (MariaDB is recommended, though anything that django supports should work)\n- [minio](https://docs.min.io/)\n- If you want to use elasticsearch, you either need [docker and docker compose](https://docs.docker.com/engine/installation/) or will have to [install elasticsearch 7.9 yourself](https://www.elastic.co/guide/en/elasticsearch/reference/7.9/install-elasticsearch.html)\n\nOn Debian/Ubuntu:\n\n```\nsudo apt install python3-pip python3-venv python3-dev nodejs \\\n    git libmysqlclient-dev libmagickwand-dev poppler-utils libssl-dev gettext\n```\n\nInstall dependencies.\n\n```\npoetry config virtualenvs.in-project true # This is not mandatory, yet quite useful\npoetry install\nnpm install\n```\n\nActivate the virtualenv created by poetry. You either need to run this in your shell before running any other python command or prefix any python command with `poetry run`.\n\n```\npoetry shell\n```\n\nCopy [etc/template.env](etc/template.env) to `.env` and adjust the values. You can specify a different dotenv file with the `ENV_PATH` environment variable.\n\nConfigure your webserver, see e.g. [etc/nginx.conf](etc/nginx.conf)\n\n### Production\n\nThe following steps are only required when you want to deploy the site to production. For development, see the corresponding section below\n\n ```\nnpm run build:prod\nnpm run build:email\n./manage.py collectstatic\n ```\n\nFollow the [the official guide](https://docs.djangoproject.com/en/1.11/howto/deployment/). Unlike the guide, we recommend gunicorn over wsgi as gunicorn is much simpler to configure.\n\nThe site is now ready :tada:. Next, have a look at [docs/Customization.md](docs/Customization.md) and [docs/Import.md](docs/Import.md).\n\n### Development\n\nPlease refer to [docs/Development.md](docs/Development.md)\n\n## Known Problems\n\nIf you hit problems regarding memory when starting elasticsearch, please have a look at this\n[documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#docker-cli-run-prod-mode).\n\nIf MySQL/MariaDB is to be used as a database backend, a Version of at least 5.7 (MySQL) or 10.2 (MariaDB) is needed, with Barracuda being set as the default format for new InnoDB-Tables (default), otherwise you will run into errors about too long Indexes.\n\n## License\n\nThis software is published under the terms of the MIT license. The json files under `testdata/oparl` are adapted from the oparl project and licensed under CC-BY-SA-4.0. The license of the included animal pictures `mainapp/assets/images` are CC0 and CC-BY-SA Luigi Rosa. The redistribution of `etc/Donald Knuth - The Complexity of Songs.pdf` is explicitly allowed in its last paragraph.\n\n[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmeine-stadt-transparent%2Fmeine-stadt-transparent.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fmeine-stadt-transparent%2Fmeine-stadt-transparent?ref=badge_large)\n',
    'author': 'Tobias Hößl',
    'author_email': 'tobias@hoessl.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
