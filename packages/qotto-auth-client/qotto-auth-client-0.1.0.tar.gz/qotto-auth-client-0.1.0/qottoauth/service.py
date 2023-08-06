import json
import logging
from typing import Optional

from qottoauth.api import QottoAuthApi
from qottoauth.models import (
    Application,
    Permission,
    Organization,
    Account,
    Member,
    Namespace, User,
)

__all__ = [
    'QottoAuthService',
]

logger = logging.getLogger(__name__)


class QottoAuthService:

    def __init__(
            self,
            api: QottoAuthApi,
    ):
        self.api = api

    def register_application(
            self,
            application_name: str,
            application_description: str,
    ) -> Application:
        logger.info(f"Registering application {application_name}.")
        application_data = self.api.mutation(
            name='registerApplication',
            input_value={
                'name': application_name,
                'description': application_description,
            },
            body='''
                application {
                    id
                    name
                    description
                }
                created
                updated
            '''
        )
        logger.info(f"Application {application_name} registered: {application_data}.")
        return Application(
            application_id=application_data['application']['id'],
            name=application_data['application']['name'],
            description=application_data['application']['description'],
        )

    def register_permission(
            self,
            application: Application,
            permission_name: str,
            permission_description: str,
    ) -> Permission:
        logger.info(f"Registering permission {application.name}::{permission_name}.")
        permission_data = self.api.mutation(
            name='registerPermission',
            input_value={
                'name': permission_name,
                'description': permission_description,
            },
            body='''
                permission {
                    id
                    name
                    description
                }
                created
                updated
            '''
        )
        logger.info(f"Permission {application.name}::{permission_name} registered: {permission_data}.")
        return Permission(
            application=application,
            permission_id=permission_data['permission']['id'],
            name=permission_data['permission']['name'],
            description=permission_data['permission']['description'],
        )

    def get_all_organizations(self) -> list[Organization]:
        organizations_data = self.api.query(
            name='organizations',
            body='''
                id
                name
                namespace
            ''',
        )
        return [
            Organization(
                organization_id=organization_data['id'],
                name=organization_data['name'],
                namespace=Namespace(organization_data['namespace']),
            ) for organization_data in organizations_data['organizations']
        ]

    def get_logged_user(
            self,
            token: Optional[str],
            secret: Optional[str],
    ) -> Optional[User]:
        if not token or not secret:
            return None
        user_data: dict = self.api.query(
            name='userFromCookies',
            variables=[
                ('tokenCookie', 'String!', token),
                ('secretCookie', 'String!', secret),
            ],
            body="""
                id
                name
                isSuperuser
            """,
        )
        if not user_data:
            return None
        return User(
            user_id=user_data['id'],
            name=user_data['name'],
            is_superuser=user_data['isSuperuser'],
        )

    def get_logged_member(
            self,
            token: Optional[str],
            secret: Optional[str],
    ) -> Optional[Member]:
        if not token or not secret:
            return None
        member_data: dict = self.api.query(
            name='memberFromCookies',
            variables=[
                ('tokenCookie', 'String!', token),
                ('secretCookie', 'String!', secret),
            ],
            body="""
                id
                organization {
                    id
                    name
                    namespace
                }
                user {
                    id
                    name
                    isSuperuser
                }
            """,
        )
        if not member_data:
            return None
        user_data = member_data['user']
        organization_data = member_data['organization']
        return Member(
            member_id=member_data['id'],
            organization=Organization(
                organization_id=organization_data['id'],
                name=organization_data['name'],
                namespace=Namespace(organization_data['namespace']),
            ),
            user=User(
                user_id=user_data['id'],
                name=user_data['name'],
                is_superuser=user_data['isSuperuser'],
            ),
        )

    def get_account(
            self,
            application: Application,
            user: User,
    ) -> Optional[Account]:
        user_data = self.api.query(
            name='user',
            variables=[
                ('id', 'ID!', user.user_id),
            ],
            body="""
                accounts {
                    id
                    enabled
                    application {
                        id
                        name
                    }
                    dataJson
                }
            """,
        )
        if not user_data:
            return None
        for account_data in user_data['accounts']:
            if account_data['application']['id'] == application.application_id:
                return Account(
                    account_id=account_data['id'],
                    user=user,
                    application=application,
                    enabled=account_data['enabled'],
                    data=json.loads(account_data['dataJson']),
                )
        return None
