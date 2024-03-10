from typing import Optional
import requests
from .identitytoolkit import IdentityToolkitHelper
from datetime import datetime


class InvalidHTTPResponseException(Exception):
    pass


class MathmatizeClassroom:
    def __init__(self, class_id: int, name: str, description: str, join_code: str):
        self.class_id = class_id
        self.name = name
        self.description = description
        self.join_code = join_code

        self.poll_session_data = {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.name}: {self.description}"


class MathmatizePollSession:
    def __init__(self, poll_session_id: int, poll_session_name: str):
        self.poll_session_id = poll_session_id
        self.poll_session_name = poll_session_name

    def __str__(self):
        return self.poll_session_name


class MathmatizePoll:
    def __init__(self, poll_uuid: str, name: str, open_date: datetime.date, target_due_date: Optional[datetime.date], poll_session: MathmatizePollSession):
        self.poll_uuid = poll_uuid
        self.name = name
        self.open_date = open_date
        self.target_due_date = target_due_date

        self.poll_session = poll_session

    def __str__(self):
        return self.name


class MathmatizeHelper:
    def __init__(self, identity: IdentityToolkitHelper, base_api_url: str = "https://mathmatize.com/api/mm"):
        """
        === Representation Invariants ===
        - len(identity.id_token) > 0
        """
        self.identity = identity
        self.base_url = base_api_url

        self.session = requests.Session()
        self.session.headers["Authorization"] = f"JWT {identity.id_token}"

        self.classes = []

    def _make_request(self, endpoint: str, method: str = "get", *args, **kwargs) -> dict:
        request_method = getattr(self.session, method)
        request_url = f"{self.base_url}/{endpoint}"

        r = request_method(request_url, *args, **kwargs)

        if r.status_code != 200:
            raise InvalidHTTPResponseException(
                f"Invalid HTTP Response Code: {r.status_code}.\nResponse body:\n" + r.text)

        return r.json()

    def fetch_classes(self) -> list[MathmatizeClassroom]:
        # Clear self.classes
        self.classes = []

        classes = self._make_request("/classes/my_memberships")

        for _class in classes:
            classroom = _class.get("classroom", {})

            name = classroom.get("name")
            class_id = classroom.get("id")
            description = classroom.get("description")
            join_code = classroom.get("code")

            class_object = MathmatizeClassroom(
                class_id=class_id, name=name, description=description, join_code=join_code)

            # Append class to self.classes
            self.classes.append(class_object)

        return self.classes

    def fetch_poll_sessions(self, classroom: MathmatizeClassroom) -> list[MathmatizePollSession]:
        poll_session_objects = []

        classroom.poll_session_data = self._make_request(
            f"classes/{classroom.class_id}/student")

        for poll_session in classroom.poll_session_data["topics_by_id"].values():
            poll_session_id = poll_session.get("id")
            poll_session_name = poll_session.get("name")

            poll_session_object = MathmatizePollSession(poll_session_id=poll_session_id,
                                                        poll_session_name=poll_session_name)
            poll_session_objects.append(poll_session_object)

        return poll_session_objects

    def fetch_polls(self, course, poll_session):
        poll_ids = []
        polls = []

        for layout in course.poll_session_data["layout"][f"{poll_session.poll_session_id}"].values():
            poll_ids += layout

        for poll_id in poll_ids:
            poll = course.poll_session_data["tasks_by_id"][poll_id]

            poll_uuid = poll.get("id")
            name = poll.get("name")
            open_date = datetime.fromisoformat(poll.get('open_date'))
            target_due_date = datetime.fromisoformat(
                poll.get('target_due_date')) if poll.get('target_due_date') else None

            poll_object = MathmatizePoll(
                poll_uuid, name, open_date, target_due_date, poll_session)

            polls.append(poll_object)

        return polls
