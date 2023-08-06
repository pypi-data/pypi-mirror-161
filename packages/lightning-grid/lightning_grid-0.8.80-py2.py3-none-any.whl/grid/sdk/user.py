import datetime
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, List

from grid.sdk import env
from grid.sdk._gql.queries import get_user_basic_info, get_user_teams


@dataclass
class User:
    user_id: str
    username: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    is_verified: Optional[bool] = None
    is_blocked: Optional[bool] = None
    completed_signup: Optional[bool] = None
    team_name: Optional[str] = None


def set_default_cluster(cluster_id):
    """Set the default cluster in the local configuration
    and in the backend (backend is TODO)
    """
    settings_path = Path(env.GRID_SETTINGS_PATH)
    if not settings_path.exists():
        env.write_default_settings(settings_path)
    user_settings = json.load(settings_path.open())
    user_settings['context'] = cluster_id
    with settings_path.open('w') as file:
        json.dump(user_settings, file, ensure_ascii=False, indent=4)
    os.environ['GRID_CLUSTER_ID'] = cluster_id
    env.reset_global_variables()


def user_from_logged_in_account() -> "User":
    resp = get_user_basic_info()
    if not resp["isVerified"]:
        raise PermissionError(
            f"User account not yet verified. Verify your "
            f"account at {env.GRID_URL}/#/verification"
        )
    if not resp["completedSignup"]:
        raise PermissionError(
            f"You haven't yet completed registration. Please complete "
            f"registration at {env.GRID_URL}/#/registration"
        )
    if resp["isBlocked"]:
        raise PermissionError(
            f"Your account with username `{resp['username']}` has been "
            f"suspended. Please reach out to support at support@grid.ai"
        )

    return User(
        user_id=resp["userId"],
        username=resp["username"],
        first_name=resp["firstName"],
        last_name=resp["lastName"],
        email=resp["email"],
        is_verified=resp["isVerified"],
        is_blocked=resp["isBlocked"],
        completed_signup=resp["completedSignup"],
    )


@dataclass(frozen=True)
class Team:
    team_id: str
    name: str
    created_at: datetime.datetime
    role: str
    members: Dict[str, User]


def get_teams() -> Dict[str, Team]:
    team_definitions = get_user_teams()
    teams = {}
    for team in team_definitions:
        members = {}
        for member in team['members']:
            user = User(
                user_id=member['id'],
                username=member['username'],
                first_name=member['firstName'],
                last_name=member['lastName'],
            )
            members[user.user_id] = user

        team = Team(
            team_id=team['id'],
            name=team['name'],
            created_at=datetime.datetime.fromisoformat(team['createdAt']),
            role=team['role'],
            members=members,
        )
        teams[team.team_id] = team

    return teams


def get_user_team_members() -> List[User]:
    """Return all users (id, username, team name) of the currently logged in user"""
    users = []
    for team_data in get_user_teams():
        for member_data in team_data['members']:
            users.append(
                User(
                    user_id=member_data['id'],
                    username=member_data['username'],
                    team_name=team_data['name'],
                    first_name=member_data['firstName'],
                    last_name=member_data['lastName']
                )
            )
    return users
