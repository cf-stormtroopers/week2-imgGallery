from sqlmodel import Session, select, delete
from typing import List, Optional
from ..models.user import Role, Permission, RolePermission, User


class PermissionService:
    """Service for managing roles and permissions."""

    def __init__(self, session: Session):
        self.session = session

    def get_user_permissions(self, user: Optional[User]) -> List[str]:
        """Get all permissions for a user."""
        if not user:
            # Get public role permissions
            public_role = self.session.exec(
                select(Role).where(Role.name == "public")
            ).first()
            if public_role:
                return self._get_role_permissions(public_role.id)
            return []

        # Get user's role permissions directly from user.role_id
        if user.role_id:
            role_permissions = self._get_role_permissions(user.role_id)
            return role_permissions

        return []

    def _get_role_permissions(self, role_id: int) -> List[str]:
        """Get permissions for a specific role."""
        role_permissions = self.session.exec(
            select(RolePermission).where(RolePermission.role_id == role_id)
        ).all()

        permission_names = []
        for rp in role_permissions:
            permission = self.session.exec(
                select(Permission).where(Permission.id == rp.permission_id)
            ).first()
            if permission:
                permission_names.append(permission.name)

        return permission_names

    def create_role(
        self, name: str, permissions: List[str], description: Optional[str] = None
    ) -> Optional[Role]:
        """Create a new role with permissions."""
        # Check if role already exists
        existing_role = self.session.exec(select(Role).where(Role.name == name)).first()
        if existing_role:
            return None

        # Create role
        role = Role(name=name, description=description)
        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)

        # Add permissions
        self._update_role_permissions(role.id, permissions)

        return role

    def update_role_permissions(self, role_id: int, permissions: List[str]) -> bool:
        """Update role permissions by recreating them."""
        # Check if role exists
        role = self.get_role_by_id(role_id)
        if not role:
            return False

        self._update_role_permissions(role_id, permissions)
        return True

    def _update_role_permissions(self, role_id: int, permissions: List[str]) -> None:
        """Internal method to update role permissions."""
        # Remove existing permissions
        existing_permissions = self.session.exec(
            select(RolePermission).where(RolePermission.role_id == role_id)
        ).all()
        for rp in existing_permissions:
            self.session.delete(rp)

        # Add new permissions
        for perm_name in permissions:
            permission = self.session.exec(
                select(Permission).where(Permission.name == perm_name)
            ).first()
            if permission:
                role_permission = RolePermission(
                    role_id=role_id, permission_id=permission.id
                )
                self.session.add(role_permission)

        self.session.commit()

    def get_all_roles(self) -> List[Role]:
        """Get all roles."""
        return self.session.exec(select(Role)).all()

    def get_all_permissions(self) -> List[Permission]:
        """Get all permissions."""
        return self.session.exec(select(Permission)).all()

    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """Get a role by ID."""
        return self.session.get(Role, role_id)

    def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """Get a role by name."""
        statement = select(Role).where(Role.name == role_name)
        return self.session.exec(statement).first()

    def get_role_permissions(self, role_id: int) -> List[Permission]:
        """Get all permissions for a role."""
        statement = (
            select(Permission)
            .join(RolePermission)
            .where(RolePermission.role_id == role_id)
        )
        return self.session.exec(statement).all()

    def delete_role(self, role_id: int) -> bool:
        """Delete a role and its associations."""
        role = self.session.get(Role, role_id)
        if not role:
            return False

        # Delete role permissions first
        self.session.exec(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )

        # Update users with this role to public role
        public_role = self.session.exec(
            select(Role).where(Role.name == "public")
        ).first()
        public_role_id = public_role.id if public_role else 1

        users_with_role = self.session.exec(
            select(User).where(User.role_id == role_id)
        ).all()
        for user in users_with_role:
            user.role_id = public_role_id
            self.session.add(user)

        # Delete the role
        self.session.delete(role)
        self.session.commit()

        return True

    def ensure_initial_data(self) -> None:
        """Create initial permissions, roles and role-permission mappings if they don't exist."""
        # Create comprehensive list of permissions
        initial_permissions = [
            "read_all_posts",
            "edit_posts",
            "delete_posts",
            "update_site_settings",
        ]

        for perm_name in initial_permissions:
            existing = self.session.exec(
                select(Permission).where(Permission.name == perm_name)
            ).first()
            if not existing:
                permission = Permission(name=perm_name)
                self.session.add(permission)
                print(f"Created permission: {perm_name}")

        self.session.commit()

        # Create roles
        roles_data = [
            {"name": "admin", "description": "Administrator role"},
            {"name": "user", "description": "Regular user role"},
            {"name": "public", "description": "Public access role"},
        ]

        for role_info in roles_data:
            existing_role = self.session.exec(
                select(Role).where(Role.name == role_info["name"])
            ).first()
            if not existing_role:
                role = Role(
                    name=role_info["name"], description=role_info["description"]
                )
                self.session.add(role)
                print(f"Created role: {role_info['name']}")

        self.session.commit()

        # Create role-permission mappings
        role_permission_mappings = [
            # Public role permissions
            {"role_name": "public", "permission_name": "read_all_posts"},
            # Admin role permissions (all permissions)
            {"role_name": "admin", "permission_name": "read_all_posts"},
            {"role_name": "admin", "permission_name": "edit_posts"},
            {"role_name": "admin", "permission_name": "delete_posts"},
            {"role_name": "admin", "permission_name": "update_site_settings"},
            # User role permissions
            {"role_name": "user", "permission_name": "read_all_posts"},
        ]

        for mapping in role_permission_mappings:
            # Get role and permission
            role = self.session.exec(
                select(Role).where(Role.name == mapping["role_name"])
            ).first()
            permission = self.session.exec(
                select(Permission).where(Permission.name == mapping["permission_name"])
            ).first()

            if role and permission:
                # Check if mapping already exists
                existing_mapping = self.session.exec(
                    select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == permission.id,
                    )
                ).first()

                if not existing_mapping:
                    role_permission = RolePermission(
                        role_id=role.id, permission_id=permission.id
                    )
                    self.session.add(role_permission)
                    print(
                        f"Mapped {mapping['role_name']} -> {mapping['permission_name']}"
                    )

        self.session.commit()
