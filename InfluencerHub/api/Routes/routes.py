from flask import Flask,session,render_template, request, redirect, url_for, flash, make_response, jsonify
from app import app
from app import cache
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from sqlalchemy.orm import joinedload
from datetime import date,timedelta, datetime
from ..Models.models import User,db, Sponsor, Influencer,Campaign, Adrequest
from celery_app import celery
from flask_jwt_extended import JWTManager, create_access_token,jwt_required,get_jwt_identity
import os
import uuid
import pathlib
import json
import re

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()

        # If both email and username are missing, immediately return an error
        if not data.get('email') and not data.get('username'):
            return jsonify({'message': 'Email or Username required'}), 400

        # Handle login by email
        if data.get('email'):
            email = data.get('email')
            password = data.get('password')
            user = User.query.filter_by(email=email).first()

        # Handle login by username
        if data.get('username'):
            username = data.get('username')
            password = data.get('password')
            user = User.query.filter_by(username=username).first()

        # If user exists and password matches
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            access_token = create_access_token(identity=user.id, additional_claims={'role': user.role, 'username': user.username})

            
            if user.role == 'sponsor':
                sponsor = Sponsor.query.filter_by(user_id=user.id).first()
                if sponsor and sponsor.is_approved:
                    return jsonify({'message': "Login Successful", 'access_token': access_token, "user": user.to_dict()}), 200
                else:
                    return jsonify({'message': "Profile still not verified"}), 404

            # Successful login for other user roles
            return jsonify({'message': "Login Successful", 'access_token': access_token, "user": user.to_dict()}), 200

        # Invalid credentials
        return jsonify({'message': "Invalid Credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        allowed_formats = {'png', 'tiff', 'jpg', 'jpeg'}

        # Validations
        if not username:
            return jsonify({'message': "Username is required"}), 400
        if not email:
            return jsonify({'message': "Email is required"}), 400
        if not password:
            return jsonify({'message': "Password is required"}), 400
        if len(password) < 6:
            return jsonify({'message': "Password must be at least 6 characters long"}), 400
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'message': "Invalid email format"}), 400

        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({'message': "Username already taken"}), 401

        try:
            if role == 'influencer' or role == 'sponsor':
                category = request.form.get('category')
                if role == 'influencer':
                    name = request.form.get('name')
                else:
                    name = request.form.get('companyname')
                profile_name = request.form.get('profile_name')
                niche = request.form.get('niche', '[]')
                niche_list = ','.join(json.loads(niche)) if isinstance(niche, str) else niche

                # Handle optional profile picture
                temp = request.files.get('profile_pic')
                profile_fin = None  # Default to None if no file is uploaded

                if temp:
                    filename = secure_filename(temp.filename)
                    if "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_formats:
                        unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
                        profile_fin = os.path.join(app.config['UPLOAD_FOLDER_PPIC'], unique_filename).replace("\\", '/')
                        os.makedirs(app.config['UPLOAD_FOLDER_PPIC'], exist_ok=True)
                        temp.save(profile_fin)
                    else:
                        return jsonify({'message': 'Invalid file format. Please use PNG, TIFF, JPG, or JPEG.'}), 400
                
                # Create the user
                new_user = User(username=username, name=name, email=email, password=generate_password_hash(password), role=role, profile_pic=profile_fin)
                if role == 'influencer':
                    new_role_user = Influencer(category=category, niche=niche_list, reach=0, user=new_user, name=profile_name)
                else:
                    companyname = request.form.get('companyname')
                    industry = request.form.get('industry')
                    budget = request.form.get('budget')
                    new_role_user = Sponsor(company_name=companyname, industry=industry, budget=budget, user=new_user, is_approved=False)
                
                db.session.add(new_role_user)
                db.session.commit()

                session['user_id'] = new_user.id
                return jsonify({'message': "Register Successful", "user": new_user.to_dict()}), 200

            else:
                return jsonify({'message': 'Invalid role.'}), 400

        except Exception as e:
            db.session.rollback()
            print(f"Error occurred: {str(e)}")
            return jsonify({'message': f'Error occurred: {str(e)}'}), 500



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

