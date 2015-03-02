# Polls API

[![Apiary Documentation](https://img.shields.io/badge/Apiary-Documented-blue.svg)](http://docs.pollsapi.apiary.io/)
[![Circle CI Status](https://img.shields.io/circleci/project/apiaryio/polls-api.svg)](https://circleci.com/gh/apiaryio/polls-api/tree/master)

This is a Python implementation of a Polls API, an API that allows consumers to
view polls and vote in them. Take a look at the
[API Documentation](http://docs.pollsapi.apiary.io/). We've
deployed an instance of this [API](https://pollsapi.herokuapp.com) for testing.

## Deploying on Heroku

Click the button below to automatically set up the Polls API in an app
running on your Heroku account.

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/apiaryio/polls-api)

Once you've deployed, you can easily clone the application and alter the
configuration to disable features:

```bash
$ heroku clone -a new-app-name
$ heroku config:set POLLS_CAN_VOTE_QUESTION=false
$ heroku config:set POLLS_CAN_CREATE_QUESTION=false
$ heroku config:set POLLS_CAN_DELETE_QUESTION=false
```

## Development Environment

You can configure a development environment with the following:

```bash
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python manage.py migrate
```

### Running the tests

```bash
$ python manage.py test
```

### Running the development server

```bash
$ python manage.py runserver
```

## License

polls-api is released under the MIT license. See [LICENSE](LICENSE).

