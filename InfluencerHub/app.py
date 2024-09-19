from flask import Flask
from flask_cors import CORS
import redis
import redis.commands.json, redis.commands.timeseries
from flask_caching import Cache
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail

app =Flask(__name__)
CORS(app, supports_credentials=True)

import config

cache = Cache(app)
mail = Mail(app)

from api.Models import models
jwt = JWTManager(app)
from api.Routes import routes

try:
    r = redis.Redis(
    host='redis-10812.c322.us-east-1-2.ec2.redns.redis-cloud.com',
    port= 10812,
    password='hqNoRpztHCBnh46RrKz4QL4CS9xkuScn',
)
    r.ping()
except redis.ConnectionError:
    print("connection failed.")

if __name__=="__main__":
    connect_redis()
    app.run(debug=True)