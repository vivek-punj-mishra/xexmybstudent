from exmyb_app import db

class EmailLogging(db.Model):
    __tablename__ ="email_logs"
    id=db.Column(db.Integer,primary_key=True)
    subject=db.Column(db.String(1000))
    from_email=db.Column(db.String(1000))
    ################# comma separated values of email
    to_email=db.Column(db.String(1000))
    body=db.Column(db.String(5000))
    aws_email_message_id=db.Column(db.String(100))
    sent=db.Column(db.Boolean)
    timestamp=db.Column(db.DateTime,server_default=db.func.now())
