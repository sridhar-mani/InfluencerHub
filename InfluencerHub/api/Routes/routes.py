from flask import Flask,session,render_template, request, redirect, url_for, flash, make_response, jsonify
from app import app
from app import cache
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import date,timedelta, datetime
from ..Models.models import User,db, Sponsor, Influencer,Campaign, Adrequest
from celery_app import celery
from flask_jwt_extended import JWTManager, create_access_token,jwt_required,get_jwt_identity
import os
import uuid
import pathlib
import json

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
            access_token=create_access_token(identity=user.id)
            return jsonify({'message':"Login Successful",'access_token':access_token,"user":user.to_dict()}), 200
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

                temp = request.files.get('profile_pic')

                if temp:
                    filename = secure_filename(temp.filename)
                    if "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_formats:
                        unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
                        profile_fin = os.path.join(app.config['UPLOAD_FOLDER_PPIC'], unique_filename).replace("\\",'/')
                        os.makedirs(app.config['UPLOAD_FOLDER_PPIC'], exist_ok=True)
                        temp.save(profile_fin)
                        new_user = User(username=username, name=name, email=email, password=generate_password_hash(password), role=role,profile_pic=profile_fin)
                        if role == 'influencer':
                            new_role_user = Influencer(category=category, niche=niche_list, reach=0, user=new_user, name=profile_name)
                        else:
                            companyname = request.form.get('companyname')
                            industry = request.form.get('industry')
                            budget = request.form.get('budget')
                            new_role_user = Sponsor(company_name=companyname, industry=industry, budget=budget, user=new_user)
                        db.session.add(new_role_user)
                        db.session.commit()

                        session['user_id'] = new_user.id
                        return jsonify({'message': "Register Successful", "user": new_user.to_dict()}), 200
                    else:
                        return jsonify({'message': 'Invalid file format. Please use PNG, TIFF, JPG, or JPEG.'}), 400
                else:
                    return jsonify({'message': 'Profile picture is required.'}), 400
            else:
                return jsonify({'message': 'Invalid role.'}), 400

        except Exception as e:
            db.session.rollback()
            # Log the exception (optionally, you can use a logging framework)
            print(f"Error occurred: {str(e)}")
            return jsonify({'message': f'Error occurred: {str(e)}'}), 500

@app.route('/users',methods=['GET','POST'])
def manage_user():
    if request.method=='POST':
        data=request.get_json()
        new_user=User(username=data['username'],password=data['password'],email=data['email'],name=data['name'],role=data['role'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()),201
    user=User.query.all()
    return jsonify([us.to_dict() for us in user])

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
@cache.cached(timeout=300, key_prefix=lambda: f"user_{request.view_args['username']}")
def handle_user(username):
    user = User.query.filter_by(username=username).first_or_404()

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
        # Return updated user details as JSON
        return jsonify(user.to_dict()), 200

    elif request.method == 'DELETE':
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        cache.delete(f"user_{request.view_args['username']}")
        # Return a successful response
        return '', 204


@app.route('/users/get_influencers', methods=['GET'])
@cache.cached(timeout=300, key_prefix='all_influencers')
def get_influencers():
    query = request.args.get('query', '')
    if query:
        # Perform a search in your database based on the query
        influencers = User.query.filter(User.role == 'influencer', User.username.ilike(f'%{query}%')).all()
        suggestions = [influencer.username for influencer in influencers]
        return jsonify(suggestions)
    else:
        return jsonify([])


@auth_required
@app.route("/add_campaign/<string:username>", methods=['POST'])
def add_campaign(username):
    temp=request.files.get("campaign_img")
    user = User.query.filter_by(username=username).first()
    if user.role == 'sponsor':
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
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=int(data['duration']))
                )
                db.session.add(new_campaign)
                db.session.commit()
                cache.delete(f"campaigns_{request.view_args['username']}")
                cache.delete('all_campaigns')
                cache.delete(f"stats_{request.view_args['username']}")
                return jsonify({'message': 'Successfull',"campaign":new_campaign.name}), 201
    else:
        return jsonify({'message': 'Unauthorized role'}), 403

@auth_required
@app.route("/campaigns/<string:username>", methods=['GET'])
@cache.cached(timeout=300, key_prefix=lambda: f"campaigns_{request.view_args['username']}")

