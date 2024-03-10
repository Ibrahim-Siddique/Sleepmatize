import requests
import os
from sleepmatize.identitytoolkit import IdentityToolkitHelper
from sleepmatize.mathmatize import MathmatizeHelper

session = requests.Session()
session.headers = {
    "Origin": "https://mathmatize.com"
}


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


def pick_option(options: list):
    print("\nPlease pick a number from the list below:")
    for index, option in enumerate(options):
        print(f"{index + 1}.", option)

    return options[int(input("> ")) - 1]


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()

    IDENTITY_TOOKLIT_API_KEY = os.getenv("IDENTITY_TOOLKIT_API_KEY")
    MATHMATIZE_EMAIL = os.getenv("MATHMATIZE_EMAIL")
    MATHMATIZE_PASSWORD = os.getenv("MATHMATIZE_PASSWORD")

    identity = IdentityToolkitHelper(IDENTITY_TOOKLIT_API_KEY)
    credentials = identity.sign_in(MATHMATIZE_EMAIL, MATHMATIZE_PASSWORD)

    print(f"Logged in as {credentials.get('displayName')}")

    mathmatize_helper = MathmatizeHelper(identity)

    courses = mathmatize_helper.fetch_classes()

    course = pick_option(courses)

    poll_sessions = mathmatize_helper.fetch_poll_sessions(course)

    poll_session = pick_option(poll_sessions)

    polls = mathmatize_helper.fetch_polls(course, poll_session)

    autoselected_poll = None

    for poll in polls:
        if poll.target_due_date is None:
            autoselected_poll = poll
            break

    if autoselected_poll:
        print(autoselected_poll)
        print(f"Poll autoselected!\n{autoselected_poll['name']}")
        if input("Proceed? (y/n)\n> ") != "y":
            autoselected_poll = None

    if autoselected_poll is None:
        poll_id = pick_option(polls).poll_uuid
    else:
        poll_id = autoselected_poll.poll_uuid
