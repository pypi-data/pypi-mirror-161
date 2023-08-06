# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tf_notify', 'tf_notify.callbacks']

package_data = \
{'': ['*']}

install_requires = \
['notifiers>=1.3.3,<1.4.0', 'tensorflow>=2.7.3,<=2.9.1']

setup_kwargs = {
    'name': 'tf-notify',
    'version': '0.3.0',
    'description': 'Want to get notified on the progress of your TensorFlow model training? Enter, a TensorFlow Keras callback to send notifications on the messaging app of your choice.',
    'long_description': '# tf-notify\n\n[![PyPI](https://img.shields.io/pypi/v/tf-notify?color=blue&label=PyPI&logo=PyPI&logoColor=white)](https://pypi.org/project/tf-notify/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tf-notify?logo=python&logoColor=white)](https://www.python.org/) [![TensorFlow version](https://shields.io/badge/tensorflow-2.7%20%7C%202.8%20%7C%202.9%20-simple?logo=tensorflow&style=flat)](https://www.tensorflow.org/)\n[![codecov](https://codecov.io/gh/ilias-ant/tf-notify/branch/main/graph/badge.svg?token=2H0VB8I8IH)](https://codecov.io/gh/ilias-ant/tf-notify) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![GitHub Workflow Status](https://img.shields.io/github/workflow/status/ilias-ant/tf-notify/CI)](https://github.com/ilias-ant/tf-notify/actions/workflows/ci.yml)\n[![Documentation Status](https://readthedocs.org/projects/tf-notify/badge/?version=latest)](https://tf-notify.readthedocs.io/en/latest/?badge=latest)\n[![PyPI - Wheel](https://img.shields.io/pypi/wheel/tf-notify?color=orange)](https://www.python.org/dev/peps/pep-0427/)\n\n> Want to get notified on the progress of your TensorFlow model training?\n\nThis package provides a [tf.keras](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/Callback) callback to send notifications to a messaging app of your choice.\n\n## Install\n\nThe recommended installation is via `pip`:\n\n```bash\npip install tf-notify\n```\n\n## Supported Apps\n\nThe following apps are currently supported. But, do check the project frequently, as many more will soon be supported!\n\n<table>\n  <tr>\n    <td>\n      <img src="https://raw.githubusercontent.com/ilias-ant/tf-notify/main/static/logos/slack.png" height="128" width="128" style="max-height: 128px; max-width: 128px;"><a href="https://tf-notify.readthedocs.io/en/latest/api/#tf_notify.callbacks.slack.SlackCallback">Slack</a>\n    </td>\n   <td>\n      <img src="https://raw.githubusercontent.com/ilias-ant/tf-notify/main/static/logos/telegram.png" height="128" width="128" style="max-height: 128px; max-width: 128px;"><a href="https://tf-notify.readthedocs.io/en/latest/api/#tf_notify.callbacks.telegram.TelegramCallback">Telegram</a>\n    </td>\n   <td>\n      <img src="https://raw.githubusercontent.com/ilias-ant/tf-notify/main/static/logos/email.png" height="128" width="128" style="max-height: 128px; max-width: 128px;"><a href="https://tf-notify.readthedocs.io/en/latest/api/#tf_notify.callbacks.email.EmailCallback">Email (SMTP)</a>\n    </td>\n  </tr>\n</table>\n\n## Usage\n\n```python\nimport tensorflow as tf\nfrom tf_notify import SlackCallback\n\n\n# define the tf.keras model to add callbacks to\nmodel = tf.keras.Sequential(name=\'neural-network\')\nmodel.add(tf.keras.layers.Dense(1, input_dim=784))\nmodel.compile(\n    optimizer=tf.keras.optimizers.RMSprop(learning_rate=0.1),\n    loss="mean_squared_error",\n    metrics=["mean_absolute_error"],\n)\n\nmodel.fit(\n    x_train,\n    y_train,\n    batch_size=128,\n    epochs=2,\n    verbose=0,\n    validation_split=0.5,\n    callbacks=[\n        SlackCallback(webhook_url=\'https://url.to/webhook\')\n    ],  # send a Slack notification when training ends!\n)\n```\n\nYou should see something like this on your Slack:\n\n<img src="https://raw.githubusercontent.com/ilias-ant/tf-notify/main/static/slack_notification_example.png" width="50%" text="https://www.researchgate.net/figure/Sample-images-from-MURA-dataset_fig2_348282230">\n\n\n\n## How to contribute\n\nIf you wish to contribute, [this](CONTRIBUTING.md) is a great place to start!\n\n## License\n\nDistributed under the [Apache-2.0 license](LICENSE).',
    'author': 'Ilias Antonopoulos',
    'author_email': 'ilias.antonopoulos@yahoo.gr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/tf-notify',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
