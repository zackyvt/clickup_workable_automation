import requests
import os

access_token = os.environ["CLICKUP_ACCESS_TOKEN"]

headers = {
    "Authorization": access_token,
    "Content-Type": "application/json"
}

def create_description(candidate_name, job_title, phone, email, address, stage, summary, id, resume_url):
    description = ""
    description += "[Workable Link](https://blufox-mobile.workable.com/backend/candidates/search#zoom/" + id + ")\n"
    description += "[Resume](" + resume_url + ")\n"
    description += "\n"
    description += "**Name:** " + candidate_name + "\n"
    description += "**Job Title:** " + job_title + "\n"
    description += "**Stage:** " + stage + "\n"
    description += "\n"
    description += "**Address:** " + address + "\n"
    description += "**Phone:** " + phone + "\n"
    description += "**Email:** " + email + "\n"
    description += "\n"
    description += "**Summary:**\n"
    description += summary
    return description

def create_candidate_task(candidate_name, job_title, phone, email, address, stage, summary, id, resume_url):
    endpoint = "https://api.clickup.com/api/v2/list/104289666/task"
    body = {
        "name": candidate_name + " - " + job_title,
        "markdown_description": create_description(candidate_name, job_title, phone, email, address, stage, summary, id, resume_url),
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

def set_stage_description(description, stage):
    lines = description.split("\n")
    for i in range(len(lines)):
        if "Stage" in lines[i]:
            lines[i] = "**Stage:** " + stage
    return "\n".join(lines)

def move_candidate_task(stage, task_id):
    stages = {
        "Approved to Start": "104289680",
        "Start Date Confirmed": "104289685",
        "Started": "104289688",
        "Did Not Start": "104289690",
        "Offer": "174093291",
        "Background": "174093295"
    }
    task = requests.get("https://api.clickup.com/api/v2/task/" + task_id + "/", headers=headers).json()
    body = {
        "name": task["name"],
        "markdown_description": "" if task["description"] is None else set_stage_description(task["description"], stage),
        "assignees": list(map(lambda assignees: assignees["id"], task["assignees"])),
        "custom_fields": task["custom_fields"]
    }
    if(task["priority"] != None): body["priority"] = task["priority"]
    requests.request("DELETE", "https://api.clickup.com/api/v2/task/" + task_id + "/", headers=headers)
    try:
        x = stages[stage]
        r = requests.post(url="https://api.clickup.com/api/v2/list/" + x + "/task", json=body, headers=headers)
    except:
        r = requests.post(url="https://api.clickup.com/api/v2/list/" + task["list"]["id"] + "/task", json=body, headers=headers)
    finally:
        return r.json()["id"]