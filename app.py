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
    task_id = create_candidate_task(data["name"], "-" if data["headline"] is None else data["headline"], "-" if data["phone"] is None else data["phone"], data["email"], "-" if data["address"] is None else data["address"], data["stage"], "-" if data["summary"] is None else data["summary"], data["profile_url"], "-" if data["resume_url"] is None else data["resume_url"], "-" if data["location"]["location_str"] is None else data["location"]["location_str"], data["job"]["title"], data["skills"])
    db.set(data["id"], task_id)
    db.set(data["id"] + "profile_url", data["profile_url"])
    return "OK"

@app.route('/candidate_moved', methods=["POST"])
def candidate_moved():
    data = request.get_json()["data"]
    accepted_stages = [
        "Approved to Start",
        "Start Date Confirmed",
        "ADP Onboarding",
        "Hired",
        "Did Not Start",
        "Offer",
        "Background",
    ]
    print("disqualified? " + str(data["disqualified"]))
    if(data["stage"] not in accepted_stages):
        print(data["stage"])
        return "OK"
    if(db.get(data["id"]) == None):
        task_id = create_candidate_task(data["name"], "-" if data["headline"] is None else data["headline"], "-" if data["phone"] is None else data["phone"], data["email"], "-" if data["address"] is None else data["address"], data["stage"], "-" if data["summary"] is None else data["summary"], data["profile_url"], "-" if data["resume_url"] is None else data["resume_url"], "-" if data["location"]["location_str"] is None else data["location"]["location_str"], data["job"]["title"], data["skills"])
        db.set(data["id"], task_id)
        db.set(data["id"] + "profile_url", data["profile_url"])
    task_id = move_candidate_task(data["stage"], db.get(data["id"]), db.get(data["id"] + "profile_url"))
    db.set(data["id"], task_id)
    return "OK"

if __name__ == '__main__':
    app.run(port=5000)