@app.route('/users',methods=['GET','POST'])
@admin_required
@jwt_required()
def manage_user():
    if request.method=='POST':
        data=request.get_json()
        new_user=User(username=data['username'],password=data['password'],email=data['email'],name=data['name'],role=data['role'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()),201
    user=User.query.all()
    return jsonify([us.to_dict() for us in user])

@auth_required
@jwt_required()
@app.route('/users/<string:username>', methods=['GET', 'PUT', 'DELETE'])
@cache.cached(timeout=300, key_prefix=lambda: f"user_{request.view_args['username']}")
def handle_user(username):
    user = User.query.filter_by(username=username).first()
    if request.method == 'GET':
        user_data = user.to_dict()
        if user.role == 'influencer':
            influencer = Influencer.query.filter_by(user_id=user.id).first()
            if influencer:
                user_data.update({
                    'category': influencer.category,
                    'niche': influencer.niche,
                    'reach': influencer.reach,

                })
        elif user.role == 'sponsor':
            sponsor = Sponsor.query.filter_by(user_id=user.id).first()
            if sponsor:
                user_data.update({
                    'company_name': sponsor.company_name,
                    'industry': sponsor.industry,
                    'budget': sponsor.budget,
                })
        return jsonify(user_data), 200

    elif request.method == 'PUT':
        data = request.get_json()

        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)

        if 'password' in data and data['password']:
            user.password = generate_password_hash(data['password'])

        user.name = data.get('name', user.name)

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
        cache.delete(f"user_{request.view_args['username']}")
        return jsonify(user.to_dict()), 200

    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        cache.delete(f"user_{request.view_args['username']}")
        return '', 204


@app.route('/users/get_influencers', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, key_prefix='all_influencers')
def get_influencers():
    
    query = request.args.get('query', '')
    print(query)
    if query:
        influencers = User.query.filter(User.role == 'influencer', User.username.ilike(f'%{query}%')).all()
        suggestions = [influencer.username for influencer in influencers]
        print(suggestions)
        return jsonify(suggestions)
    else:
        return jsonify([])


@auth_required
@jwt_required()
@app.route("/add_campaign/<string:username>", methods=['POST'])
def add_campaign(username):
    temp = request.files.get("campaign_img")
    user = User.query.filter_by(username=username).first()

    if user.role == 'sponsor':
        data = request.form.to_dict()
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        sponsor_budget = sponsor.budget
        allowed_formats = {'png', 'tiff', 'jpg', 'jpeg'}

        # Check if campaign already exists by its name or another unique identifier
        existing_campaign = Campaign.query.filter_by(name=data['name'], sponsor_id=sponsor.id).first()

        if float(data.get('budget')) > sponsor_budget:
            return jsonify({'message': 'Insufficient Budget'}), 400

        if temp:
            filename = secure_filename(temp.filename)
            if "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_formats:
                unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
                campaign_fin = os.path.join(app.config['UPLOAD_FOLDER_PPIC'], unique_filename)
                os.makedirs(app.config['UPLOAD_FOLDER_PPIC'], exist_ok=True)
                temp.save(campaign_fin)

                if existing_campaign:
                    # Update existing campaign
                    existing_campaign.description = data['description']
                    existing_campaign.budget = data['budget']
                    existing_campaign.visibility = data['visibility']
                    existing_campaign.goals = data['goals']
                    existing_campaign.niche = data['niche']
                    existing_campaign.end_date = datetime.now() + timedelta(days=int(data['duration']))
                    existing_campaign.campaign_pic = campaign_fin

                    db.session.commit()
                    cache.delete(f"campaigns_{request.view_args['username']}")
                    cache.delete('all_campaigns')
                    cache.delete(f"stats_{request.view_args['username']}")
                    return jsonify({'message': 'Campaign Updated Successfully', 'campaign': existing_campaign.name}), 200
                else:
                    # Create a new campaign
                    new_campaign = Campaign(
                        name=data['name'],
                        description=data['description'],
                        budget=data['budget'],
                        sponsor=sponsor,
                        visibility=data['visibility'],
                        goals=data['goals'],
                        niche=data['niche'],
                        start_date=datetime.now(),
                        end_date=datetime.now() + timedelta(days=int(data['duration'])),
                        campaign_pic=campaign_fin
                    )
                    db.session.add(new_campaign)
                    db.session.commit()
                    cache.delete(f"campaigns_{request.view_args['username']}")
                    cache.delete('all_campaigns')
                    cache.delete(f"stats_{request.view_args['username']}")
                    return jsonify({'message': 'Campaign Added Successfully', 'campaign': new_campaign.name}), 201
            else:
                return jsonify({'message': 'Invalid file format. Please use PNG, TIFF, JPG, or JPEG.'}), 400
        else:
            if existing_campaign:
                existing_campaign.description = data['description']
                existing_campaign.budget = data['budget']
                existing_campaign.visibility = data['visibility']
                existing_campaign.goals = data['goals']
                existing_campaign.niche = data['niche']
                existing_campaign.end_date = datetime.now() + timedelta(days=int(data['duration']))

                db.session.commit()
                cache.delete(f"campaigns_{request.view_args['username']}")
                cache.delete('all_campaigns')
                cache.delete(f"stats_{request.view_args['username']}")
                return jsonify({'message': 'Campaign Updated Successfully', 'campaign': existing_campaign.name}), 200
            else:
                # Create a new campaign without an image
                new_campaign = Campaign(
                    name=data['name'],
                    description=data['description'],
                    budget=data['budget'],
                    sponsor=sponsor,
                    visibility=data['visibility'],
                    goals=data['goals'],
                    niche=data['niche'],
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=int(data['duration']))
                )
                db.session.add(new_campaign)
                db.session.commit()
                cache.delete(f"campaigns_{request.view_args['username']}")
                cache.delete('all_campaigns')
                cache.delete(f"stats_{request.view_args['username']}")
                return jsonify({'message': 'Campaign Added Successfully', 'campaign': new_campaign.name}), 201
    else:
        return jsonify({'message': 'Unauthorized role'}), 403

    
