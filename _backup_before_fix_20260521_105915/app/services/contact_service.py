"""
聯絡消息業務邏輯
"""
from sqlalchemy.orm import Session
from app.models.contact import ContactMessage
import logging

logger = logging.getLogger(__name__)


class ContactService:
    """聯絡業務邏輯"""
    
    @staticmethod
    def create_contact_message(
        db: Session,
        name: str,
        email: str,
        phone: str,
        message_type: str,
        subject: str,
        message: str
    ) -> ContactMessage:
        """建立聯絡消息"""
        contact = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            message_type=message_type,
            subject=subject,
            message=message,
            status="New"
        )
        
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        logger.info(f"新聯絡消息: {contact.id} - {message_type}")
        return contact
