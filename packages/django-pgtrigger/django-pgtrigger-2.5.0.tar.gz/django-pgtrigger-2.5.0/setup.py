# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgtrigger',
 'pgtrigger.management',
 'pgtrigger.management.commands',
 'pgtrigger.tests',
 'pgtrigger.tests.migrations']

package_data = \
{'': ['*']}

install_requires = \
['django-pgconnection>=1.0.1', 'django>=2']

setup_kwargs = {
    'name': 'django-pgtrigger',
    'version': '2.5.0',
    'description': 'Postgres trigger support integrated with Django models.',
    'long_description': 'django-pgtrigger\n################\n\n``django-pgtrigger`` provides primitives for configuring\n`Postgres triggers <https://www.postgresql.org/docs/current/sql-createtrigger.html>`__\non Django models.\n\nTriggers can solve a\nwide variety of database-level problems more elegantly and reliably\nthan in the application-level of Django. Here are some common\nproblems that can be solved with triggers, many of which we later show how to\nsolve in the docs:\n\n1. Protecting updates and deletes or rows or columns (``pgtrigger.Protect``).\n2. Soft deleting models by setting a field to a value on delete (``pgtrigger.SoftDelete``).\n3. Tracking changes to models or columns change, or when specific conditions\n   happen (`django-pghistory <https://django-pghistory.readthedocs.io>`__ uses ``django-pgtrigger`` to do this).\n4. Keeping fields in sync with other fields.\n5. Ensuring that engineers use an official interface\n   (e.g. engineers must use ``User.objects.create_user`` and not\n   ``User.objects.create``).\n6. Only allowing a status field of a model to transition through certain\n   states (``pgtrigger.FSM``).\n\nQuick Start\n===========\n\nInstall ``django-pgtrigger`` with ``pip3 install django-pgtrigger`` and\nadd ``pgtrigger`` to ``settings.INSTALLED_APPS``.\n\nTriggers are declared in the ``triggers`` attribute of the model ``Meta``.\nIf you don\'t have access to the model definition,\nyou can still call ``pgtrigger.register`` programmatically.\n\nUsers declare the PL/pgSQL code\nin a ``pgtrigger.Trigger`` object or use the derived triggers in\n``django-pgtrigger`` for common scenarios. For example,\n``pgtrigger.Protect`` protects operations on a model, such as deletions:\n\n.. code-block:: python\n\n    from django.db import models\n    import pgtrigger\n\n\n    class CannotBeDeletedModel(models.Model):\n        """This model cannot be deleted!"""\n\n        class Meta:\n            triggers = [\n                pgtrigger.Protect(name=\'protect_deletes\', operation=pgtrigger.Delete)\n            ]\n\n``django-pgtrigger`` implements common Django idioms.\nFor example, users can use ``pgtrigger.Q`` and ``pgtrigger.F`` objects to\nconditionally execute triggers based on the ``OLD`` and ``NEW`` row\nbeing modified.\n\nFor example, here we protect deletion of "active" rows of a model:\n\n.. code-block:: python\n\n    from django.db import models\n    import pgtrigger\n\n\n    class CannotBeDeletedModel(models.Model):\n        """Active model object cannot be deleted!"""\n        is_active = models.BooleanField(default=True)\n\n        class Meta:\n            triggers = [\n                pgtrigger.Protect(\n                    name=\'protect_deletes\',\n                    operation=pgtrigger.Delete,\n                    # Protect deletes when the OLD row of the trigger is still active\n                    condition=pgtrigger.Q(old__is_active=True)\n                )\n            ]\n\n\nCombining ``pgtrigger.Q``, ``pgtrigger.F``, and derived ``pgtrigger.Trigger``\nobjects can solve a wide array of Django problems without ever having to\nwrite raw SQL. Users, however, can still customize\ntriggers and write as much raw SQL as needed for their use case.\n\n\nTutorial\n========\n\nFor a complete run-through of ``django-pgtrigger`` and all derived\ntriggers (along with a trigger cookbook!), read the\n`pgtrigger docs <https://django-pgtrigger.readthedocs.io/>`__. The docs\nhave a full tutorial of how to configure triggers and lots of code examples.\n\nAfter you have gone through the\ntutorial in the docs, check out\n`<https://wesleykendall.github.io/django-pgtrigger-tutorial/>`__, which\nis an interactive tutorial written for a Django meetup talk about\n``django-pgtrigger``.\n\n\nDocumentation\n=============\n\n`View the django-pgtrigger docs here\n<https://django-pgtrigger.readthedocs.io/>`_.\n\nInstallation\n============\n\nInstall django-pgtrigger with::\n\n    pip3 install django-pgtrigger\n\nAfter this, add ``pgtrigger`` to the ``INSTALLED_APPS``\nsetting of your Django project.\n\nContributing Guide\n==================\n\nFor information on setting up django-pgtrigger for development and\ncontributing changes, view `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.\n\nPrimary Authors\n===============\n\n- @wesleykendall (Wes Kendall)\n\nOther Contributors\n==================\n\n- @jzmiller1\n- @rrauenza\n',
    'author': 'Wes Kendall',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Opus10/django-pgtrigger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<4',
}


setup(**setup_kwargs)
