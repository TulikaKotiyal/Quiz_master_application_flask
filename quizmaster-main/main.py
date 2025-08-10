from flask import Flask
from flask_login import LoginManager
from config import Config
from database import db, User
from routes import main_bp, auth_bp, admin_bp, user_bp
from werkzeug.security import generate_password_hash
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Set the login view

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')

# Create database tables and add admin user (if not exists)
with app.app_context():
    db.create_all()

    # Check if admin user exists, if not create one
    admin = User.query.filter_by(email='tulikakotiyal2004@gmail.com').first()  # Use 'email' to check for admin
    if not admin:
        admin = User(
            username='Tulika Kotiyal',  # Set the admin username
            email='tulikakotiyal2004@gmail.com',  # Set the admin email
            password=generate_password_hash('admin_Tulika123'),  # Set the admin password (hash it)
            full_name='Tulika Kotiyal',
            qualification='System Administrator',
            dob=datetime.strptime('2004-07-26', '%Y-%m-%d').date(),  # Convert to date object
            is_admin=True  # Mark this user as an admin
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created!')

if __name__ == '__main__':
    app.run(debug=True)