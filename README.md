djaodjin-chat is a Django application that implements the logic to support
web page chat between customers and representatives.

Major Features:

- Realtime chat.


Development
===========

After cloning the repository, create a virtualenv environment and install
the prerequisites:

    $ virtualenv-2.7 _installTop_
    $ source _installTop_/bin/activate
    $ pip install -r testsite/requirements.txt

It remains to create the database and populate it with test data.

    $ python ./manage.py migrate --run-syncdb --noinput
    $ python ./manage.py loaddata testsite/fixtures/test_data.json

If all is well then, you are ready to run the server and browse the testsite.

    $ python manage.py runserver

    # Browse http://localhost:8000/
    # Login with username: donny and password: yoyo


Implementation Notes
--------------------

The latest versions of django-restframework (>=3.0) implement paginators
disconnected from parameters in  views (i.e. no more paginate_by). You will
thus need to define ``PAGE_SIZE`` in your settings.py

    $ diff testsite/settings.py
    +REST_FRAMEWORK = {
    +    'PAGE_SIZE': 25,
    +}
