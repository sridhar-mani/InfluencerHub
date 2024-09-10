from flask import Flask
from flask_cors import CORS
import redis

try:
    r = redis.Redis(
    host='redis-10812.c322.us-east-1-2.ec2.redns.redis-cloud.com', 
    port= 10812, 
    password='hqNoRpztHCBnh46RrKz4QL4CS9xkuScn'
)
    r.ping()
except redis.ConnectionError:
    print("connection failed.")

app =Flask(__name__)

import config
from api.Models import models
from api.Routes import routes

CORS(app)

if __name__=="__main__":
    app.run(debug=True)