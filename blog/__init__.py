from .views import app
from .models import graph

graph.run("CREATE CONSTRAINT on (n:User) ASSERT n.username IS UNIQUE")
graph.run("CREATE CONSTRAINT on (n:Post) ASSERT n.id IS UNIQUE")
graph.run("CREATE CONSTRAINT on (n:Tag) ASSERT n.name IS UNIQUE")
graph.run("CREATE INDEX on :Post(date)")
