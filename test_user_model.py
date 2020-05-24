"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""
        hashed_pwd1 = bcrypt.generate_password_hash("HASHED_PASSWORD1").decode('UTF-8')
        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password=hashed_pwd1
        )
        db.session.add(user1)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(user1.messages), 0)
        self.assertEqual(len(user1.followers), 0)
        """Test repr"""
        self.assertEqual("test1@test.com", user1.__repr__.__self__.email)
        
        hashed_pwd2 = bcrypt.generate_password_hash("HASHED_PASSWORD2").decode('UTF-8')
        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password=hashed_pwd2
        )
        
        
        """Test following functionality"""
        
        """Test user1 is followed by user2"""
        user1.followers.append(user2)
        self.assertTrue(user1.is_followed_by(user2))
        
        """Test user1 is following user2"""
        user1.following.append(user2)
        self.assertTrue(user1.is_following(user2))
        
        """Test User.signup functionality"""
        
        """Test successful signup"""
        user3 = User.signup(username="user3", email="test3@test.com", password="HASHED_PASSWORD3", image_url=None)
        self.assertEqual("user3", user3.username)
        
        """Test unsuccessful signup"""
        user4 = User.signup(username="", email="test4@test.com", password="HASHED_PASSWORD4", image_url=None)
        user4 = db.session.query(User).filter_by(username='').first()
        self.assertEqual(None, user4)
        
        print("USER1.PASSWORD => ",user1.password)
        
        """Test authenticate functionality"""
        
        """Test successful authenticate"""
        auth1 = User.authenticate("testuser1", "HASHED_PASSWORD1")
        self.assertEqual(auth1, user1)
        auth2 = User.authenticate("testuser3", "HASHED_PASSWORD3")
        self.assertEqual(auth1, user1)
        """Test unsuccessful authenticate"""
        auth3 = User.authenticate("testuser1", "HASHED_PASSWORD2")
        self.assertFalse(auth3)
        print(db.session.query(User).all())
        # Does the repr method work as expected?
        # Does is_following successfully detect when user1 is following user2?
        # Does is_following successfully detect when user1 is not following user2?
        # Does is_followed_by successfully detect when user1 is followed by user2?
        # Does is_followed_by successfully detect when user1 is not followed by user2?
        # Does User.create successfully create a new user given valid credentials?
        # Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?
        # Does User.authenticate successfully return a user when given a valid username and password?
        # Does User.authenticate fail to return a user when the username is invalid?
        # Does User.authenticate fail to return a user when the password is invalid?