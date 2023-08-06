django-opposable-thumbs
====

Tested on Django 2.1 and Python 3.5.

Example settings:

```
OPPOSABLE_THUMBS = {
    'CACHE_DIR': os.path.join(BASE_DIR, 'path/to/folder/'),
    'ALLOWED_SOURCES': [
        'http://example.com/static/one/',
        'http://example.com/static/two/',
        'http://somwehereelse.com/',
    ]
}
```
