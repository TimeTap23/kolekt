"""
Team Collaboration Service
Handles team management, member roles, and collaboration features
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

class TeamRole(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class Permission(Enum):
    CREATE_CONTENT = "create_content"
    EDIT_CONTENT = "edit_content"
    DELETE_CONTENT = "delete_content"
    PUBLISH_CONTENT = "publish_content"
    MANAGE_MEMBERS = "manage_members"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_BILLING = "manage_billing"
    MANAGE_SETTINGS = "manage_settings"

@dataclass
class TeamMember:
    """Team member information"""
    user_id: str
    email: str
    name: str
    role: TeamRole
    joined_at: datetime
    last_active: Optional[datetime] = None
    avatar_url: Optional[str] = None

@dataclass
class Team:
    """Team information"""
    team_id: str
    name: str
    description: Optional[str]
    owner_id: str
    created_at: datetime
    updated_at: datetime
    member_count: int
    plan: str
    settings: Dict[str, Any]

@dataclass
class TeamInvitation:
    """Team invitation"""
    invitation_id: str
    team_id: str
    email: str
    role: TeamRole
    invited_by: str
    invited_at: datetime
    expires_at: datetime
    status: str  # pending, accepted, expired

@dataclass
class ContentApproval:
    """Content approval workflow"""
    approval_id: str
    content_id: str
    team_id: str
    requester_id: str
    approver_id: Optional[str]
    status: str  # pending, approved, rejected
    requested_at: datetime
    approved_at: Optional[datetime]
    comments: Optional[str]

class TeamService:
    """Service for team collaboration features"""
    
    def __init__(self):
        # In production, this would be database tables
        self.teams = {}
        self.team_members = {}
        self.invitations = {}
        self.content_approvals = {}
        self.role_permissions = {
            TeamRole.OWNER: [
                Permission.CREATE_CONTENT,
                Permission.EDIT_CONTENT,
                Permission.DELETE_CONTENT,
                Permission.PUBLISH_CONTENT,
                Permission.MANAGE_MEMBERS,
                Permission.VIEW_ANALYTICS,
                Permission.MANAGE_BILLING,
                Permission.MANAGE_SETTINGS
            ],
            TeamRole.ADMIN: [
                Permission.CREATE_CONTENT,
                Permission.EDIT_CONTENT,
                Permission.DELETE_CONTENT,
                Permission.PUBLISH_CONTENT,
                Permission.MANAGE_MEMBERS,
                Permission.VIEW_ANALYTICS,
                Permission.MANAGE_SETTINGS
            ],
            TeamRole.EDITOR: [
                Permission.CREATE_CONTENT,
                Permission.EDIT_CONTENT,
                Permission.PUBLISH_CONTENT,
                Permission.VIEW_ANALYTICS
            ],
            TeamRole.VIEWER: [
                Permission.VIEW_ANALYTICS
            ]
        }
    
    async def create_team(self, name: str, description: str, owner_id: str, plan: str = "starter") -> Team:
        """Create a new team"""
        try:
            team_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            team = Team(
                team_id=team_id,
                name=name,
                description=description,
                owner_id=owner_id,
                created_at=now,
                updated_at=now,
                member_count=1,
                plan=plan,
                settings={
                    "approval_required": False,
                    "auto_publish": True,
                    "notification_preferences": {
                        "email": True,
                        "slack": False
                    }
                }
            )
            
            self.teams[team_id] = team
            
            # Add owner as first member
            owner_member = TeamMember(
                user_id=owner_id,
                email="owner@example.com",  # Would get from user service
                name="Team Owner",  # Would get from user service
                role=TeamRole.OWNER,
                joined_at=now
            )
            
            self.team_members[team_id] = [owner_member]
            
            logger.info(f"Created team {team_id} with owner {owner_id}")
            return team
            
        except Exception as e:
            logger.error(f"Error creating team: {e}")
            raise
    
    async def get_team(self, team_id: str) -> Optional[Team]:
        """Get team by ID"""
        return self.teams.get(team_id)
    
    async def get_user_teams(self, user_id: str) -> List[Team]:
        """Get all teams a user belongs to"""
        try:
            user_teams = []
            for team_id, members in self.team_members.items():
                if any(member.user_id == user_id for member in members):
                    team = self.teams.get(team_id)
                    if team:
                        user_teams.append(team)
            return user_teams
        except Exception as e:
            logger.error(f"Error getting user teams: {e}")
            return []
    
    async def add_team_member(self, team_id: str, user_id: str, email: str, name: str, role: TeamRole) -> bool:
        """Add a member to a team"""
        try:
            team = self.teams.get(team_id)
            if not team:
                raise ValueError(f"Team {team_id} not found")
            
            # Check if user is already a member
            existing_members = self.team_members.get(team_id, [])
            if any(member.user_id == user_id for member in existing_members):
                raise ValueError(f"User {user_id} is already a member of team {team_id}")
            
            # Add new member
            new_member = TeamMember(
                user_id=user_id,
                email=email,
                name=name,
                role=role,
                joined_at=datetime.utcnow()
            )
            
            existing_members.append(new_member)
            self.team_members[team_id] = existing_members
            
            # Update team member count
            team.member_count = len(existing_members)
            team.updated_at = datetime.utcnow()
            
            logger.info(f"Added member {user_id} to team {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding team member: {e}")
            return False
    
    async def remove_team_member(self, team_id: str, user_id: str, removed_by: str) -> bool:
        """Remove a member from a team"""
        try:
            team = self.teams.get(team_id)
            if not team:
                raise ValueError(f"Team {team_id} not found")
            
            # Check permissions
            if not await self.has_permission(removed_by, team_id, Permission.MANAGE_MEMBERS):
                raise ValueError("Insufficient permissions to remove team member")
            
            # Prevent removing the owner
            if user_id == team.owner_id:
                raise ValueError("Cannot remove team owner")
            
            # Remove member
            existing_members = self.team_members.get(team_id, [])
            existing_members = [m for m in existing_members if m.user_id != user_id]
            self.team_members[team_id] = existing_members
            
            # Update team member count
            team.member_count = len(existing_members)
            team.updated_at = datetime.utcnow()
            
            logger.info(f"Removed member {user_id} from team {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing team member: {e}")
            return False
    
    async def update_member_role(self, team_id: str, user_id: str, new_role: TeamRole, updated_by: str) -> bool:
        """Update a team member's role"""
        try:
            team = self.teams.get(team_id)
            if not team:
                raise ValueError(f"Team {team_id} not found")
            
            # Check permissions
            if not await self.has_permission(updated_by, team_id, Permission.MANAGE_MEMBERS):
                raise ValueError("Insufficient permissions to update member role")
            
            # Prevent changing owner role
            if user_id == team.owner_id:
                raise ValueError("Cannot change team owner role")
            
            # Update member role
            existing_members = self.team_members.get(team_id, [])
            for member in existing_members:
                if member.user_id == user_id:
                    member.role = new_role
                    break
            
            team.updated_at = datetime.utcnow()
            
            logger.info(f"Updated role for member {user_id} in team {team_id} to {new_role}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating member role: {e}")
            return False
    
    async def invite_member(self, team_id: str, email: str, role: TeamRole, invited_by: str) -> TeamInvitation:
        """Invite a new member to the team"""
        try:
            team = self.teams.get(team_id)
            if not team:
                raise ValueError(f"Team {team_id} not found")
            
            # Check permissions
            if not await self.has_permission(invited_by, team_id, Permission.MANAGE_MEMBERS):
                raise ValueError("Insufficient permissions to invite members")
            
            invitation_id = str(uuid.uuid4())
            now = datetime.utcnow()
            expires_at = now + timedelta(days=7)
            
            invitation = TeamInvitation(
                invitation_id=invitation_id,
                team_id=team_id,
                email=email,
                role=role,
                invited_by=invited_by,
                invited_at=now,
                expires_at=expires_at,
                status="pending"
            )
            
            self.invitations[invitation_id] = invitation
            
            logger.info(f"Created invitation {invitation_id} for {email} to team {team_id}")
            return invitation
            
        except Exception as e:
            logger.error(f"Error inviting member: {e}")
            raise
    
    async def accept_invitation(self, invitation_id: str, user_id: str, email: str, name: str) -> bool:
        """Accept a team invitation"""
        try:
            invitation = self.invitations.get(invitation_id)
            if not invitation:
                raise ValueError(f"Invitation {invitation_id} not found")
            
            if invitation.status != "pending":
                raise ValueError(f"Invitation {invitation_id} is not pending")
            
            if invitation.email != email:
                raise ValueError("Email does not match invitation")
            
            if datetime.utcnow() > invitation.expires_at:
                invitation.status = "expired"
                raise ValueError(f"Invitation {invitation_id} has expired")
            
            # Add member to team
            success = await self.add_team_member(
                invitation.team_id,
                user_id,
                email,
                name,
                invitation.role
            )
            
            if success:
                invitation.status = "accepted"
                logger.info(f"Accepted invitation {invitation_id} for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error accepting invitation: {e}")
            return False
    
    async def has_permission(self, user_id: str, team_id: str, permission: Permission) -> bool:
        """Check if user has specific permission in team"""
        try:
            members = self.team_members.get(team_id, [])
            user_member = next((m for m in members if m.user_id == user_id), None)
            
            if not user_member:
                return False
            
            user_permissions = self.role_permissions.get(user_member.role, [])
            return permission in user_permissions
            
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            return False
    
    async def get_team_members(self, team_id: str) -> List[TeamMember]:
        """Get all members of a team"""
        return self.team_members.get(team_id, [])
    
    async def create_content_approval(self, content_id: str, team_id: str, requester_id: str, comments: str = None) -> ContentApproval:
        """Create a content approval request"""
        try:
            approval_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            approval = ContentApproval(
                approval_id=approval_id,
                content_id=content_id,
                team_id=team_id,
                requester_id=requester_id,
                approver_id=None,
                status="pending",
                requested_at=now,
                approved_at=None,
                comments=comments
            )
            
            self.content_approvals[approval_id] = approval
            
            logger.info(f"Created content approval {approval_id} for content {content_id}")
            return approval
            
        except Exception as e:
            logger.error(f"Error creating content approval: {e}")
            raise
    
    async def approve_content(self, approval_id: str, approver_id: str, approved: bool, comments: str = None) -> bool:
        """Approve or reject content"""
        try:
            approval = self.content_approvals.get(approval_id)
            if not approval:
                raise ValueError(f"Approval {approval_id} not found")
            
            if approval.status != "pending":
                raise ValueError(f"Approval {approval_id} is not pending")
            
            # Check if approver has permission
            if not await self.has_permission(approver_id, approval.team_id, Permission.EDIT_CONTENT):
                raise ValueError("Insufficient permissions to approve content")
            
            approval.approver_id = approver_id
            approval.status = "approved" if approved else "rejected"
            approval.approved_at = datetime.utcnow()
            if comments:
                approval.comments = comments
            
            logger.info(f"Content approval {approval_id} {approval.status} by {approver_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error approving content: {e}")
            return False
    
    async def get_pending_approvals(self, team_id: str, user_id: str) -> List[ContentApproval]:
        """Get pending approvals for a team"""
        try:
            if not await self.has_permission(user_id, team_id, Permission.EDIT_CONTENT):
                return []
            
            pending = [
                approval for approval in self.content_approvals.values()
                if approval.team_id == team_id and approval.status == "pending"
            ]
            
            return sorted(pending, key=lambda x: x.requested_at, reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}")
            return []
    
    async def update_team_settings(self, team_id: str, settings: Dict[str, Any], updated_by: str) -> bool:
        """Update team settings"""
        try:
            team = self.teams.get(team_id)
            if not team:
                raise ValueError(f"Team {team_id} not found")
            
            if not await self.has_permission(updated_by, team_id, Permission.MANAGE_SETTINGS):
                raise ValueError("Insufficient permissions to update team settings")
            
            team.settings.update(settings)
            team.updated_at = datetime.utcnow()
            
            logger.info(f"Updated settings for team {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating team settings: {e}")
            return False
    
    async def get_team_analytics(self, team_id: str, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get team analytics"""
        try:
            if not await self.has_permission(user_id, team_id, Permission.VIEW_ANALYTICS):
                return {}
            
            # Mock analytics data
            return {
                "total_members": len(self.team_members.get(team_id, [])),
                "active_members": len([m for m in self.team_members.get(team_id, []) 
                                     if m.last_active and (datetime.utcnow() - m.last_active).days < 7]),
                "content_created": 42,
                "content_published": 38,
                "pending_approvals": len([a for a in self.content_approvals.values() 
                                        if a.team_id == team_id and a.status == "pending"]),
                "engagement_rate": 0.045,
                "top_performer": "John Doe",
                "recent_activity": [
                    {"type": "content_created", "user": "Jane Smith", "time": "2 hours ago"},
                    {"type": "content_published", "user": "John Doe", "time": "4 hours ago"},
                    {"type": "member_joined", "user": "Bob Wilson", "time": "1 day ago"}
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting team analytics: {e}")
            return {}
