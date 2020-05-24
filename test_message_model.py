"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
    
    def test_message_model(self):
        """Create a user with a message to test"""
        hashed_pwd1 = bcrypt.generate_password_hash("HASHED_PASSWORD1").decode('UTF-8')
        user1 = User(email="test1@test.com", username="testuser1", password=hashed_pwd1)
        db.session.add(user1)
        db.session.commit()
        message1 = Message(text="TestMessage", user_id=user1.id)
        db.session.add(message1)
        db.session.commit()
        """Test get_message_by_id"""
        testmessage = Message.get_message_by_id(message1.id)
        self.assertEqual(user1.id, testmessage.user_id)
        
        """Test get_filtered_messages"""
        filtered_List = [user1.id]
        testmessage = Message.get_filtered_messages(filtered_List)
        self.assertEqual(user1.id, testmessage[0].user_id)
        
        """Test get_liked_messages"""
        hashed_pwd2 = bcrypt.generate_password_hash("HASHED_PASSWORD2").decode('UTF-8')
        user2 = User(email="test2@test.com", username="testuser2", password=hashed_pwd2)
        db.session.add(user1)
        db.session.commit()
        user2.likes.append(message1.id)
        liked = [message1.id]
        testmessage = Message.get_liked_messages(liked)
        self.assertEqual(message1.id, testmessage[0].id)
        
        """Test delete_message"""
        before = db.session.query(Message).count()
        Message.delete_message(message1.id)
        after = db.session.query(Message).count()
        self.assertEqual(before - 1, after)