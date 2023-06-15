from app import db

class Project(db.Model):
    __tablename__ = 'project'
    proj_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proj_name = db.Column(db.String(256), nullable=False)
    donor = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Enum('yes', 'no'), nullable=False)
    row_created = db.Column(db.DateTime, nullable=False)
    row_updated_date = db.Column(db.DateTime, nullable=False)