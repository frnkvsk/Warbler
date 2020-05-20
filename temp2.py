
class Follows(db.Model):
    """Connection of a follower <-> followed_user."""
    __tablename__ = 'follows'
    user_being_followed_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True)
    user_following_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True)

class Likes(db.Model):
    """Mapping user likes to warbles."""
    __tablename__ = 'likes' 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id', ondelete='cascade'), unique=True)

class User(db.Model):
    """User in the system."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, default="/static/images/default-pic.png")
    header_image_url = db.Column(db.Text, default="/static/images/warbler-hero.jpg")
    bio = db.Column(db.Text)
    location = db.Column(db.Text)    
    
    messages = db.relationship('Message')
    followers = db.relationship("User", secondary="follows", primaryjoin=(Follows.user_being_followed_id == id), 
                                secondaryjoin=(Follows.user_following_id == id))
    following = db.relationship("User", secondary="follows", primaryjoin=(Follows.user_following_id == id), 
                                secondaryjoin=(Follows.user_being_followed_id == id))
    likes = db.relationship('Message', secondary="likes")    

class Message(db.Model):
    """An individual message ("warble")."""
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(140), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    user = db.relationship('User')

