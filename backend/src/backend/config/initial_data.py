from sqlmodel import select
from .database import get_session
from backend.utils.auth import hash_password
from backend.models.models import Setting, User


def create_initial_data():
    session = next(get_session())

    initial_users = [
        User(
            username="CloneFest2025",
            display_name="Administrator",
            password_hash=hash_password("CloneFest2025"),
            role="admin"
        )
    ]

    initial_settings = [
        Setting(key="site_name", value="My Gallery"),
        Setting(key="allow_registrations", value="true"),
    ]

    for user in initial_users:
        existing_user = session.exec(select(User).where(User.username == user.username)).first()
        if not existing_user:
            session.add(user)
            print(f"Created initial user: {user.username}")
        else:
            print(f"User {user.username} already exists")

    for setting in initial_settings:
        existing_setting = session.exec(select(Setting).where(Setting.key == setting.key)).first()
        if not existing_setting:
            session.add(setting)
            print(f"Created initial setting: {setting.key} = {setting.value}")
        else:
            print(f"Setting {setting.key} already exists")

    session.commit()
