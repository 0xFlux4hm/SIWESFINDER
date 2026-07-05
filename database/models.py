"""
Database models for SIWES Hunter NG
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
import json


@dataclass
class Job:
    """
    Job opportunity model
    """
    title: str
    company: str
    hash: str
    location: Optional[str] = None
    stipend: Optional[str] = None
    deadline: Optional[datetime] = None
    application_link: Optional[str] = None
    source: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    job_type: Optional[str] = None
    remote: bool = False
    rank_score: float = 0.0
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    sent_to_channel: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'stipend': self.stipend,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'application_link': self.application_link,
            'source': self.source,
            'description': self.description,
            'requirements': self.requirements,
            'job_type': self.job_type,
            'remote': self.remote,
            'rank_score': self.rank_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def telegram_message(self) -> str:
        """Format as Telegram message"""
        from config.constants import EMOJIS
        
        message = f"""
{EMOJIS['alert']} NEW OPPORTUNITY

{EMOJIS['company']} Company:
{self.company}

{EMOJIS['position']} Position:
{self.title}

{EMOJIS['location']} Location:
{self.location or 'Not specified'}

{EMOJIS['money']} Stipend:
{self.stipend or 'Not specified'}

{EMOJIS['star']} Match Score:
{self.rank_score:.1f}/100
"""
        if self.application_link:
            message += f"\n{EMOJIS['link']} Apply: {self.application_link}"
        
        if self.deadline:
            message += f"\n{EMOJIS['calendar']} Deadline: {self.deadline.strftime('%Y-%m-%d')}"
        
        message += "\n\n━━━━━━━━━━━━━━"
        
        return message


@dataclass
class User:
    """
    Telegram user model
    """
    telegram_id: int
    id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    interests: Optional[str] = None
    subscribed: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'location': self.location,
            'interests': self.interests,
            'subscribed': self.subscribed,
        }
    
    def get_interests(self) -> List[str]:
        """Get interests as list"""
        if self.interests:
            return json.loads(self.interests)
        return []
    
    def set_interests(self, interests: List[str]):
        """Set interests from list"""
        self.interests = json.dumps(interests)


@dataclass
class Alert:
    """
    Alert notification model
    """
    user_id: int
    job_id: int
    id: Optional[int] = None
    sent_at: Optional[datetime] = None
    read: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'read': self.read,
        }


@dataclass
class Setting:
    """
    User settings model
    """
    user_id: int
    id: Optional[int] = None
    notification_frequency: str = 'all'
    preferred_locations: Optional[str] = None
    preferred_roles: Optional[str] = None
    min_stipend: int = 0
    email_notifications: bool = True
    telegram_notifications: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def get_preferred_locations(self) -> List[str]:
        """Get preferred locations as list"""
        if self.preferred_locations:
            return json.loads(self.preferred_locations)
        return []
    
    def set_preferred_locations(self, locations: List[str]):
        """Set preferred locations from list"""
        self.preferred_locations = json.dumps(locations)
    
    def get_preferred_roles(self) -> List[str]:
        """Get preferred roles as list"""
        if self.preferred_roles:
            return json.loads(self.preferred_roles)
        return []
    
    def set_preferred_roles(self, roles: List[str]):
        """Set preferred roles from list"""
        self.preferred_roles = json.dumps(roles)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'notification_frequency': self.notification_frequency,
            'preferred_locations': self.get_preferred_locations(),
            'preferred_roles': self.get_preferred_roles(),
            'min_stipend': self.min_stipend,
            'email_notifications': self.email_notifications,
            'telegram_notifications': self.telegram_notifications,
        }
