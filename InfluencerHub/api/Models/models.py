from datetime import datetime
from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from dataclasses import asdict

db = SQLAlchemy(app)
migrate = Migrate(app, db)

campaign_influencer=db.Table(
    'campaign_influencer',
    db.Column('campaign_id',db.Integer, db.ForeignKey('campaign.id'),primary_key=True),
    db.Column('influencer_id',db.Integer, db.ForeignKey('influencer.id'),primary_key=True)
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    flagged = db.Column(db.Boolean, default=False)
    profile_pic = db.Column(db.String(100),nullable=True)
    flag_reason = db.Column(db.String(255), nullable=True)  

    sponsor = db.relationship('Sponsor', back_populates='user', uselist=False)
    influencer = db.relationship('Influencer', back_populates='user', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'flagged': self.flagged,
            'flag_reason': self.flag_reason,
            'profile_pic': self.profile_pic
        }

class Adrequest(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    messages=db.Column(db.String(100),nullable=False)
    requirements=db.Column(db.String(256),nullable=False)
    payment_amount=db.Column(db.Float,nullable=False)
    status= db.Column(db.String(10),nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'messages': self.messages,
            'requirements': self.requirements,
            'payment_amount': self.payment_amount,
            'status': self.status,
            'campaign_id': self.campaign_id,
            'influencer_id': self.influencer_id
        }

    campaign_id=db.Column(db.Integer,db.ForeignKey('campaign.id'),nullable=False)
    influencer_id=db.Column(db.Integer,db.ForeignKey('influencer.id'),nullable=False)

    campaign = db.relationship('Campaign', back_populates='ad_requests') 
    influencer = db.relationship('Influencer', back_populates='ad_requests') 

class Sponsor(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    company_name=db.Column(db.String(100))
    industry=db.Column(db.String(100))
    budget=db.Column(db.Float)
    niche = db.Column(db.String(100))
    is_approved = db.Column(db.Boolean, default=False)
    
    def to_dic(self):
        return {
            "id":self.id,
            "company_name":self.company_name,
            "industry":self.industry,
            "budget":self.budget,
            "niche":self.niche,
        }

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
    campaign_pic = db.Column(db.String(100),nullable=True)
    niche = db.Column(db.String(100))
    flagged = db.Column(db.Boolean, default=False)
    def to_dic(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'budget': self.budget,
            'visibility': self.visibility,
            'goals': self.goals,
            'campaign_pic': self.campaign_pic,
            'niche' : self.niche,
            'flagged':self.flagged,
            'company_name': self.sponsor.company_name if self.sponsor else None 
        }

    sponsor_id=db.Column(db.Integer,db.ForeignKey('sponsor.id'),nullable=False)

    ad_requests = db.relationship('Adrequest', back_populates='campaign')
    sponsor=db.relationship('Sponsor',back_populates='campaigns',lazy='select')

    influencers = db.relationship('Influencer',secondary=campaign_influencer, back_populates = 'campaigns')

class Influencer(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    category=db.Column(db.String(100))
    niche=db.Column(db.String(100))
    reach=db.Column(db.Float)
    def to_dic(self):
        return {
            "id":self.id,
            "name":self.name,
            "category":self.category,
            "niche":self.niche,
            "reach":self.reach,
        }
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    user = db.relationship('User',back_populates='influencer')
    ad_requests = db.relationship('Adrequest', back_populates='influencer')

    campaigns = db.relationship('Campaign',secondary = campaign_influencer, back_populates='influencers')


with app.app_context():
    db.create_all()
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        password_hash=generate_password_hash('admin')
        admin=User(username='admin', password=password_hash, email='admin@example.com', name='Admin', role='admin')
        db.session.add(admin)
        db.session.commit()