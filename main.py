import requests
import os
import json

session = requests.Session()
session.headers = {
    "Origin": "https://mathmatize.com"
}


def login(email: str, password: str) -> str:
    r = session.post(
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyDlmqEmT_xyn91XrDmJqSlXTTnN_DcTFAk",
        json={
            "returnSecureToken": True,
            "email": email,
            "password": password,
            "clientType": "CLIENT_TYPE_WEB"})

    json_response = r.json()

    session.headers["Authorization"] = "JWT " + json_response.get("idToken")

    return json_response


def refresh_token(refresh_token: str) -> str:
    pass


def store_credentials(credentials: dict, filename: str) -> bool:
    try:
        with open(filename, "w") as file:
            json.dump(credentials, file, indent=4)

        return True
    finally:
        return False


def fetch_courses():
    r = session.get("https://mathmatize.com/api/mm/classes/my_memberships")
    return r.json()


def fetch_poll_sessions(course_id):
    r = session.get(
        f"https://mathmatize.com/api/mm/classes/{course_id}/student")
    return r.json()


def fetch_polls(topic_id, poll_sessions):
    poll_ids = []
    polls = []

    for layout in poll_sessions["layout"][f"{topic_id}"].values():
        poll_ids += layout

    for poll_id in poll_ids:
        polls.append(poll_sessions["tasks_by_id"][poll_id])

    return polls


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()

    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")

    credentials = login(EMAIL, PASSWORD)

    store_credentials(credentials, ".credentials.json")

    print(f"Logged in as {credentials.get('displayName')}")

    courses = fetch_courses()

    for index, course in enumerate(courses):
        print(f"{index + 1}.", course.get("classroom", {}).get("name"))

    poll_sessions = fetch_poll_sessions(
        courses[int(input("> ")) - 1]["classroom"]["id"])

    poll_topics = list(poll_sessions["topics_by_id"].values())

    for index, poll_session in enumerate(poll_topics):
        print(f"{index + 1}.", poll_session["name"])

    polls = fetch_polls(
        poll_topics[int(input("> ")) - 1]["id"], poll_sessions)

    autoselected_poll = None

    for poll in polls:
        if poll["target_due_date"] is None:
            autoselected_poll = poll
            break

    if autoselected_poll:
        print(autoselected_poll)
        print(f"Poll autoselected!\n{autoselected_poll['name']}")
        if input("Proceed? (y/n)\n> ") != "y":
            autoselected_poll = None

    if autoselected_poll is None:
        for index, poll in enumerate(polls):
            print(f"{index + 1}.", poll)
        poll_id = polls[int(input("> ")) - 1]['id']
    else:
        poll_id = autoselected_poll["id"]

    input("")
