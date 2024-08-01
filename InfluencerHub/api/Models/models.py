from datetime import datetime
from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from dataclasses import asdict

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100),nullable=False)
    role = db.Column(db.String(20),nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'role': self.role,
        }

    sponsor= db.relationship('Sponsor',back_populates='user',uselist=False)
    influencer=db.relationship('Influencer',back_populates='user',uselist=False)

class Adrequest(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    messages=db.Column(db.String(100),nullable=False)
    requirements=db.Column(db.String(256),nullable=False)
    payment_amount=db.Column(db.Float,nullable=False)
    status= db.Column(db.String(10),nullable=False)

    campaign_id=db.Column(db.Integer,db.ForeignKey('campaign.id'),nullable=False)
    influencer_id=db.Column(db.Integer,db.ForeignKey('influencer.id'),nullable=False)

    campaign = db.relationship('Campaign', back_populates='ad_requests') 
    influencer = db.relationship('Influencer', back_populates='ad_requests') 

class Sponsor(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    company_name=db.Column(db.String(100))
    industry=db.Column(db.String(100))
    budget=db.Column(db.Float)

    user = db.relationship('User',back_populates='sponsor')
    campaigns=db.relationship('Campaign',back_populates='sponsor')

    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

class Campaign(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    description=db.Column(db.Text,nullable=False)
    start_date=db.Column(db.DateTime,nullable=False)
    end_date=db.Column(db.DateTime,nullable=False)
    budget=db.Column(db.Float,nullable=False)
    visibility=db.Column(db.String(10),nullable=False)
    goals=db.Column(db.String(100),nullable=False)

    sponsor_id=db.Column(db.Integer,db.ForeignKey('sponsor.id'),nullable=False)

    ad_requests = db.relationship('Adrequest', back_populates='campaign')
    sponsor=db.relationship('Sponsor',back_populates='campaigns',lazy='select')

class Influencer(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    category=db.Column(db.String(100))
    niche=db.Column(db.String(100))
    reach=db.Column(db.Float)

    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    user = db.relationship('User',back_populates='influencer')
    ad_requests = db.relationship('Adrequest', back_populates='influencer')

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        password_hash=generate_password_hash('admin')
        admin=User(username='admin', password=password_hash, email='admin@example.com', name='Admin', role='admin')
        db.session.add(admin)
        db.session.commit()