from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    
    facts = relationship("Fact", back_populates="document")
    failures = relationship("Failure", back_populates="document")

class Failure(Base):
    __tablename__ = "failures"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"))
    error_type = Column(String)
    raw_output = Column(Text)
    context = Column(Text)
    
    document = relationship("Document", back_populates="failures")

class Fact(Base):
    __tablename__ = "facts"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"))
    statement = Column(Text)
    evidence = Column(Text)
    page_number = Column(Integer)
    
    document = relationship("Document", back_populates="facts")
    
class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    fact1_id = Column(Integer, ForeignKey("facts.id"))
    fact2_id = Column(Integer, ForeignKey("facts.id"))
    relationship_type = Column(String) # "corroborates", "contradicts", "reconciled"
    explanation = Column(Text)
    
    fact1 = relationship("Fact", foreign_keys=[fact1_id])
    fact2 = relationship("Fact", foreign_keys=[fact2_id])
