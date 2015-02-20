import os
import tempfile
from invoke import run, task


@task
def dropdb():
    from polls.models import Question, Choice, Vote
    Vote.drop_table(True)
    Choice.drop_table(True)
    Question.drop_table(True)


@task
def syncdb():
    from polls.models import Question, Choice, Vote
    Question.create_table(True)
    Choice.create_table(True)
    Vote.create_table(True)


class Database(object):
    def __init__(self, name='tests', cleanup=True):
        self.database_path = os.path.join(tempfile.gettempdir(), '{}.sqlite'.format(name))
        self.cleanup = cleanup

    def __enter__(self):
        os.environ['DATABASE_URL'] = 'sqlite:///{}'.format(self.database_path)
        run('invoke syncdb')

    def __exit__(self, *args, **kwargs):
        if self.cleanup:
            run('invoke dropdb')

        del os.environ['DATABASE_URL']

@task
def tests():
    with Database():
        run('python -m unittest discover')

@task
def develop():
    print('Serving on http://localhost:8080')

    with Database('development', False):
        run('python -m polls')

@task
def shell():
    with Database('development', False):
        run('python')

