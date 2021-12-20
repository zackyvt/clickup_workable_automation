import requests
import os

access_token = os.environ["CLICKUP_ACCESS_TOKEN"]

headers = {
    "Authorization": access_token,
    "Content-Type": "application/json"
}

def create_candidate_task(candidate_name, job_title, phone, email):
    endpoint = "https://api.clickup.com/api/v2/list/104289666/task"
    body = {
        "name": candidate_name + " - " + job_title,
        "custom_fields": [
            {
                "id": "9ab84d7a-4096-459e-b0ec-04a4259a3dba",
                "name": "Candidate Personal Email",
                "type": "email",
                "type_config": {},
                "value": email,
                "hide_from_guests": False,
                "required": False
            },
            {
                "id": "134063c2-fd05-42d1-b5e7-a348b279e10e",
                "name": "Candidate Phone",
                "type": "phone",
                "type_config": {},
                "value": phone,
                "hide_from_guests": False,
                "required": False
            }
        ]
    }
    r = requests.post(url=endpoint, json=body, headers=headers)
    return r.json()["id"]

def move_candidate_task(stage, task_id):
    stages = {
        "Approved to Start": "104289680",
        "Start Date Confirmed": "104289685",
        "Started": "104289688",
        "Did Not Start": "104289690",
        "Offer": "dfz86-667",
        "Background": "dfz86-707"
    }
    try:
        x = stages[stage]
    except:
        return task_id
    task = requests.get("https://api.clickup.com/api/v2/task/" + task_id + "/", headers=headers).json()
    body = {
        "name": task["name"],
        "description": "" if task["description"] is None else task["description"],
        "assignees": list(map(lambda assignees: assignees["id"], task["assignees"])),
        "text_content": "" if task["text_content"] is None else task["text_content"],
        "custom_fields": task["custom_fields"]
    }
    if(task["priority"] != None): body["priority"] = task["priority"]
    requests.request("DELETE", "https://api.clickup.com/api/v2/task/" + task_id + "/", headers=headers)
    r = requests.post(url="https://api.clickup.com/api/v2/list/" + stages[stage] + "/task", json=body, headers=headers)
    print(r.content)
    return r.json()["id"]