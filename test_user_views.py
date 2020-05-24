"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase
# from flask import g
from models import db, connect_db, Message, User, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY, g

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        tempuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()
        self.testuser = db.session.query(User).filter_by(username="testuser").first()
        
    def tearDown(self):
        db.session.rollback()
        
    def test_add_user_to_g(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            """Test before request"""
            resp = c.get("/")
            self.assertEqual(self.testuser.id, g.user.id)
            
    def test_signup(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            """Test if user in setUp was successfully inserted int User db"""
            user = db.session.query(User).first()
            self.assertEqual("testuser", user.username)
            self.assertEqual("test@test.com", user.email)
            
    def test_logout_login(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            """Test user logout"""
            resp = c.get("/logout")  
            """Make sure it redirects"""
            self.assertEqual(resp.status_code, 302)
            """Follow redirect"""
            resp = c.get("/logout", follow_redirects=True)   
            self.assertEqual(resp.status_code, 200) 
            """Test redirected page"""    
            html = resp.get_data(as_text=True)            
            self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)
            """Test if user is logged out"""
            self.assertEqual(None, g.user)
            
            """Log user in"""
            resp = c.post("/login", data={"username": "testuser", "password": "testuser"}, follow_redirects=True) 
            self.assertEqual(resp.status_code, 200) 
            """Test redirected page"""    
            html = resp.get_data(as_text=True)            
            self.assertIn('<aside class="col-md-4 col-lg-3 col-sm-12" id="home-aside">', html)
            
    def test_list_users(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get("/users", data={"q":"sam"})
            self.assertEqual(resp.status_code, 200) 
            html = resp.get_data(as_text=True)            
            self.assertIn('<p class="card-bio">BIO HERE</p>', html)
            
    def test_users_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            resp = c.get(f"/users/{self.testuser.id}")
            self.assertEqual(resp.status_code, 200) 
            html = resp.get_data(as_text=True)            
            self.assertIn('<ul class="list-group" id="messages">', html)
    
    def test_show_following(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            """Create user to follow self.testuser"""
            User.signup(username="follow",
                                    email="follow@test.com",
                                    password="follow",
                                    image_url=None)
            db.session.commit()
            user = db.session.query(User).filter_by(username="follow").first()
            
            user.following.append(self.testuser)
            db.session.commit()   
            
            resp = c.get(f"/users/{user.id}/following")
            self.assertEqual(resp.status_code, 200) 
            html = resp.get_data(as_text=True)            
            self.assertIn('<div class="col-lg-4 col-md-6 col-12">', html) 
            
    def test_users_followers(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            """Create user that follows self.testuser"""
            User.signup(username="follows",
                                    email="follows@test.com",
                                    password="follow",
                                    image_url=None)
            db.session.commit()
            user = db.session.query(User).filter_by(username="follows").first()
            
            user.followers.append(self.testuser)
            db.session.commit()   
            
            resp = c.get(f"/users/{user.id}/followers")
            self.assertEqual(resp.status_code, 200) 
            html = resp.get_data(as_text=True)            
            self.assertIn('<div class="col-lg-4 col-md-6 col-12">', html) 
            
    def test_add_follow(self): 
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            """Create user to follow"""
            User.signup(username="follow",
                                    email="follow@test.com",
                                    password="follow",
                                    image_url=None)
            db.session.commit()
            user = db.session.query(User).filter_by(username="follow").first()
            
            resp = c.post(f"/users/follow/{user.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200) 
            html = resp.get_data(as_text=True)            
            self.assertIn('<div class="col-lg-4 col-md-6 col-12">', html)
    
    def test_stop_following(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            """Create user to follow"""
            User.signup(username="follow",
                                    email="follow@test.com",
                                    password="follow",
                                    image_url=None)
            db.session.commit()
            user = db.session.query(User).filter_by(username="follow").first()
            
            """Not allowed to directly add append a follow to the current user in session so we add them indirectly through the follower"""
            user.followers.append(self.testuser)
            db.session.commit()   
            before = len(self.testuser.following)
            resp = c.post(f"/users/stop-following/{user.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            newuser = db.session.query(User).filter_by(id=self.testuser.id).first()
            after = len(newuser.following)        
            self.assertEqual(before -1, after)
            
    def test_show_likes(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            """Create user and message to like"""
            tempuser = User.signup(username="like",
                                    email="like@test.com",
                                    password="likelike",
                                    image_url=None)
            db.session.add(tempuser)
            db.session.commit()
            user = db.session.query(User).filter_by(username="like").first()
            message = Message(text="Testmessage",user_id=user.id)
            db.session.add(message)
            db.session.commit()
            testmessage = db.session.query(Message).first()
            user = db.session.query(User).filter_by(username="like").first()
            templike = Likes(user_id=self.testuser.id, message_id=testmessage.id)
            db.session.add(templike)
            db.session.commit()
            testuser = db.session.query(User).filter_by(username='testuser').first()
            self.assertEqual(testuser.likes[0].id, message.id)
            resp = c.get(f"/users/{self.testuser.id}/likes")
            self.assertEqual(resp.status_code, 200) 
            html = resp.get_data(as_text=True)            
            self.assertIn('<div class="message-area">', html)
            
    def test_profile(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id                
            
            d = {"password":"testuser", "email":"test@test.com", "image_url":None, "header_image_url":None, "bio":None, "location":"Earth"} 
            
            resp = c.post("users/profile", data=d, follow_redirects=True)
            self.assertEqual(resp.status_code, 200) 
            html = resp.get_data(as_text=True)            
            self.assertIn('<aside class="col-md-4 col-lg-3 col-sm-12" id="home-aside">', html)
            testuser = db.session.query(User).filter_by(id=g.user.id).first()
            self.assertEqual("Earth", testuser.location)
            
    def test_changepw(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id   
                
            d = {"oldPassword":"testuser", "newPassword1":"newtestuserpw", "newPassword2":"newtestuserpw"}
            resp = c.post("/users/changepw", data=d, follow_redirects=True)
            self.assertEqual(resp.status_code, 200) 
            html = resp.get_data(as_text=True)            
            self.assertIn('<aside class="col-md-4 col-lg-3 col-sm-12" id="home-aside">', html)
            testuser = db.session.query(User).filter_by(id=g.user.id).first()
            
            """Test if password is changed"""
            auth = User.authenticate("testuser", "newtestuserpw")
            self.assertTrue(auth)
     
    def test_delete_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id    
            
            testid = self.testuser.id
            resp = c.post("/users/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200) 
            html = resp.get_data(as_text=True) 
            """Test if redirected to the signup page"""           
            self.assertIn('<h2 class="join-message">Join Warbler today.</h2>', html)            
            """Test if g.user is signed out"""
            userg = g.user
            self.assertIsNone(userg)
            """Test if user is deleted"""
            deleted = db.session.query(User).filter_by(id=testid).first()
            self.assertIsNone(deleted)