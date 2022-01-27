from exmyb_app import db
from datetime import datetime
import pytz

class UsrVerificationModel(db.Model):
    __tablename__ = 'usr_verification'

    id = db.Column(db.Integer, primary_key=True)
    usr_type = db.Column(db.String(32))
    verification_type = db.Column(db.String(32))
    verification_id = db.Column(db.String(120))
    otp = db.Column(db.String(10), nullable=False)
    otp_time = db.Column(db.DateTime, default=datetime.utcnow())
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_send = db.Column(db.Boolean)
    is_expired = db.Column(db.Boolean, nullable=False)
    message = db.Column(db.Text)
    attempts = db.Column(db.Integer, default=0)

    @classmethod
    def find_otp_by_type_id(cls, verification_id, usr_type):
        return cls.query.filter_by(verification_id=verification_id, usr_type=usr_type).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

