# pynnacle

> A utility class to simplify sending emails.

[![PyPI][pypi-image]][pypi-url]
[![Downloads][downloads-image]][downloads-url]
[![Status][status-image]][pypi-url]
[![Python Version][python-version-image]][pypi-url]
[![Format][format-image]][pypi-url]
[![Requirements][requirements-status-image]][requirements-status-url]
[![tests][tests-image]][tests-url]
[![Codecov][codecov-image]][codecov-url]
[![CodeFactor][codefactor-image]][codefactor-url]
[![Codeclimate][codeclimate-image]][codeclimate-url]
[![Lgtm alerts][lgtm-alerts-image]][lgtm-alerts-url]
[![Lgtm quality][lgtm-quality-image]][lgtm-quality-url]
[![CodeQl][codeql-image]][codeql-url]
[![readthedocs][readthedocs-image]][readthedocs-url]
[![pre-commit][pre-commit-image]][pre-commit-url]
[![pre-commit.ci status][pre-commit.ci-image]][pre-commit.ci-url]
[![Code style: black][black-image]][black-url]
[![Checked with mypy][mypy-image]][mypy-url]
[![security: bandit][bandit-image]][bandit-url]
[![Commitizen friendly][commitizen-image]][commitizen-url]
[![Conventional Commits][conventional-commits-image]][conventional-commits-url]
[![DeepSource][deepsource-image]][deepsource-url]
[![license][license-image]][license-url]

Pynnacle provides a wrapper to mimetypes, smtplib and email.message libraries to provide a simplified facade
interface to make sending emails as simple as possible. It abstracts away all the low level details and when
imported into other modules provides a clean, clutter-free interface.

![](assets/header.png)

## Installation

OS X & Linux:

```sh
pip3 install pynnacle
```

Windows:

```sh
pip install pynnacle
```

## Usage example

Firstly import the module

```sh
from pynnacle.pynnacle import SendEmail
```

Pynnacle stores the configuration of email servers in an 'ini' file.
If a service is already configured then the main class can be instatiated with only 3 arguments as follows:

```sh
mailer = SendEmail(
    service="gmail"
    user_id=user_id,
    user_pass=user_pass,
)
```

If the service hs not been configured, simple pass "custom" as the service and pass the other smtp arguments
to the initializer as follows:

```sh
mailer = SendEmail(
    service="custom"
    user_id=user_id,
    user_pass=user_pass,
    smtp_server=server,
    smtp_port=port,
    smtp_authentication=auth,
    smtp_encryption=encrypt,
)
```

Then simply send the email

```sh
mailer.message_send(
    subject="Hi There",
    sender="sender@abc.com",
    recipient="recipient@xyz.com",
    body="This is where the text of the email body goes",
)
```

cc, bcc and attachments arguments can also be used, supplied as lists

```sh
mailer.message_send(
    subject="Hi There",
    sender="sender@abc.com",
    recipient="recipient@xyz.com",
    body="This is where the text of the email body goes",
    cc=["person1@def.com", "person2@ghi.com"],
    bcc=["person3@jkl.com", "person4@mno.com"],
    attachments=["path_to_file1", "path_to_file2"]
)
```

## Further simplifications

### Storing and Reusing SMTP

Additional setting can be saved in the "ini" file as and when you like.

e.g.config.ini

```sh
[gmail]
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_authentication = yes
smtp_encryption = yes
pop3_server = pop.gmail.com
pop3_port = 995
pop3_authentication = yes
pop3_encryption = yes
```

### Storing credentials