@admin_required
@jwt_required()
@app.route('/unapproved_sponsors', methods=['GET'])
def get_unapproved_sponsors():

    unapproved_sponsors = User.query.join(Sponsor).options(joinedload(User.sponsor)).filter(User.role == 'sponsor', Sponsor.is_approved ==  False).all()
    
    response = [sponsor.to_dict() for sponsor in unapproved_sponsors]
    
    return jsonify(response), 200
@auth_required
@jwt_required()
@app.route("/campaigns/<string:username>", methods=['GET'])
@cache.cached(timeout=300, key_prefix=lambda: f"campaigns_{request.view_args['username']}")
def get_campaigns(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    if user.role == 'sponsor':
        # Fetch campaigns for the sponsor
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
        # Return both campaign and user data (joined with influencer data)
        influencers = db.session.query(User, Influencer).join(Influencer, User.id == Influencer.user_id).all()

        influencers_data = [
            {**influencer_user.to_dict(), **influencer.to_dict()} for influencer_user, influencer in influencers
        ]

        return jsonify({
            'campaigns': [campaign.to_dic() for campaign in campaigns],
            'influencers': influencers_data,
            'username': user.username
        }), 200

    elif user.role == 'influencer':
        # Fetch campaigns for the influencer
        influencer = Influencer.query.filter_by(user_id=user.id).first()
        ad_requests = Adrequest.query.filter_by(influencer_id=influencer.id).all()
        campaign_ids = [ad_request.campaign_id for ad_request in ad_requests]
        campaigns = Campaign.query.filter(Campaign.id.in_(campaign_ids)).all()
        
        return jsonify({
            'campaigns': [campaign.to_dic() for campaign in campaigns],
            'ad_requests': [ad_request.to_dict() for ad_request in ad_requests],
            'username': user.username  # Include user data for influencers as well
        }), 200

    else:
        # Return all campaigns, influencers, and sponsors with joined user data
        campaigns = Campaign.query.all()
        influencers = db.session.query(User, Influencer).join(Influencer, User.id == Influencer.user_id).all()
        sponsors = db.session.query(User, Sponsor).join(Sponsor, User.id == Sponsor.user_id).all()

        influencers_data = [
            {**influencer_user.to_dict(), **influencer.to_dict()} for influencer_user, influencer in influencers
        ]
        sponsors_data = [
            {**sponsor_user.to_dict(), **sponsor.to_dict()} for sponsor_user, sponsor in sponsors
        ]

        return jsonify({
            'campaigns': [campaign.to_dic() for campaign in campaigns],
            'influencers': influencers_data,
            'sponsors': sponsors_data
        }), 200

@auth_required
@jwt_required()
@app.route("/campaign/<string:username>/<string:name>", methods=['GET'])
@cache.cached(timeout=300, key_prefix=lambda: f"campaigns_{request.view_args['username']}_{request.view_args['name']}")
def get_campaign(username, name):
    print(username, name)
    user = User.query.filter_by(username=name).first()
    if user and user.role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id, name=username).all()
        print(campaigns)
        return jsonify([campaign.to_dic() for campaign in campaigns]), 200
    else:
        return jsonify({'message': 'Unauthorized role or user not found'}), 403


