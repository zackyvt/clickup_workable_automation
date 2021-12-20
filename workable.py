import os
import requests
import redis
import clickup

def parse_redis_url(url):
    host = url.split("@")[1].split(":")[0]
    password = url.split("@")[0].split("://:")[1]
    port = int(url.split("@")[1].split(":")[1])
    return (host, password, port)

(host, password, port) = parse_redis_url(os.environ["REDIS_URL"])
db = redis.Redis(host=host, password=password, port=port, charset="utf-8", decode_responses=True)

headers = {
    "Authorization": "Bearer " + os.environ["WORKABLE_ACCESS_TOKEN"],
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def delete_all_entries():
    for key in db.scan_iter("*"):
        if key == "candidate_created_webhook_id" or key == "candidate_moved_webhook_id":
            continue
        print("deleted key " + key)
        db.delete(key)

import time

def load_all_entries(include_applied=False):
    accepted_stages = ["background", "offer", "adp-onboarding", "approved-to-start", "hired", "did-not-start"]
    if(include_applied):
        accepted_stages.append("applied")
    for stage in accepted_stages:
        next = "https://" + os.environ["WORKABLE_ACCOUNT"] + ".workable.com/spi/v3/candidates?stage=" + stage
        while True:
            r = requests.get(next, headers=headers)
            candidates = r.json()["candidates"]
            for candidate in candidates:
                req = requests.get("https://" + os.environ["WORKABLE_ACCOUNT"] + ".workable.com/spi/v3/candidates/" + candidate["id"], headers=headers)
                if(req.status_code == 429):
                    candidates.append(candidate)
                    time.sleep(10)
                    continue
                candidate = req.json()["candidate"]
                task_id = clickup.create_candidate_task(candidate["name"], "-" if candidate["headline"] is None else candidate["headline"], "-" if candidate["phone"] is None else candidate["phone"], candidate["email"], "-" if candidate["address"] is None else candidate["address"], candidate["stage"], "-" if candidate["summary"] is None else candidate["summary"], candidate["profile_url"], "-" if candidate["resume_url"] is None else candidate["resume_url"], "-" if candidate["location"]["location_str"] is None else candidate["location"]["location_str"], candidate["job"]["title"], candidate["skills"])
                task_id = clickup.move_candidate_task(candidate["stage"], task_id, candidate["profile_url"])
                db.set(candidate["id"], task_id)
                db.set(candidate["id"] + "profile_url", candidate["profile_url"])
                print("added task " + task_id)
            try:
                paging = r.json()["paging"]
                next = paging["next"]
            except:
                break

delete_all_entries()
load_all_entries()
#load_all_entries(include_applied=True)