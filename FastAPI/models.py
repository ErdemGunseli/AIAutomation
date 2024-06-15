from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Boolean

from database import Base
from enums import MessageType, AutomationResult


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, index=True, unique=True, nullable=False)
    postcode = Column(String, nullable=False)
    password = Column(String, nullable=False)

    messages = relationship("Message", back_populates="user")
    automations = relationship("Automation", back_populates="user")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    # null if system message that applies to all users:
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    type = Column(Enum(MessageType), nullable=False, index=True)
    text = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), index=True)

    user = relationship("User", back_populates="messages")


class Automation(Base):
    __tablename__ = "automations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=True, default=False)
    # How often the automation condition must be checked (in seconds):
    check_interval = Column(Integer, nullable=False)
    # When the automation condition was last checked:
    last_check = Column(DateTime, server_default=func.now(), index=True)
    # When the automation was created:
    timestamp = Column(DateTime, server_default=func.now(), index=True)

    user = relationship("User", back_populates="automations")
    logs = relationship("AutomationLog", back_populates="automation")


class AutomationLog(Base):
    __tablename__ = "automation_logs"
    id = Column(Integer, primary_key=True)
    automation_id = Column(Integer, ForeignKey("automations.id"), nullable=False, index=True)
    description = Column(String, nullable=False)
    result = Column(Enum(AutomationResult), nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), index=True)

    automation = relationship("Automation", back_populates="logs")