@auth_required
@jwt_required()
@app.route("/add_adrequest/<string:username>/<int:campaign_id>", methods=['POST'])
def add_adrequest(username, campaign_id):
    print(username,campaign_id)
    user = User.query.filter_by(username=username).first()
    print(user)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.role != 'sponsor':
        return jsonify({'message': 'Unauthorized role'}), 403
    
    campaign = Campaign.query.get(campaign_id)
    print(campaign)
    if not campaign:
        return jsonify({'message': 'Campaign not found'}), 404

    data = request.get_json()
    print(data)
    if not data:
        return jsonify({'message': 'Invalid or missing JSON data'}), 400

    # Assuming 'influencer_id' is sent as part of the request
    influencer_username = data.get('influencers')
    print(influencer_username)
    if influencer_username:
        influencer_id = Influencer.query.filter_by(name=influencer_username).first().id
        new_adrequest = Adrequest(
        messages=data.get('message'),
        requirements=data.get('requirements'),
        payment_amount=data.get('payment_amount'),
        status='pending',
        campaign_id=campaign.id,
        influencer_id=influencer_id
    )
        if not influencer_id:
            return jsonify({'message': 'Influencer not selected'}), 400

    new_adrequest = Adrequest(
        messages=data.get('message'),
        requirements=data.get('requirements'),
        payment_amount=data.get('payment_amount'),
        status='pending',
        campaign_id=campaign.id,
        influencer_id=0
    )

    db.session.add(new_adrequest)
    db.session.commit()
    return jsonify({'message': 'Ad request submitted successfully'}), 201

@auth_required
@jwt_required()
@app.route("/stats/<string:username>", methods=['GET'])
@cache.cached(timeout=300, key_prefix=lambda: f"stats_{request.view_args['username']}")
def get_stats(username):
    user = User.query.filter_by(username=username).first()
    if user:
        if user.role == 'sponsor':
            sponsor = Sponsor.query.filter_by(user_id=user.id).first()
            campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all() or []
            active_campaign = 0
            inactive_campaign = 0
            used_budget = 0
            niches = []

            for campaign in campaigns:
                used_budget += campaign.budget
                if campaign.end_date > datetime.now():
                    active_campaign += 1
                else:
                    inactive_campaign += 1
                niches.append(campaign.niche)

            ad_requests = Adrequest.query.filter(Adrequest.campaign_id.in_([campaign.id for campaign in campaigns])).all()

            influencers_budget = [
                {"influencer": ad.influencer.name, "budget": ad.payment_amount}
                for ad in ad_requests if ad.influencer_id != 0 and ad.influencer is not Np
            ]

            response_data = {
                "adrequestsdata": [ad_request.to_dict() for ad_request in ad_requests],
                "campaignsdata": [campaign.to_dic() for campaign in campaigns],
                "sponsordata": sponsor.to_dict(),
                "activevsinactive": [active_campaign, inactive_campaign]
            }

            if influencers_budget:
                response_data["influencerbudget"] = influencers_budget

            return jsonify(response_data), 200

        elif user.role == 'influencer':
            influencer = Influencer.query.filter_by(user_id=user.id).first()
            ad_requests = Adrequest.query.filter_by(influencer_id=influencer.id).all() or []
            return jsonify([ad_request.to_dict() for ad_request in ad_requests]), 200

        else:
            users = User.query.all()
            campaigns = Campaign.query.all()
            ad_requests = Adrequest.query.all()
            return jsonify({
                'users': [user.to_dict() for user in users],
                'campaigns': [campaign.to_dic() for campaign in campaigns],
                'ad_requests': [ad_request.to_dict() for ad_request in ad_requests]
            }), 200
    else:
        return jsonify({"message":"Sorry the user does not exist"}),404

