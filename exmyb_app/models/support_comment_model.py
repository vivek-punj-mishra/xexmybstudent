from exmyb_app import db
from datetime import datetime

class SupportComments(db.Model):
    __table_name__ = 'support_comments'

    id = db.Column(db.Integer, primary_key=True)
    customer_support_id = db.Column(db.Integer, db.ForeignKey('customer_supports.id'))
    support_file = db.Column(db.Text, nullable=True)
    upload_type = db.Column(db.String(255), nullable=False)
    attachment_type = db.Column(db.String(255), nullable=False)
    added_by_email = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

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

    def to_json(self):
        not_convert_into_str = ['id', 'created_by', 'updated_by']
        return {col.name: (str(getattr(self, col.name)) if (
                    getattr(self, col.name) is not None and col.name not in not_convert_into_str) else getattr(self, col.name))
                for col in self.__table__.columns if col.name not in ['user_id','created_by', 'updated_by']}

    @classmethod
    def find_by_support_id(cls, customer_support_id):
        return cls.query.order_by(cls.updated_at.desc()).filter_by(customer_support_id=customer_support_id).all()