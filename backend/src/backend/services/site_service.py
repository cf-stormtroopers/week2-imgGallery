from sqlmodel import Session, select
from typing import List, Optional, Dict, Any

from ..models.system import Setting, Extension
from ..models.user import User, UserRead
from .permission_service import PermissionService


class SiteService:
    """Service for site-wide information and configuration."""

    def __init__(self, session: Session):
        self.session = session
        self.permission_service = PermissionService(session)

    async def get_site_info(
        self, current_user: Optional[User] = None
    ) -> Dict[str, Any]:
        """
        Get general site information including user info, blog title, extensions, etc.
        """
        site_info = {
            "user": None,
            "blog_title": await self._get_blog_title(),
            "blog_description": await self._get_blog_description(),
            "extensions": await self._get_active_extensions(),
            "theme": await self._get_active_theme_name(),
            "settings": await self._get_public_settings(),
            "features": await self._get_enabled_features(),
            "permissions": self.permission_service.get_user_permissions(current_user),
        }

        # Include user info if authenticated
        if current_user:
            site_info["user"] = UserRead(
                id=current_user.id,
                username=current_user.username,
                email=current_user.email,
                display_name=current_user.display_name,
                bio=current_user.bio,
                avatar_url=current_user.avatar_url,
                role_id=current_user.role_id,
                created_at=current_user.created_at,
                updated_at=current_user.updated_at,
            )

        return site_info

    async def _get_blog_title(self) -> str:
        """Get the blog title from settings."""
        setting = self.session.exec(
            select(Setting).where(Setting.key == "blog_title")
        ).first()
        return setting.value if setting else "My Blog"

    async def _get_blog_description(self) -> str:
        """Get the blog description from settings."""
        setting = self.session.exec(
            select(Setting).where(Setting.key == "blog_description")
        ).first()
        return setting.value if setting else "A blog powered by FastAPI"

    async def _get_active_extensions(self) -> List[str]:
        """Get list of active extension names."""
        extensions = self.session.exec(
            select(Extension).where(Extension.is_active == True)
        ).all()
        return [ext.slug for ext in extensions]

    async def _get_active_theme_name(self) -> Optional[str]:
        """Get the name of the currently active theme."""
        from ..models.system import Theme

        theme = self.session.exec(select(Theme).where(Theme.is_active == True)).first()
        return theme.name if theme else None

    async def _get_public_settings(self) -> Dict[str, Any]:
        """Get public-facing settings (non-sensitive configuration)."""
        public_keys = [
            "show_search",
            "show_markdown",
            "show_registration",
        ]

        settings = {}
        for key in public_keys:
            setting = self.session.exec(
                select(Setting).where(Setting.key == key)
            ).first()
            if setting:
                # Convert boolean strings to actual booleans
                if setting.type == "boolean":
                    settings[key] = setting.value.lower() == "true"
                elif setting.type == "integer":
                    settings[key] = (
                        int(setting.value) if setting.value.isdigit() else None
                    )
                else:
                    settings[key] = setting.value
            else:
                settings[key] = None

        return settings

    async def _get_enabled_features(self) -> List[str]:
        """Get list of enabled features based on settings and extensions."""
        features = []

        # Check for comment system
        if await self._is_feature_enabled("allow_comments"):
            features.append("comments")

        # Check for user registration
        if await self._is_feature_enabled("allow_registration"):
            features.append("registration")

        # Check for file uploads
        features.append("file_uploads")  # Always enabled for now

        # Check for themes
        features.append("themes")  # Always enabled

        # Check extensions for additional features
        active_extensions = await self._get_active_extensions()
        for ext in active_extensions:
            features.append(f"ext_{ext.lower()}")

        return features

    async def _is_feature_enabled(self, setting_key: str) -> bool:
        """Check if a feature is enabled via settings."""
        setting = self.session.exec(
            select(Setting).where(Setting.key == setting_key)
        ).first()
        if setting and setting.type == "boolean":
            return setting.value.lower() == "true"
        return False

    async def get_all_extensions(self) -> List[Extension]:
        """Get all extensions (active and inactive)."""
        return self.session.exec(select(Extension)).all()

    async def get_active_extensions(self) -> List[Extension]:
        """Get only active extensions."""
        return self.session.exec(
            select(Extension).where(Extension.is_active == True)
        ).all()

    async def update_extension_status(self, extension_slug: str, is_active: bool) -> Extension:
        """
        Update the active status of an extension.
        
        Args:
            extension_slug: The slug of the extension to update
            is_active: The new active status
            
        Returns:
            The updated extension
            
        Raises:
            ValueError: If extension is not found
        """
        extension = self.session.exec(
            select(Extension).where(Extension.slug == extension_slug)
        ).first()
        if not extension:
            raise ValueError(f"Extension with slug '{extension_slug}' not found")
        
        extension.is_active = is_active
        self.session.add(extension)
        self.session.commit()
        self.session.refresh(extension)
        
        return extension

    async def update_settings(
        self,
        blog_title: Optional[str] = None,
        show_search: Optional[bool] = None,
        show_markdown: Optional[bool] = None,
        show_registration: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Update site settings.
        """
        updated_settings = {}

        if blog_title is not None:
            setting = await self._get_or_create_setting("blog_title", "string")
            setting.value = blog_title
            self.session.add(setting)
            updated_settings["blog_title"] = blog_title

        if show_search is not None:
            setting = await self._get_or_create_setting("show_search", "boolean")
            setting.value = str(show_search).lower()
            self.session.add(setting)
            updated_settings["show_search"] = show_search

        if show_markdown is not None:
            setting = await self._get_or_create_setting("show_markdown", "boolean")
            setting.value = str(show_markdown).lower()
            self.session.add(setting)
            updated_settings["show_markdown"] = show_markdown

        if show_registration is not None:
            setting = await self._get_or_create_setting("show_registration", "boolean")
            setting.value = str(show_registration).lower()
            self.session.add(setting)
            updated_settings["show_registration"] = show_registration

        self.session.commit()
        return updated_settings

    async def _get_or_create_setting(self, key: str, setting_type: str) -> Setting:
        """Get an existing setting or create a new one."""
        setting = self.session.exec(select(Setting).where(Setting.key == key)).first()

        if not setting:
            setting = Setting(
                key=key, value="", type=setting_type, description=f"Setting for {key}"
            )

        return setting
