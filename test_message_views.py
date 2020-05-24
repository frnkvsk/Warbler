"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()
        
    def tearDown(self):
        db.session.rollback()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
            """Test POST"""
            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
            """Test GET"""
            resp = c.get("/messages/new")
            html = resp.get_data(as_text=True)
            # Make sure it renders template messages/new.html
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<button class="btn btn-outline-success btn-block">Add my message!</button>', html)
    
    def test_messages_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            """Get testuser"""
            user = db.session.query(User).first()
            """Add a test message"""
            message = Message(text="TestMessage1")
            user.messages.append(message)
            db.session.commit()
            """Test GET"""
            resp = c.get(f"/messages/{message.id}")
            html = resp.get_data(as_text=True)
            """Make sure it renders template messages/show.html which includes the test message"""
            self.assertEqual(resp.status_code, 200)
            self.assertIn('TestMessage1', html)
            
    def test_message_destroy(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            """Get testuser"""
            user = db.session.query(User).first()
            """Add a test message"""
            message = Message(text="TestMessage1")
            user.messages.append(message)
            db.session.commit()
            """Get count of messages in Message db"""
            before = db.session.query(Message).count()
            """Test POST"""
            resp = c.post(f"/messages/{message.id}/delete")
            
            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            """Get count of messages in Message db"""
            after = db.session.query(Message).count()
            """Test if message was deleted"""
            self.assertEqual(before - 1, after)
            
    def test_do_like(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            """Get testuser"""
            user = db.session.query(User).first()
            """Add a test message"""
            message = Message(text="TestMessage1")
            user.messages.append(message)
            db.session.commit()
            """Get count of likes in Likes db"""
            before = db.session.query(Likes).count()
            """Test POST"""
            resp = c.post("/do_like", data = {"message_id":f"{message.id}"})
            """Get count of likes in Likes db"""
            after = db.session.query(Likes).count()
            """Test if like was added"""
            self.assertEqual(before + 1, after)
            """Now test the unlike toggle feature"""
            before = db.session.query(Likes).count()
            resp = c.post("/do_like", data = {"message_id":f"{message.id}"})
            after = db.session.query(Likes).count()
            self.assertEqual(before - 1, after)
            