from polls.urls import router
from polls.models import database

app = database(router)

