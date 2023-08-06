# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['purchase',
 'purchase.controllers',
 'purchase.exceptions',
 'purchase.loggers',
 'purchase.migrations',
 'purchase.models',
 'purchase.serializers',
 'purchase.signals',
 'purchase.strings',
 'purchase.templates',
 'purchase.verifiers',
 'purchase.views']

package_data = \
{'': ['*']}

install_requires = \
['Django>=4.0.1,<5.0.0',
 'Pygments>=2.10.0,<3.0.0',
 'django-admin-rangefilter>=0.8.1,<0.9.0',
 'django-filter>=2.4.0,<3.0.0',
 'djangorestframework>=3.12.4,<4.0.0',
 'drf-yasg>=1.21.3,<2.0.0',
 'google-api-python-client>=2.21.0,<3.0.0',
 'google-auth-oauthlib>=0.4.6,<0.5.0',
 'google-auth>=2.1.0,<3.0.0',
 'google>=3.0.0,<4.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'django-purchase-core',
    'version': '0.3.3',
    'description': 'A reusable Django app for creating, logging and verifying purchases.',
    'long_description': 'Purchase Core\n===============\n\nA reusable Django app for creating, logging and verifying purchases.\n\nQuick start\n-----------\n\n1. Install Django Purchase Core & Dependencies:\n\n    >>> pip install django-purchase-core\n\n\n2. Add "purchase", "rest_framework\', and "rangefilter" to your INSTALLED_APPS setting like this:\n\n.. code:: python\n\n        INSTALLED_APPS = [\n            ...,\n            \'rest_framework\',\n            \'purchase\',\n            \'rangefilter\',\n            ...,\n        ]\n\n3. Add the following to app_config.urls:\n\n.. code:: python\n\n    from django.conf.urls import url, include\n\n    urlpatterns = [\n        ...,\n        path("api/", include("purchase.urls")),\n        ...,\n    ]\n\n\n4. Run Django Commands:\n\n    >>> python manage.py makemigrations\n    >>> python manage.py migrate\n\n\n5. Configure configuration and credentials for your game in the admin panel.\n\nAdd progress level update processing\n-------------------------------------\n\n1. To work with subscription you first need to set authorization and user model:\n\n   * setup "PURCHASE_USER_ATTACHED" in you settings.py to True (not provided equals False, when it False no signal will be called, user model wont be used)\n\n   .. code:: python\n\n        ...\n        PURCHASE_USER_ATTACHED = True\n        ...\n\n   * configure user model (in your settings.py)\n\n   .. code:: python\n\n        USER_MODEL = YourUserModel\n\n   * configure auth and permission classes for DRF (in your settings.py)\n\n   .. code:: python\n\n        REST_FRAMEWORK = {\n            "DEFAULT_PERMISSION_CLASSES": [\n                "rest_framework.permissions.IsAuthenticated"\n            ],\n            "DEFAULT_AUTHENTICATION_CLASSES": [\n                "path.to.your.auth.class.or.base"\n            ],\n        }\n\n   * to handle completed purchase setup receiver to update progress, which will receive "instance"\n\n   .. code:: python\n\n            from django.dispatch import receiver\n\n            from purchase.signals import purchase_completed\n\n            @receiver(purchase_completed)\n            def purchase_completed(sender, **kwargs):\n                purchase = kwargs["instance"]\n                user = purchase.user  # User completed purchase\n                purchase_id = purchase.purchase_id  # Your product ID, as it presented in store\n                ...\n\n\n2. To work with subscription you first need to set authorization and user model:\n\n   * configure user model, auth and permission classes for DRF (in your settings.py, as for purchase with user)\n\n   .. code:: python\n\n        ...\n        USER_MODEL = YourUserModel\n        ...\n\n        ...\n        REST_FRAMEWORK = {\n            ...\n            "DEFAULT_PERMISSION_CLASSES": [\n                "rest_framework.permissions.IsAuthenticated"\n            ],\n            ...\n            "DEFAULT_AUTHENTICATION_CLASSES": [\n                "path.to.your.auth.class.or.base"\n            ],\n            ...\n        }\n        ...\n\n   * setup receiver for signal, which will receive "instance" as Subscription model instance\n\n   .. code:: python\n\n        from django.dispatch import receiver\n\n        from purchase.signals import subscription_completed\n\n        @receiver(subscription_completed)\n        def subscription_completed(sender, **kwargs):\n            subscription = kwargs["instance"]\n            user = subscription.user  # User completed subscription\n            subscription_id = subscription.product_id  # your subscription ID, as it presented in store\n            ...\n',
    'author': 'Qmobi',
    'author_email': 'info@qmobi.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/boy-scouts/game-core-purchase',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
