from py2neo import Graph, Node
from py2neo import Relationship
from passlib.hash import bcrypt
from datetime import datetime
import uuid
import os

url = os.environ.get("GRAPHENEDB_URL", "http://localhost:7474")
print (url)
graph = Graph(url + "/db/data/")
print (url)
# calendar = GregorianCalendar(graph)


class User:
    def __init__(self, username):
        self.username = username

    def find(self):
        # user = graph.node_selector.select("User", "username", self.username)
        return graph.evaluate("match (u:User) where u.username={x} return u", x=self.username)

    def register(self, password):
        if not self.find():
            user = Node("User", username=self.username, password=bcrypt.encrypt(password))
            graph.create(user)
            return True

        return False

    def verify_password(self, password):
        user = self.find()
        if not user:
            return False

        return bcrypt.verify(password, user["password"])

    def add_post(self, title, tags, text):
        user = self.find()
        today = datetime.now()

        post = Node(
            "Post",
            id=str(uuid.uuid4()),
            title=title,
            text=text,
            timestamp=int(today.strftime("%s")),
            date=today.strftime("%F"),
        )

        graph.create(Relationship(user, "PUBLISHED", post))

        # today_node = calendar.date(today.year, today.month, today.day).day
        # graph.create(Relationship(post, "ON", today_node))

        tags = [x.strip() for x in tags.lower().split(",")]
        tags = set(tags)
        for tag in tags:
            t = Node("Tag", name=tag)
            graph.merge(t)
            rel = Relationship(t, "TAGGED", post)
            graph.create(rel)

    def like_post(self, post_id):
        user = self.find()
        post = graph.evaluate("match (p:Post) where p.id={x} return p", x=post_id)
        graph.create(Relationship(user, "LIKES", post))

    def recent_posts(self, n):
        query = """
        MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
        WHERE user.username = {username}
        RETURN post, COLLECT(tag) AS tags
        ORDER BY post.timestamp DESC LIMIT {n}    
        """
        return graph.run(query, username=self.username, n=n)

    def similar_users(self, n):
        query = """
        MATCH (user1:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
              (user2:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
        WHERE user1.username = {username} AND user1 <> user2
        WITH user2, COLLECT(DISTINCT tag.name) as tags, count(distinct tag.name) as tag_count
        ORDER BY tag_count DESC LIMIT {n}
        return user2.username as similar_user, tags    
        """
        return graph.run(query, username=self.username, n=n)

    def commonality_of_user(self, user):
        query1 = """
        MATCH (user1:User)-[:PUBLISHED]->(post:Post)<-[:LIKES]-(user2:User)
        WHERE user1.username = {username1} AND user2.username = {username2}
        RETURN COUNT(post) AS likes
        """

        likes = graph.evaluate(query1, username1=self.username, username2=user.username)
        likes = 0 if not likes else likes

        query2 = """
        MATCH (user1:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
              (user2:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
        WHERE user1.username = {username1} AND user2.username = {username2}
        RETURN COLLECT(DISTINCT tag.name) AS tags
        """

        tags = graph.evaluate(query2, username1=self.username, username2=user.username)
        return {"likes": likes, "tags": tags}


def todays_recent_posts(n):
    query = """
    MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
    where post.date = {today}
    return user, post, collect(tag) as tags
    """

    today = datetime.now().strftime("%F")
    return graph.run(query, today=today, n=n)