@auth_required
@jwt_required()
@app.route("/submit_request/<string:type>/<int:id>", methods=['POST'])
def submit_request(type, id):
    try:
        data = request.get_json()
        message = data.get('message', "")
        requirements = data.get('requirements', "")
        payment_amount = data.get('amount', 0.0)
        campaign_id = data.get('campaign_id', None)

        if not campaign_id:

            return jsonify({'message': 'Campaign ID is required'}), 400

        if type == 'influencer':
            print("campaign",campaign_id)
            influ = Influencer.query.get(id)
            print(influ)
            if not Influencer:
                return jsonify({'message': 'Influencer not found'}), 404

            adrequest_new = Adrequest(
                messages=message,
                requirements=requirements,
                payment_amount=payment_amount,
                status='pending',
                campaign_id=campaign_id,
                influencer_id=id
            )
            db.session.add(adrequest_new)
            db.session.commit()
            cache.delete(f"stats_{request.view_args['username']}")

            return jsonify({'message': 'Request submitted successfully'}), 201

        elif type == 'campaign':
            campaign = Campaign.query.get(id)
            if not campaign:
                return jsonify({'message': 'Campaign not found'}), 404

            adrequest_new = Adrequest(
                messages=message,
                requirements=requirements,
                payment_amount=payment_amount,
                status='pending',
                campaign_id=campaign.id,
                influencer_id=id  # Assuming `id` is the influencer_id in this context
            )
            db.session.add(adrequest_new)
            db.session.commit()
            cache.delete(f"stats_{request.view_args['username']}")


            return jsonify({'message': 'Request submitted successfully'}), 201
        else:
            return jsonify({'message': 'Invalid request type'}), 400

    except Exception as e:
        db.session.rollback()
        cache.delete(f"stats_{request.view_args['username']}")

        print("Error submitting request:", e)
        return jsonify({'message': 'Failed to submit request'}), 500

@auth_required
@jwt_required()
@app.route("/adrequests/<string:username>", methods=['GET'])
@cache.cached(timeout=300,key_prefix=lambda: f"adrequests_{request.view_args['username']}")
def get_adrequests(username):
    user = User.query.filter_by(username=username).first()
    print(user)
    if user.role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
        ad_requests = Adrequest.query.filter(Adrequest.campaign_id.in_([campaign.id for campaign in campaigns])).all()
        ad_requests = [{
                 'id': ad.id,
        'message': ad.messages,
        'requirements': ad.requirements,
        'payment_amount': ad.payment_amount,
        'status': ad.status,
        'campaign_name': [cam.name for cam in campaigns if cam.id==ad.id][0]
                        } for ad in ad_requests if ad.status == 'pending']
        return jsonify([ad_request for ad_request in ad_requests]), 200
    if user.role == 'influencer':
        influencer = Influencer.query.filter_by(user_id=user.id).first()
        ad_requests = Adrequest.query.filter_by(influencer_id=influencer.id).all()

        ad_requests = [{
            'id': ad.id,
            'message': ad.messages,
            'requirements': ad.requirements,
            'payment_amount': ad.payment_amount,
            'status': ad.status,
            'campaign_name': Campaign.query.get(ad.campaign_id).name
        } for ad in ad_requests if ad.status == 'pending']

        return jsonify(ad_requests), 200
    else:
        return jsonify({'message': 'Unauthorized role'}), 403

