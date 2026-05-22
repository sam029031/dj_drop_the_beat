"""聯絡消息業務邏輯"""
from sqlalchemy.orm import Session
from app.models.contact import ContactMessage

class ContactService:
    @staticmethod
    def create_contact_message(db: Session, name: str, email: str, phone: str, message_type: str, subject: str, message: str) -> ContactMessage:
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
        return contact

    @staticmethod
    def submit_message(db: Session, name: str, email: str, phone: str, message_type: str, message: str, user_id: int | None = None, subject: str | None = None) -> ContactMessage:
        subject = subject or ("廠商贊助查詢" if message_type == "sponsor_inquiry" else "個人意見回饋")
        return ContactService.create_contact_message(db, name, email, phone, message_type, subject, message)