def get_campaigns(username):
    user = User.query.filter_by(username=username).first()
    if user:
        if user.role == 'sponsor':
            sponsor = Sponsor.query.filter_by(user_id=user.id).first()
            campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
            influencer = Influencer.query.all()
            return jsonify({
                'campaigns': [campaign.to_dic() for campaign in campaigns],
                "influencers":[ i.to_dic() for i in influencer ]}
                ), 200
        elif user.role == 'influencer':
            influencer = Influencer.query.filter_by(user_id=user.id).first()
            ad_requests = Adrequest.query.filter_by(influencer_id=influencer.id).all()
            campaign_ids = [ad_request.campaign_id for ad_request in ad_requests]
            campaigns = Campaign.query.filter(Campaign.id.in_(campaign_ids)).all()
            return jsonify({
                'campaigns': [campaign.to_dic() for campaign in campaigns],
                'ad_requests': [ad_request.to_dict() for ad_request in ad_requests]
            }), 200
        else:
            campaigns = Campaign.query.all()
            influencer = Influencer.query.all()
            sponsor = User.query.filter_by(role='sponsor').all()
            return jsonify({'campaigns':[campaign.to_dic() for campaign in campaigns],'influencers':[influ.to_dic() for influ in influencer],'sponsors':[spons.to_dict() for spons in sponsor]}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@auth_required
@app.route("/campaign/<string:username>/<string:name>", methods=['GET'])
@cache.cached(timeout=300, key_prefix=lambda: f"campaigns_{request.view_args['username']}_{name}")

def get_campaign(username,name):
    user = User.query.filter_by(username=username).first()
    if user.role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id, name=name).all()
        print(campaigns)
        return jsonify([campaign.to_dic() for campaign in campaigns]), 200
    else:
        return jsonify({'message': 'Unauthorized role'}), 403

@auth_required
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
@app.route("/stats/<string:username>", methods=['GET'])
@cache.cached(timeout=300, key_prefix=lambda: f"stats_{request.view_args['username']}")
def get_stats(username):
    user = User.query.filter_by(username=username).first()
    if user:
        if user.role == 'sponsor':
            sponsor = Sponsor.query.filter_by(user_id=user.id).first()
            campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
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
                "sponsordata": sponsor.to_dic(),
                "activevsinactive": [active_campaign, inactive_campaign]
            }

            if influencers_budget:
                response_data["influencerbudget"] = influencers_budget

            return jsonify(response_data), 200

        elif user.role == 'influencer':
            influencer = Influencer.query.filter_by(user_id=user.id).first()
            ad_requests = Adrequest.query.filter_by(influencer_id=influencer.id).all()
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
@app.route('/process_request/<int:id>', methods=['POST'])
def process_ad_requests(id):
    ad_request = Adrequest.query.get(id)
    if not ad_request:
        return jsonify({'message': 'Ad request not found'}), 404
    data = request.get_json()
    print(data)
    if data.get("todo") == 'accept':
        if data.get("sender") == 'sponsor':
            campaign= Campaign.query.get(ad_request.campaign_id)
            influencer = Influencer.query.get(ad_request.influencer_id)
            if campaign and influencer:
                if influencer not in campaign.influencers:
                    campaign.influencers.append(influencer)
                ad_request.status = 'accepted'

        elif data.get("sender") == 'influencer':
            influencer = Influencer.query.get(ad_request.influencer_id)
            campaign= Campaign.query.get(ad_request.campaign_id)
            if influencer and campaign:
                if campaign not in influencer.campaigns:
                    influencer.campaigns.append(campaign)
                ad_request.status = 'accepted'

        else:
            return jsonify({'message': 'Invalid sender type'}), 400

    elif data.get("todo") == 'reject':
        ad_request.status = 'rejected'
    else:
        return jsonify({'message': 'Invalid action'}), 400
    cache.delete(f"stats_{request.view_args['username']}")

    db.session.commit()
    return jsonify({'message': f'Request has been {ad_request.status}'}), 200

@admin_required
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

@admin_required
@app.route('/remove_user/<string:username>',methods=['POST'])
def remove_user(username):
    user=User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message":"User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    cache.delete(f"stats_{request.view_args['username']}")

    return jsonify({"message":"The user has been removed successfully"}),200

@admin_required
@app.route('/flagged_data',methods = ['GET'])
@cache.cached(timeout=300, key_prefix='flagged_data')
def get_flaggerData():
    users = User.query.filter(User.role != 'admin').all()
    campaigns = Campaign.query.filter(Campaign.flagged == True).all()

    return jsonify({
        "users":[user.to_dict() for user in users],
        "campaigns":[campaign.to_dic() for campaign in campaigns]
    }),200

@celery.task
def export_campaings_to_csv(sponsor_id):
    sponsor = Sponsor.query.get(sponsor_id)
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
    csv_file=f"{sponsor.company_name}_campaigns.csv"
    with open(csv_file,'w') as file:
        writer = csv.writer(file)
        writer.writerow(['Name','Description','Budget','Start Date','End Date'])
        for cam in campaigns:
            writer.writerow([cam.name,cam.description,cam.budget,cam.start_date,cam.end_date])
    print(f"CSV export completed for {sponsor.company_name}")

@app.route('/export_campaign',methods=['POST'])
@auth_required
def export_campaigns():
    user=User.query.get(session['user_id'])
    if user.role != 'sponsor':
        return jsonify({"message":"Unauthorized"}),403
    export_campaings_to_csv.delay(user.id)
    return jsonify({'message':'Export initiated successfully'}),200