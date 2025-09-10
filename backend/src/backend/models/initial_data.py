from backend.src.backend.utils.auth import hash_password
from backend.src.backend.models.models import Setting, User


def get_initial_data():
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
        existing_user = User.get_or_none(User.username == user.username)
        if not existing_user:
            user.save()
            print(f"Created initial user: {user.username}")
        else:
            print(f"User {user.username} already exists")

    for setting in initial_settings:
        existing_setting = Setting.get_or_none(Setting.key == setting.key)
        if not existing_setting:
            setting.save()
            print(f"Created initial setting: {setting.key} = {setting.value}")
        else:
            print(f"Setting {setting.key} already exists")
