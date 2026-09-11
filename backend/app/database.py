import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AuditDB(Base):
    __tablename__ = "audits"

    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    source_url = Column(String, nullable=False)
    resolved_url = Column(String, nullable=True)
    source_type = Column(String, nullable=False)
    business_name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    location = Column(String, nullable=True)
    overall_score = Column(Integer, default=0)
    identity_confidence = Column(Float, default=0.0)
    status = Column(String, default="QUEUED")  # QUEUED, COMPLETED, FAILED
    is_demo = Column(Boolean, default=False)
    
    # Serialized structured fields
    scores_json = Column(Text, nullable=True)
    evidence_json = Column(Text, nullable=True)
    opportunity_json = Column(Text, nullable=True)
    website_concept_json = Column(Text, nullable=True)
    quick_win_json = Column(Text, nullable=True)
    whatsapp_message = Column(Text, nullable=True)
    sales_brief_json = Column(Text, nullable=True)
    
    # Artifact paths
    report_pdf_path = Column(String, nullable=True)
    desktop_preview_path = Column(String, nullable=True)
    mobile_preview_path = Column(String, nullable=True)
    quick_win_path = Column(String, nullable=True)
    sales_pack_zip_path = Column(String, nullable=True)

class LeadDB(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    niche = Column(String, index=True)
    location = Column(String, index=True)
    business_name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    maps_url = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    opportunity_flag = Column(String, nullable=True)  # NO_WEBSITE, NO_WHATSAPP, REVIEW_DEFICIT, STRONG_REPUTATION
    opportunity_summary = Column(Text, nullable=True)
    status = Column(String, default="NEW")  # NEW, AUDITED, CONTACTED
    audit_id = Column(String, nullable=True)
    audit_score = Column(Integer, nullable=True)
    
    # Tracking & Follow-up fields
    is_finalized = Column(Boolean, default=False)
    stage = Column(String, default="PITCH_READY")  # PITCH_READY, CONTACTED, FOLLOW_UP, CALL_SCHEDULED, WON, LOST
    notes = Column(Text, nullable=True)
    next_followup = Column(String, nullable=True)
    last_contacted = Column(String, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Auto-migrate new columns if SQLite table already exists
try:
    with engine.connect() as conn:
        cursor = conn.connection.cursor()
        cursor.execute("PRAGMA table_info(leads)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        
        new_cols = {
            "is_finalized": "BOOLEAN DEFAULT 0",
            "stage": "VARCHAR DEFAULT 'PITCH_READY'",
            "notes": "TEXT",
            "next_followup": "VARCHAR",
            "last_contacted": "VARCHAR"
        }
        for col_name, col_type in new_cols.items():
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE leads ADD COLUMN {col_name} {col_type}")
        conn.connection.commit()
except Exception as e:
    print(f"[Database] Migration note: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
