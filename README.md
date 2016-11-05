# Wagtail SendInBlue

[Wagtail](https://wagtail.io/) integration for [SendInblue][].

## Installation

Install it with pip:

```shell
pip install wagtail-sendinblue
```

Add `sendinblue` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'sendinblue',
    # ...
]
```

Add the `sendinblue.urls` to your `urls.py`:

```python
from sendinblue import urls as sendinblue_urls

urlpatterns = [
    # ...
    url(r'', include(sendinblue_urls)),
    url(r'', include(wagtail_urls)),
]
```

## Configuration

Go to the Wagtail administration and in `Settings > SendInBlue`
enter your API Key.
You need a [SendInBlue][] account and
you can retrieve it your [SendInBlue administration](https://account.sendinblue.com/advanced/api?ae=312).

## Automation support

There is an optionnal support for Automation.

You need to add the following at the end of your base Django template:

```html+jinja
  {% sendinblue %}
</body>
</html>
```

or if using [django-jinja](http://niwinz.github.io/django-jinja/):

```html+jinja
  {{ sendinblue() }}
</body>
</html>
```


[SendInBlue]: https://www.sendinblue.com/?ae=312
