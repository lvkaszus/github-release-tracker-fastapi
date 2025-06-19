from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base

class Release(Base):
    __tablename__ = 'releases'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    tag_name = Column(String(32))
    published_at = Column(DateTime)
    html_url = Column(Text)
