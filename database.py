from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'

    id = Column(String, primary_key=True)  # Gmail message ID
    thread_id = Column(String, index=True)  # Gmail thread ID
    sender = Column(String)
    recipient = Column(String)
    subject = Column(String)
    date = Column(DateTime)
    body = Column(Text)

    def __repr__(self):
        return f"<Email(subject={self.subject}, sender={self.sender})>"

# Create SQLite engine
engine = create_engine('sqlite:///emails.db', echo=True)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

# Create tables
def init_db():
    Base.metadata.create_all(engine)