@auth_required
@jwt_required()
@app.route('/process_request/<int:id>', methods=['POST'])
def process_ad_requests(id):
    ad_request = Adrequest.query.get(id)
    
    if not ad_request:
        return jsonify({'message': 'Ad request not found'}), 404

    data = request.get_json()

    if not data or "todo" not in data or "sender" not in data:
        return jsonify({'message': 'Invalid data. "todo" and "sender" fields are required'}), 400

    try:
        if data.get("todo") == 'accept':
            if data.get("sender") == 'sponsor':
                campaign = Campaign.query.get(ad_request.campaign_id)
                influencer = Influencer.query.get(ad_request.influencer_id)
                
                if campaign and influencer:
                    if influencer not in campaign.influencers:
                        campaign.influencers.append(influencer)
                    ad_request.status = 'accepted'
                else:
                    return jsonify({'message': 'Campaign or Influencer not found'}), 404

            elif data.get("sender") == 'influencer':
                influencer = Influencer.query.get(ad_request.influencer_id)
                campaign = Campaign.query.get(ad_request.campaign_id)
                
                if influencer and campaign:
                    if campaign not in influencer.campaigns:
                        influencer.campaigns.append(campaign)
                    ad_request.status = 'accepted'
                else:
                    return jsonify({'message': 'Campaign or Influencer not found'}), 404

            else:
                return jsonify({'message': 'Invalid sender type'}), 400

        elif data.get("todo") == 'reject':
            ad_request.status = 'rejected'

        else:
            return jsonify({'message': 'Invalid action'}), 400

        # Invalidate cache after processing request
        cache.delete(f"stats_{request.view_args['username']}")
        
        # Commit changes to the database
        db.session.commit()

        return jsonify({'message': f'Request has been {ad_request.status}'}), 200
    
    except Exception as e:
        # Handle any unexpected errors
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@admin_required
@jwt_required()
@app.route('/getcampaings',methods=["GET"])
@cache.cached(timeout=300, key_prefix="active_campaigns")
def get_all_campaigns():
    campaig = Campaign.query.all()
    campaigns = []
    for campaign in campaig:
        if campaign.end_date<datetime.now():
            campaigns.append(campaign)
    return jsonify([cam.to_dic() for cam in campaigns]),200

@admin_required
@jwt_required()
@app.route('/flaguser/<string:username>',methods=['POST'])
def flag_user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message":"User not found"}), 404
    data= request.get_json()
    user.flagged=True
    user.flag_reason = data.get("flag_reason")
    db.session.commit()
    cache.delete(f"stats_{request.view_args['username']}")

    return jsonify({"message":"The user has been flagged successfully"}), 200

@admin_required
@jwt_required()
@app.route('/unflaguser/<string:username>',methods=['POST'])
def unflag_user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message":"User not found"}), 404
    user.flagged=False
    user.flag_reason = None
    cache.delete(f"stats_{request.view_args['username']}")

    db.session.commit()
    return jsonify({"message":"The user has been unflagged successfully"}), 200