To avoid hard-coding any credentials I use the Python [keyring](https://github.com/jaraco/keyring) library

```sh
service = "gmail"

user_id = keyring.get_password(service, "service_id")
user_pass = keyring.get_password(service, "service_password")
```

_For more examples and usage, please refer to the [Wiki][wiki]._

## A Note on gmail authentication

As of 30/05/2022 Google will no longer support the use of third-party apps or devices that only ask for your username and password.
The "Less secure app access" setting has now been turned off.
The application now has to be assigned a 16 byte code which can be configured from your account as follows:

- 1 Log onto your account: https://myaccount.google.com
- 2 Goto security
- 3 Enable 2-step verification
- 4 click "App password" to generate the key

Then simply use this along with the account email address to authenticate

## Development setup

Describe how to install all development dependencies and how to run an automated test-suite of some kind. Potentially do this for multiple platforms.

```sh
pip install --editable pynnacle
```

## Documentation

### - [**Read the Docs**](https://pynnacle.readthedocs.io/en/latest/)

### - [**Wiki**](https://github.com/Stephen-RA-King/pynnacle/wiki)

## Meta

[![](assets/linkedin.png)](https://linkedin.com/in/stephen-k-3a4644210)
[![](assets/github.png)](https://github.com/Stephen-RA-King)
[![](assets/pypi.png)](https://pypi.org/project/pynnacle/)
[![](assets/www.png)](https://www.justpython.tech)
[![](assets/email.png)](mailto:stephen.ra.king@gmail.com)
[![](assets/cv.png)](https://www.justpython.tech/cv)

Stephen R A King : stephen.ra.king@gmail.com

Distributed under the MIT license. See [license](license-url) for more information.

[https://github.com/Stephen-RA-King/pynnacle](https://github.com/Stephen-RA-King/pynnacle)

Created with Cookiecutter template: [**cc_template**][cc_template-url] version 1.2.0

<!-- Markdown link & img dfn's -->

[bandit-image]: https://img.shields.io/badge/security-bandit-yellow.svg
[bandit-url]: https://github.com/PyCQA/bandit
[black-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-url]: https://github.com/psf/black
[cc_template-url]: https://github.com/Stephen-RA-King/cc_template
[codeclimate-image]: https://api.codeclimate.com/v1/badges/7fc352185512a1dab75d/maintainability
[codeclimate-url]: https://codeclimate.com/github/Stephen-RA-King/pynnacle/maintainability
[codecov-image]: https://codecov.io/gh/Stephen-RA-King/pynnacle/branch/main/graph/badge.svg
[codecov-url]: https://app.codecov.io/gh/Stephen-RA-King/pynnacle
[codefactor-image]: https://www.codefactor.io/repository/github/Stephen-RA-King/pynnacle/badge
[codefactor-url]: https://www.codefactor.io/repository/github/Stephen-RA-King/pynnacle
[codeql-image]: https://github.com/Stephen-RA-King/pynnacle/actions/workflows/codeql-analysis.yml/badge.svg
[codeql-url]: https://github.com/Stephen-RA-King/pynnacle/actions/workflows/codeql-analysis.yml
[commitizen-image]: https://img.shields.io/badge/commitizen-friendly-brightgreen.svg
[commitizen-url]: http://commitizen.github.io/cz-cli/
[conventional-commits-image]: https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square
[conventional-commits-url]: https://conventionalcommits.org
[deepsource-image]: https://static.deepsource.io/deepsource-badge-light-mini.svg
[deepsource-url]: https://deepsource.io/gh/Stephen-RA-King/pynnacle/?ref=repository-badge
[downloads-image]: https://static.pepy.tech/personalized-badge/pynnacle?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads
[downloads-url]: https://pepy.tech/project/pynnacle
[format-image]: https://img.shields.io/pypi/format/pynnacle
[lgtm-alerts-image]: https://img.shields.io/lgtm/alerts/g/Stephen-RA-King/pynnacle.svg?logo=lgtm&logoWidth=18
[lgtm-alerts-url]: https://lgtm.com/projects/g/Stephen-RA-King/pynnacle/alerts/
[lgtm-quality-image]: https://img.shields.io/lgtm/grade/python/g/Stephen-RA-King/pynnacle.svg?logo=lgtm&logoWidth=18
[lgtm-quality-url]: https://lgtm.com/projects/g/Stephen-RA-King/pynnacle/context:python
[license-image]: https://img.shields.io/pypi/l/pynnacle
[license-url]: https://github.com/Stephen-RA-King/pynnacle/blob/main/license
[mypy-image]: http://www.mypy-lang.org/static/mypy_badge.svg
[mypy-url]: http://mypy-lang.org/
[pre-commit-image]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
[pre-commit-url]: https://github.com/pre-commit/pre-commit
[pre-commit.ci-image]: https://results.pre-commit.ci/badge/github/Stephen-RA-King/gitwatch/main.svg
[pre-commit.ci-url]: https://results.pre-commit.ci/latest/github/Stephen-RA-King/gitwatch/main
[pypi-url]: https://pypi.org/project/pynnacle/
[pypi-image]: https://img.shields.io/pypi/v/pynnacle.svg
[python-version-image]: https://img.shields.io/pypi/pyversions/pynnacle
[readthedocs-image]: https://readthedocs.org/projects/pynnacle/badge/?version=latest
[readthedocs-url]: https://pynnacle.readthedocs.io/en/latest/?badge=latest
[requirements-status-image]: https://requires.io/github/Stephen-RA-King/pynnacle/requirements.svg?branch=main
[requirements-status-url]: https://requires.io/github/Stephen-RA-King/pynnacle/requirements/?branch=main
[status-image]: https://img.shields.io/pypi/status/pynnacle.svg
[tests-image]: https://github.com/Stephen-RA-King/pynnacle/actions/workflows/tests.yml/badge.svg
[tests-url]: https://github.com/Stephen-RA-King/pynnacle/actions/workflows/tests.yml
[wiki]: https://github.com/Stephen-RA-King/pynnacle/wiki
