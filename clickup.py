import requests
import os

access_token = os.environ["CLICKUP_ACCESS_TOKEN"]

headers = {
    "Authorization": access_token,
    "Content-Type": "application/json"
}

def create_description(candidate_name, job_title, phone, email, address, stage, summary, profile_url, resume_url, location_str, applied_position, skills):
    description = ""
    description += "[Workable Profile](" + profile_url + ")\n"
    description += "\n"
    description += "**Name:** " + candidate_name + "\n"
    description += "**Headline:** " + job_title + "\n"
    description += "**Applying For:** " + applied_position + "\n"
    description += "**Stage:** " + stage + "\n"
    description += "\n"
    description += "**Address:** " + address + "\n"
    description += "**Location:** " + location_str + "\n"
    description += "**Phone:** " + phone + "\n"
    description += "**Email:** " + email + "\n"
    description += "\n"
    description += "**Skills:** " + ", ".join(list(map(lambda x: x["name"], skills))) + "\n\n"
    description += "**Summary:**\n"
    description += summary
    return description

def create_candidate_task(candidate_name, job_title, phone, email, address, stage, summary, profile_url, resume_url, location_str, applied_position, skills):
    endpoint = "https://api.clickup.com/api/v2/list/157768892/task"
    body = {
        "name": candidate_name + " - " + applied_position,
        "markdown_description": create_description(candidate_name, job_title, phone, email, address, stage, summary, profile_url, resume_url, location_str, applied_position, skills),
        "custom_fields": [
            {
                "id": "979fb074-2ee0-4855-8236-6f8029c29c52",
                "name": "Candidate Name",
                "type": "short_text",
                "type_config": {},
                "date_created": "1640110971688",
                "hide_from_guests": False,
                "value": candidate_name,
                "required": False
            },
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
    print(r.json())
    return r.json()["id"]

def set_stage_description(description, stage, profile_url):
    lines = description.split("\n")
    for i in range(len(lines)):
        if "Workable Profile" in lines[i]:
            lines[i] = "[Workable Profile](" + profile_url + ")"
            continue
        if len(lines[i].split(":")) == 2:
            lines[i] = "**" + lines[i].split(":")[0] + ":** " + lines[i].split(":")[1]
            continue
        if "Stage" in lines[i]:
            lines[i] = "**Stage:** " + stage
            continue
    return "\n".join(lines)

def move_candidate_task(stage, task_id, profile_url):
    stages = {
        "Approved to Start": "104289680",
        "Start Date Confirmed": "104289685",
        "ADP Onboarding": "122149571",
        "Hired": "104289688",
        "Did Not Start": "104289690",
        "Offer": "174093291",
        "Background": "174093295"
    }
    task = requests.get("https://api.clickup.com/api/v2/task/" + task_id + "/", headers=headers).json()
    body = {
        "name": task["name"],
        "markdown_description": "-" if task["description"] is None else set_stage_description(task["description"], stage, profile_url),
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