import os
import requests
import redis

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

endpoint = "https://" + os.environ["WORKABLE_ACCOUNT"] + ".workable.com/spi/v3/subscriptions"
webhook_setup_data = {
    "args": {
        "account_id": os.environ["WORKABLE_ACCOUNT"]
    }
}

def setup_candidate_created_webhook():
    data = webhook_setup_data
    data["event"] = "candidate_created"
    data["target"] = os.environ["CANDIDATE_CREATED_ENDPOINT"]
    r = requests.post(url=endpoint, headers=headers, json=data)
    print(r.status_code)
    print(r.json()["id"])
    db.set("candidate_created_webhook_id", r.json()["id"])

def setup_candidate_moved_webhook():
    data = webhook_setup_data
    data["event"] = "candidate_moved"
    data["target"] = os.environ["CANDIDATE_MOVED_ENDPOINT"]
    r = requests.post(url=endpoint, headers=headers, json=data)
    print(r.status_code)
    print(r.json()["id"])
    db.set("candidate_moved_webhook_id", r.json()["id"])

def delete_webhooks():
    requests.request("DELETE", endpoint + "/" + db.get("candidate_created_webhook_id"), headers=headers)
    requests.request("DELETE", endpoint + "/" + db.get("candidate_moved_webhook_id"), headers=headers)

setup_candidate_created_webhook()
setup_candidate_moved_webhook()