@app.route("/remove_user/<int:id>", methods=['DELETE'])
@jwt_required()
def remove_user(id):
    user = User.query.get(id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    try:
        db.session.delete(user)  
        db.session.commit()
        cache.delete(f"stats_{request.view_args['username']}")

        return jsonify({'message': 'User and associated data deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_required
@jwt_required()
@app.route('/flagged_data',methods = ['GET'])
@cache.cached(timeout=300, key_prefix='flagged_data')
def get_flaggerData():
    users = User.query.filter(User.role != 'admin').all()
    campaigns = Campaign.query.filter(Campaign.flagged == True).all()

    flagged_users = [user for user in users if user.flagged]
    flagged_campaigns = [campaign for campaign in campaigns if campaign.flagged]

    return jsonify({
        "users":[user.to_dict() for user in flagged_users],
        "campaigns":[campaign.to_dic() for campaign in flagged_campaigns]
    }),200

@celery.task
def export_campaigns_to_csv(sponsor_id, campaign_id):
    with app.app_context():
        sponsor = Sponsor.query.get(sponsor_id)
        if sponsor:
            campaign = Campaign.query.get(campaign_id)
            if campaign and campaign.sponsor_id == sponsor.id:

                csv_file = os.path.join("static", "stats", f"{sponsor.company_name}_{campaign.name}.csv")
                os.makedirs(os.path.dirname(csv_file), exist_ok=True)
                
                with open(csv_file, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Name', 'Description', 'Budget', 'Start Date', 'End Date', 'Visibility', 'Goals'])
                    writer.writerow([
                        campaign.name,
                        campaign.description,
                        campaign.budget,
                        campaign.start_date,
                        campaign.end_date,
                        campaign.visibility,
                        campaign.goals
                    ])
                print(f"CSV export completed for {sponsor.company_name}")

                send_export_completion_email(sponsor.user.email, campaign.name)
            else:
                print("Campaign not found or unauthorized access")
        else:
            print("Sponsor not found")

@auth_required
@app.route('/download_campaign/<int:campaign_id>/<string:username>', methods=['GET'])
def export_campaign(campaign_id,username):
    user = User.query.get(username=username).first()
    if user.role != 'sponsor':
        return jsonify({"message": "Unauthorized"}), 403

    sponsor = Sponsor.query.filter_by(user_id=user.id).first()
    if not sponsor:
        return jsonify({"message": "Sponsor not found"}), 404

    campaign = Campaign.query.get(campaign_id)
    if not campaign or campaign.sponsor_id != sponsor.id:
        return jsonify({"message": "Campaign not found or unauthorized access"}), 404

    export_campaigns_to_csv.delay(sponsor.id, campaign_id)
    return jsonify({'message': 'Export initiated successfully'}), 200

def send_export_completion_email(to_email, campaign_name):
    subject = "Your Campaign Export is Ready"
    body = f"""
    <p>Dear Sponsor,</p>
    <p>The export for your campaign <strong>{campaign_name}</strong> is now ready.</p>
    <p>Please log in to your account to download the CSV file.</p>
    <p>Best regards,<br>Your Team</p>
    """
    is_html = True

    api_key = app.config['EMAIL_API_KEY']
    api_url = app.config['EMAIL_API_URL']
    api_mail = str(app.config['EMAIL_API_MAIL'])

    data = {
        "apikey": api_key,
        "from": api_mail,
        "subject": subject,
        "recipients": [{"email": to_email}],
    }
    if is_html:
        data["html"] = body
    else:
        data["message"] = body

    response = requests.post(api_url, json=data)
    if response.status_code == 200:
        print(f"Email sent to {to_email}")
    else:
        print(f"Failed to send email to {to_email}: {response.text}")


@celery.task
def send_daily_reminders():
    influencer_with_pending_requests = Influencer.query.filter(Influencer.ad_requests.any(Adrequest.status=="pending")).all()
    for inf in influencer_with_pending_requests:
        api_key = app.config['EMAIL_API_KEY']
        api_url = app.config['EMAIL_API_URL']
        api_mail=str(app.config['EMAIL_API_MAIL'])
        data = {
        "apikey": api_key,
        "from": api_mail,
        "subject": subject,
        "recipients": [{"email": to_email}]
    }
        if is_html:
            data["html"] = body
        else:
            data["message"] = body 
        response = requests.post(api_url, json=data)
        if response.status_code == 200:
            print(f"Email sent to {to_email}")
        else:
            print(f"Failed to send email to {to_email}: {response.text}")

    print("Daily reminders sent")

@admin_required
@jwt_required
@app.route('/approve_sponsor',methods=['POST'])
def method_name():
    id = request.get_json().get('sponsor_id')
    sponsor = Sponsor.query.filter_by(user_id=id).first()
    sponsor.is_approved = True
    db.session.commit()
    return jsonify({"message":"Sponsor approved successfully"}),200

@auth_required
@jwt_required
@app.route('/delete_campaign',methods=['POST'])
def delete_Campaign():
    try:
        id=request.get_json().get('campaign_id')
        campagin = Campaign.query.filter_by(id=id).first()
        if not campagin:
            return jsonify({'error': 'Campaign not found'}), 404
        print(campagin)
        db.session.delete(campagin)
        db.session.commit()
        return jsonify({'message':'deleted campaign successfully'}), 200
    except:
        return jsonify({'error':'unable to delete the campagin'}),403