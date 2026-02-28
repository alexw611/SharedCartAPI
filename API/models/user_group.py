from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from API.database import Base


class UserGroup(Base):
    __tablename__ = "UserGroups"
    
    userId = Column(BigInteger, ForeignKey("Users.id"), primary_key=True)
    groupId = Column(BigInteger, ForeignKey("Groups.id"), primary_key=True)
    
    user = relationship("User", back_populates="groups")
    group = relationship("Group", back_populates="users")

