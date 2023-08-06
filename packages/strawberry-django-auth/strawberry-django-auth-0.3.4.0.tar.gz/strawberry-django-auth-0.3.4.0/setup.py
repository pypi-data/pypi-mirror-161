# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gqlauth',
 'gqlauth.bases',
 'gqlauth.factory',
 'gqlauth.migrations',
 'gqlauth.user']

package_data = \
{'': ['*'],
 'gqlauth': ['templates/email/*', 'templates/email/images/*'],
 'gqlauth.factory': ['fonts/*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0',
 'PyJWT>=1.7.1,<3.0',
 'django-admin-display>=1.3.0,<2.0.0',
 'packaging>=20.0,<30.0',
 'strawberry-django-jwt>=0.2.1,<0.3.0',
 'strawberry-graphql-django>=0.2.5,<4.0',
 'strawberry-graphql>=0.69.0,<1.0.0']

extras_require = \
{':python_version <= "3.7"': ['importlib-metadata>=1.7,<5.0']}

setup_kwargs = {
    'name': 'strawberry-django-auth',
    'version': '0.3.4.0',
    'description': 'Graphql authentication system with Strawberry for Django.',
    'long_description': "\n![Tests](https://github.com/nrbnlulu/strawberry-django-auth/actions/workflows/tests.yml/badge.svg)\n[![Pypi](https://img.shields.io/pypi/v/strawberry-django-auth.svg)](https://pypi.org/project/strawberry-django-auth/)\n[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/nrbnlulu/strawberry-django-auth/blob/master/CONTRIBUTING.md)\n# Strawberry-django Auth\n[Django](https://github.com/django/django) registration and authentication with [Strawberry](https://strawberry.rocks/).\n\n## Demo\n\n![Demo Video](https://github.com/nrbnlulu/strawberry-django-auth/blob/main/demo.gif)\n\n## About\n### This Library is the strawberry version of ![Django-graphql-auth](https://github.com/pedrobern/django-graphql-auth/).\n\nAbstract all the basic logic of handling user accounts out of your app,\nso you don't need to think about it and can **get you up and running faster**.\n\nNo lock-in. When you are ready to implement your own code or this package\nis not up to your expectations , it's *easy to extend or switch to\nyour implementation*.\n\n\n### Docs can be found [here](https://nrbnlulu.github.io/strawberry-django-auth/)\n\n## Features\n\n* [x] Awesome docs!\n* [x] Captcha validation\n* [x] Async/Sync supported!\n* [x] Works with ==default or custom== user model\n* [x] JWT authentication <small>(with [Strawberry Django JWT](https://github.com/KundaPanda/strawberry-django-jwt))</small>\n* [x] User registration with email verification\n* [x] Add secondary email, with email verification too\n* [x] Resend activation email\n* [x] Retrieve/Update user\n* [x] Archive user\n* [x] Permanently delete user or make it inactive\n* [x] Turn archived user active again on login\n* [x] Track user status <small>(archived, verified, secondary email)</small>\n* [x] Password change\n* [x] Password reset through email\n* [x] Revoke user tokens on account archive/delete/password change/reset\n* [x] All mutations return `success` and `errors`\n* [x] Default email templates <small>(you will customize though)</small>\n* [x] Customizable, no lock-in\n* [x] Passwordless registration\n* [ ] Currently, only mutation\n\n\n### Full schema features\n\n```python\nimport strawberry\nfrom gqlauth.user import arg_mutations as mutations\n\n\n@strawberry.type\nclass AuthMutation:\n    register = mutations.Register.field\n    verify_account = mutations.VerifyAccount.field\n    resend_activation_email = mutations.ResendActivationEmail.field\n    send_password_reset_email = mutations.SendPasswordResetEmail.field\n    password_reset = mutations.PasswordReset.field\n    password_set = mutations.PasswordSet.field\n    password_change = mutations.PasswordChange.field\n    archive_account = mutations.ArchiveAccount.field\n    delete_account = mutations.DeleteAccount.field\n    update_account = mutations.UpdateAccount.field\n    send_secondary_email_activation = mutations.SendSecondaryEmailActivation.field\n    verify_secondary_email = mutations.VerifySecondaryEmail.field\n    swap_emails = mutations.SwapEmails.field\n    captcha = mutations.Captcha.field\n\n    # django-graphql-jwt authentication\n    # with some extra features\n    token_auth = mutations.ObtainJSONWebToken.field\n    verify_token = mutations.VerifyToken.field\n    refresh_token = mutations.RefreshToken.field\n    revoke_token = mutations.RevokeToken.field\n\n\nschema = strawberry.Schema(mutation=AuthMutation)\n```\n\n## Contributing\n\nSee [CONTRIBUTING.md](https://github.com/nrbnlulu/strawberry-django-auth/blob/master/CONTRIBUTING.md)\n",
    'author': 'Nir.J Benlulu',
    'author_email': 'nrbnlulu@gmail.com',
    'maintainer': 'Nir.J Benlulu',
    'maintainer_email': 'nrbnlulu@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
