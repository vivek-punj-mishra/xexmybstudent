from exmyb_app import db
from datetime import datetime

from exmyb_app.helper.enum_handler import LeadStatus


class LeadsModel(db.Model):
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    lead_owner = db.Column(db.String(128))
    lead_owner_email = db.Column(db.String(128))
    first_assignee_sdr = db.Column(db.String(128))
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    title = db.Column(db.String(255))
    email = db.Column(db.String(128))
    designation = db.Column(db.String(64))
    country_code = db.Column(db.String(8))
    mobile_number = db.Column(db.String(20))
    website = db.Column(db.String(128))
    company = db.Column(db.String(128))
    industry = db.Column(db.String(512))
    annual_revenue = db.Column(db.Numeric(19, 2))
    project_name = db.Column(db.String(255))
    lead_source = db.Column(db.String(128))
    lead_status = db.Column(db.String(128), default=LeadStatus.PENDING.value)
    lead_interest = db.Column(db.String(128))
    pan_no_of_account = db.Column(db.String(64))
    currency = db.Column(db.String(32), default='INR')
    preferred_language = db.Column(db.String(64))
    notes = db.Column(db.Text)
    reference = db.Column(db.Text)
    sku = db.Column(db.String(64))
    expected_timeline = db.Column(db.String(128))
    expected_budget = db.Column(db.String(128))
    street = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    zip_code = db.Column(db.String(32))
    country = db.Column(db.String(255))
    description = db.Column(db.Text)
    fb_campaign = db.Column(db.String(255))
    linkedin_campaign = db.Column(db.String(255))
    project_id = db.Column(db.Integer)
    zoho_crm_lead_id = db.Column(db.String(64), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow())
    created_by = db.Column(db.Integer)
    updated_by = db.Column(db.Integer)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete()
        db.session.commit()

    @classmethod
    def find_by_zoho_id(cls, zoho_id):
        return cls.query.filter_by(zoho_crm_lead_id=zoho_id).first()