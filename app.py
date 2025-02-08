from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__, 
    static_url_path='',
    static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tweets.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

UPLOAD_FOLDER = 'static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_picture(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to filename to make it unique
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return None

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.String(200))
    profile_picture = db.Column(db.String(200), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tweets = db.relationship('Tweet', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(280), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Like', backref='tweet', lazy=True)

    def is_liked_by(self, user):
        like = Like.query.filter_by(user_id=user.id, tweet_id=self.id).first()
        if like is not None:
            return True
        else:
            return False

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'tweet_id'),)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/write', methods=['GET', 'POST'])
@login_required
def write_tweet():
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            tweet = Tweet(content=content, user_id=current_user.id)
            db.session.add(tweet)
            db.session.commit()
            flash('Tweet posted successfully!')
            return redirect(url_for('feed'))
    return render_template('write_tweet.html')

@app.route('/feed')
@login_required
def feed():
    # Get all tweets from all users, ordered by timestamp
    all_tweets = Tweet.query.order_by(Tweet.timestamp.desc()).all()
    # For each tweet, we'll also pass the username of the author
    tweets_with_authors = []
    for tweet in all_tweets:
        like_status = Like.query.filter_by(user_id=current_user.id, tweet_id=tweet.id).first() is not None
        tweets_with_authors.append({
            'id': tweet.id,
            'content': tweet.content,
            'timestamp': tweet.timestamp,
            'author': tweet.author.username,
            'is_own_tweet': tweet.author.id == current_user.id,
            'likes': len(tweet.likes),
            'is_liked_by': like_status
        })
    return render_template('feed.html', tweets=tweets_with_authors)

@app.route('/profile')
@app.route('/profile/<username>')
@login_required
def profile(username=None):
    if username is None:
        user = current_user
    else:
        user = User.query.filter_by(username=username).first_or_404()
    
    user_tweets = Tweet.query.filter_by(user_id=user.id)\
        .order_by(Tweet.timestamp.desc()).all()
    return render_template('profile.html', user=user, tweets=user_tweets)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        bio = request.form.get('bio', '')
        
        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file.filename != '':
                filename = save_profile_picture(file)
                if filename:
                    # Delete old profile picture if it exists and is not the default
                    if current_user.profile_picture != 'default.jpg':
                        old_file = os.path.join(app.config['UPLOAD_FOLDER'], current_user.profile_picture)
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    current_user.profile_picture = filename

        current_user.bio = bio
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', user=current_user)

@app.route('/tweet/<int:tweet_id>/like', methods=['POST'])
@login_required
def like_tweet(tweet_id):
    tweet = Tweet.query.get_or_404(tweet_id)
    like = Like.query.filter_by(user_id=current_user.id, tweet_id=tweet_id).first()
    
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'status': 'unliked', 'likes': len(tweet.likes)})
    
    like = Like(user_id=current_user.id, tweet_id=tweet_id)
    db.session.add(like)
    db.session.commit()
    return jsonify({'status': 'liked', 'likes': len(tweet.likes)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
