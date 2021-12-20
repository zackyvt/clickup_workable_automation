from flask import Flask, request
app = Flask(__name__)

from clickup import create_candidate_task, move_candidate_task

import redis
import os

def parse_redis_url(url):
    host = url.split("@")[1].split(":")[0]
    password = url.split("@")[0].split("://:")[1]
    port = int(url.split("@")[1].split(":")[1])
    return (host, password, port)

(host, password, port) = parse_redis_url(os.environ["REDIS_URL"])
db = redis.Redis(host=host, password=password, port=port, charset="utf-8", decode_responses=True)

@app.route('/')
def index():
    return "OK"

@app.route('/candidate_created', methods=["POST"])
def candidate_created():
    data = request.get_json()["data"]
    task_id = create_candidate_task(data["name"], "" if data["headline"] is None else data["headline"], data["phone"], data["email"], data["address"], data["stage"], "" if data["summary"] is None else data["summary"], data["id"], "" if data["resume_url"] is None else data["resume_url"])
    db.set(data["id"], task_id)
    return "OK"

@app.route('/candidate_moved', methods=["POST"])
def candidate_moved():
    data = request.get_json()["data"]
    if(db.get(data["id"]) == None):
        task_id = create_candidate_task(data["name"], "" if data["headline"] is None else data["headline"], data["phone"], data["email"], data["address"], data["stage"], "" if data["summary"] is None else data["summary"], data["id"], "" if data["resume_url"] is None else data["resume_url"])
        db.set(data["id"], task_id)
    task_id = move_candidate_task(data["stage"], str(db.get(data["id"])))
    db.set(data["id"], task_id)
    return "OK"

if __name__ == '__main__':
    app.run(port=5000)