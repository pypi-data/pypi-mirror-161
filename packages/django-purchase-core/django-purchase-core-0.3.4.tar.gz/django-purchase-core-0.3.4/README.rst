Purchase Core
===============

A reusable Django app for creating, logging and verifying purchases.

Quick start
-----------

1. Install Django Purchase Core & Dependencies:

    >>> pip install django-purchase-core


2. Add "purchase", "rest_framework', and "rangefilter" to your INSTALLED_APPS setting like this:

.. code:: python

        INSTALLED_APPS = [
            ...,
            'rest_framework',
            'purchase',
            'rangefilter',
            ...,
        ]

3. Add the following to app_config.urls:

.. code:: python

    from django.conf.urls import url, include

    urlpatterns = [
        ...,
        path("api/", include("purchase.urls")),
        ...,
    ]


4. Run Django Commands:

    >>> python manage.py makemigrations
    >>> python manage.py migrate


5. Configure configuration and credentials for your game in the admin panel.

Add progress level update processing
-------------------------------------

1. To work with subscription you first need to set authorization and user model:

   * setup "PURCHASE_USER_ATTACHED" in you settings.py to True (not provided equals False, when it False no signal will be called, user model wont be used)

   .. code:: python

        ...
        PURCHASE_USER_ATTACHED = True
        ...

   * configure user model (in your settings.py)

   .. code:: python

        USER_MODEL = YourUserModel

   * configure auth and permission classes for DRF (in your settings.py)

   .. code:: python

        REST_FRAMEWORK = {
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated"
            ],
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "path.to.your.auth.class.or.base"
            ],
        }

   * to handle completed purchase setup receiver to update progress, which will receive "instance"

   .. code:: python

            from django.dispatch import receiver

            from purchase.signals import purchase_completed

            @receiver(purchase_completed)
            def purchase_completed(sender, **kwargs):
                purchase = kwargs["instance"]
                user = purchase.user  # User completed purchase
                purchase_id = purchase.purchase_id  # Your product ID, as it presented in store
                ...


2. To work with subscription you first need to set authorization and user model:

   * configure user model, auth and permission classes for DRF (in your settings.py, as for purchase with user)

   .. code:: python

        ...
        USER_MODEL = YourUserModel
        ...

        ...
        REST_FRAMEWORK = {
            ...
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated"
            ],
            ...
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "path.to.your.auth.class.or.base"
            ],
            ...
        }
        ...

   * setup receiver for signal, which will receive "instance" as Subscription model instance

   .. code:: python

        from django.dispatch import receiver

        from purchase.signals import subscription_completed

        @receiver(subscription_completed)
        def subscription_completed(sender, **kwargs):
            subscription = kwargs["instance"]
            user = subscription.user  # User completed subscription
            subscription_id = subscription.product_id  # your subscription ID, as it presented in store
            ...
