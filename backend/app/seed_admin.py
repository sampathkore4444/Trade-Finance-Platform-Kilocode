"""
Seed Admin User Script
Run this script to create the default admin user after the database tables are created.

Usage:
    python -m app.seed_admin

Or from docker:
    docker-compose exec backend python -m app.seed_admin
"""

import asyncio
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin_user():
    """Create admin user if not exists."""
    from app.database import AsyncSessionLocal
    from app.modules.users.models import (
        User,
        Role,
        user_roles,
        Organization,
        Branch,
        Department,
    )

    async with AsyncSessionLocal() as session:
        # Check if admin exists
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()

        if admin:
            print("Admin user already exists!")
            return

        # Create default organization
        org = Organization(
            name="Trade Finance Bank", code="TFB", is_active=True
        )
        session.add(org)
        await session.flush()

        # Create default branch
        branch = Branch(
            name="Main Branch", code="MB001", organization_id=org.id, is_active=True
        )
        session.add(branch)
        await session.flush()

        # Create default department
        dept = Department(
            name="Trade Finance Department",
            code="TFD001",
            organization_id=org.id,
            is_active=True,
        )
        session.add(dept)
        await session.flush()

        # Create admin user
        admin = User(
            email="admin@tradefinance.com",
            username="admin",
            password_hash=pwd_context.hash("admin123"),
            first_name="System",
            last_name="Administrator",
            is_active=True,
            is_verified=True,
            is_mfa_enabled=False,
            branch_id=branch.id,
            department_id=dept.id,
        )
        session.add(admin)
        await session.flush()

        # Create default roles
        roles_data = [
            ("ADMIN", "System Administrator with full access"),
            (
                "RELATIONSHIP_MANAGER",
                "Manages customer relationships and trade transactions",
            ),
            ("CREDIT_OFFICER", "Evaluates credit applications and risk"),
            ("OPERATIONS", "Handles document processing and operational tasks"),
            ("COMPLIANCE", "Manages compliance and KYC verification"),
            ("VIEWER", "Read-only access to view transactions"),
        ]

        roles = []
        for name, desc in roles_data:
            role = Role(name=name, description=desc)
            session.add(role)
            roles.append(role)

        await session.flush()

        # Assign admin role to admin user
        admin_role = next(r for r in roles if r.name == "ADMIN")
        await session.execute(
            user_roles.insert().values(user_id=admin.id, role_id=admin_role.id)
        )

        await session.commit()
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
