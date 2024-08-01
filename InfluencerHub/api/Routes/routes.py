from flask import Flask,render_template, request, redirect, url_for, flash, session, make_response, jsonify
from app import app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import date,timedelta
from ..Models.models import User,db, Sponsor, Influencer
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
            print(username,password)
            user=User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):
            session['user_id']=user.id
            return jsonify({'message':"Login Successful","user":user.to_dict()}), 200
        else:
            return jsonify({'message':"Invalid Credentials"}), 401

@app.route('/register',methods=['POST'])
def register():
    if request.method=='POST':
        data=request.get_json()
        username = data.get('username')
      
        email=data.get('email')
        password = data.get('password')
        role=data.get('role')
        if(data.get('influencer')):
            category=data.get('category')
            name=data.get('name')
            niche=data.get('niche')
            niches = '';
            for i in niche:
                niches+=i+','
        else:
            companyname=data.get('name')
            industry=data.get('industry')
            budget = data.get('budget')
        user=User.query.filter_by(username=username).first()
        if not user:
            if(data.get('influencer')):
                new_user=User(username=username,name=name,email=email,password=generate_password_hash(password),role=role)
                new_Influencer=Influencer(category=category,niche=niches,reach=0,user=new_user)
                db.session.add(new_Influencer)
            else:
                new_user=User(username=username,name=companyname,email=email,password=generate_password_hash(password),role=role)
                new_sponsor=Sponsor(company_name=companyname,industry=industry,budget=budget,user=new_user)
                db.session.add(new_sponsor)
            print(new_user)
            db.session.add(new_user)
            db.session.commit()
            this_user=User.query.filter_by(username=username).first()
            session['user_id']=this_user.id
            return jsonify({'message':"Register Successful","user":this_user.to_dict()}), 200
        else:
            return jsonify({'message':"Username already taken"}), 401


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


@app.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(user.to_dict())
    elif request.method == 'PUT':
        data = request.get_json()
        user.username = data['username']
        user.email = data['email']
        user.password=data['password']
        user.name = data['name']
        user.role = data['role']
        db.session.commit()
        return jsonify(user.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return '', 204

@app.route('/',methods=['GET'])
def Home():
    return "hi"


def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            flash('Please login')
            return redirect(url_for('login'))
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