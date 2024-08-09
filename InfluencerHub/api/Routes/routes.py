from flask import Flask,session,render_template, request, redirect, url_for, flash, make_response, jsonify
from app import app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import date,timedelta
from ..Models.models import User,db, Sponsor, Influencer,Campaign, Adrequest
import os
import uuid
import pathlib

@app.route('/login',methods=['POST'])
def login():
    if request.method=='POST':
        data=request.get_json()
        if data.get('email'):
            email=data.get('email')
            password=data.get('password')
            user=User.query.filter_by(email=email).first()
        if data.get('username'):
            username=data.get('username')
            password=data.get('password')
            user=User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):
            session['user_id']=user.id
            print(session['user_id'])
            return jsonify({'message':"Login Successful","user":user.to_dict()}), 200
        else:
            return jsonify({'message':"Invalid Credentials"}), 401
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        allowed_formats = {'png', 'tiff', 'jpg', 'jpeg'}

        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({'message': "Username already taken"}), 401
        print("UPLOAD_FOLDER_PPIC:", os.getenv('UPLOAD_FOLDER_PPIC'))
        try:
            if role == 'influencer':
                category = request.form.get('category')
                name = request.form.get('name')
                profile_name = request.form.get('profile_name')
                niche = request.form.get('niche', '[]')
                niche_list = ','.join(eval(niche)) if isinstance(niche, str) else niche

                # Access file from request.files
                temp = request.files.get('profile_pic')

                if temp:
                    # print(temp)
                    filename = secure_filename(temp.filename)
                    if "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_formats:
                        unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
                        # print(unique_filename)
                        profile_fin = os.path.join(app.config['UPLOAD_FOLDER_PPIC'], unique_filename)
                        os.makedirs(app.config['UPLOAD_FOLDER_PPIC'], exist_ok=True)
                        temp.save(profile_fin)
                        new_user = User(username=username, name=name, email=email, password=generate_password_hash(password), role=role)
                        new_influencer = Influencer(category=category, niche=niche_list, reach=0, user=new_user, name=profile_name, profile_pic=profile_fin)
                        print(temp, filename, unique_filename, profile_fin)
                        db.session.add(new_influencer)
                        db.session.add(new_user)
                        db.session.commit()
                        session['user_id'] = new_user.id
                        return jsonify({'message': "Register Successful", "user": new_user.to_dict()}), 200
                    else:
                        return jsonify({'message': 'Invalid file format. Please use PNG, TIFF, JPG, or JPEG.'}), 400
                else:
                    return jsonify({'message': 'Profile picture is required for influencers.'}), 400
            else:
                companyname = request.form.get('companyname')
                industry = request.form.get('industry')
                budget = request.form.get('budget')
                new_user = User(username=username, name=companyname, email=email, password=generate_password_hash(password), role=role)
                new_sponsor = Sponsor(company_name=companyname, industry=industry, budget=budget, user=new_user)
                db.session.add(new_sponsor)
                db.session.add(new_user)
                db.session.commit()
                session['user_id'] = new_user.id
                return jsonify({'message': "Register Successful", "user": new_user.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            print("Error during registration:", e)
            return jsonify({'message': "Registration failed due to server error."}), 500


@app.route('/users',methods=['GET','POST'])
def manage_user():
    if request.method=='POST':
        data=request.get_json()
        new_user=User(username=data['username'],password=data['password'],email=data['email'],name=data['name'],role=data['role'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()),201
    user=User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/',methods=['GET'])
def Home():
    return "hi"


def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner


def admin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please Login')
            return redirect(url_for('login'))
        user=User.query.get(session['user_id'])
        if not user.role =='admin':
            flash("Please login as administrator")
            return redirect(url_for('Home'))
        return func(*args,**kwargs)
    return inner

@auth_required
@app.route('/users/<string:username>', methods=['GET', 'PUT', 'DELETE'])
def handle_user(username):
    user = User.query.filter_by(username=username).first_or_404()

    if request.method == 'GET':
        # Initialize user data
        user_data = user.to_dict()

        # Include role-specific details in the response
        if user.role == 'influencer':
            influencer = Influencer.query.filter_by(user_id=user.id).first()
            if influencer:
                user_data.update({
                    'category': influencer.category,
                    'niche': influencer.niche,
                    'reach': influencer.reach,
                    'profile_pic': influencer.profile_pic.replace("\\","/")
                })
        elif user.role == 'sponsor':
            sponsor = Sponsor.query.filter_by(user_id=user.id).first()
            if sponsor:
                user_data.update({
                    'company_name': sponsor.company_name,
                    'industry': sponsor.industry,
                    'budget': sponsor.budget
                })
        
        return jsonify(user_data), 200

    elif request.method == 'PUT':
        data = request.get_json()

        # Update user details
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)

        if 'password' in data and data['password']:
            user.password = generate_password_hash(data['password'])

        user.name = data.get('name', user.name)

        # Handle role-specific updates if necessary
        if user.role == 'influencer':
            influencer = Influencer.query.filter_by(user_id=user.id).first()
            if influencer:
                influencer.category = data.get('category', influencer.category)
                influencer.niche = data.get('niche', influencer.niche)
                influencer.reach = data.get('reach', influencer.reach)
        elif user.role == 'sponsor':
            sponsor = Sponsor.query.filter_by(user_id=user.id).first()
            if sponsor:
                sponsor.industry = data.get('industry', sponsor.industry)
                sponsor.budget = data.get('budget', sponsor.budget)

        db.session.commit()

        # Return updated user details as JSON
        return jsonify(user.to_dict()), 200

    elif request.method == 'DELETE':
        # Delete the user
        db.session.delete(user)
        db.session.commit()

        # Return a successful response
        return '', 204

@auth_required
@app.route("/add_campaign/<string:username>", methods=['POST'])
def add_campaign(username):
    temp=request.files.get("campaign_img")
    user = User.query.filter_by(username=username).first()
    if user.role == 'sponsor':
        print("Request form data:", request.form.to_dict()) 
        data = request.form.to_dict()
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        sponsor_budget = sponsor.budget
        allowed_formats = {'png', 'tiff', 'jpg', 'jpeg'}

        if float(data.get('budget')) > sponsor_budget:
            return jsonify({'message': 'Insufficient Budget'}), 400
        else:
            if temp:
                filename = secure_filename(temp.filename)
            
                if "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_formats:
                    unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
                    campaign_fin = os.path.join(app.config['UPLOAD_FOLDER_PPIC'], unique_filename)
                    os.makedirs(app.config['UPLOAD_FOLDER_PPIC'], exist_ok=True)
                    temp.save(campaign_fin)
                    print(campaign_fin)
                    new_campaign = Campaign(
                        name=data['name'],
                        description=data['description'],
                        budget=data['budget'],
                        sponsor=sponsor,
                        visibility=data['visibility'],
                        goals=data['goals'],
                        niche=data['niche'],
                        start_date=date.today(),
                        end_date=date.today() + timedelta(days=int(data['duration'])),
                        campaign_pic=campaign_fin
                    )
                    db.session.add(new_campaign)
                    db.session.commit()
                    return jsonify({'message': 'Successfull',"campaign":new_campaign.name}), 201
                else:
                    return jsonify({'message': 'Invalid file format. Please use PNG, TIFF, JPG, or JPEG.'}), 400
            else:
                new_campaign = Campaign(
                    name=data['name'],
                    description=data['description'],
                    budget=data['budget'],
                    sponsor=sponsor,
                    visibility=data['visibility'],
                    goals=data['goals'],
                    niche=data['niche'],
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=int(data['duration']))
                )
                db.session.add(new_campaign)
                db.session.commit()
                return jsonify({'message': 'Successfull',"campaign":new_campaign.name}), 201
    else:
        return jsonify({'message': 'Unauthorized role'}), 403


@auth_required
@app.route("/campaign/<string:username>", methods=['GET'])
def get_campaigns(username):
    user = User.query.filter_by(username=username).first()
    if user.role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        campaigns = Campaign.query.filter_by(sponsor=sponsor).all()
        return jsonify([campaign.to_dic() for campaign in campaigns]), 200
    else:
        return jsonify({'message': 'Unauthorized role'}), 403