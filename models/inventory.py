from app import db
from datetime import datetime



class Inventory(db.Model):
    __tablename__ = 'inventory'
    inventory_id = db.Column(db.Integer, primary_key=True)
    proj_id = db.Column(db.Integer, db.ForeignKey('project.proj_id'))
    project = db.relationship('Project', backref='inventory_items')
    equipment = db.Column(db.String(256), nullable=False)
    technical_id = db.Column(db.String(256), nullable=False)
    staff_personal_id = db.Column(db.Integer, db.ForeignKey('staff_personal_info.staff_personal_id'))
    staff_personal = db.relationship('StaffPersonalInfo', backref='inventory_items')
    asset_id = db.Column(db.String(256), nullable=False)
    inventory_labeling = db.Column(db.String(256), nullable=False)
    category = db.Column(db.String(256), nullable=False)
    item = db.Column(db.String(256), nullable=False)
    make = db.Column(db.String(256), nullable=False)
    model = db.Column(db.String(256), nullable=False)
    serial_no = db.Column(db.String(256), nullable=False)
    document_type = db.Column(db.String(256), nullable=False)
    document_id = db.Column(db.String(256), nullable=False)
    acquisition_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    exchange_rate = db.Column(db.Float, nullable=False)
    amount_in_usd = db.Column(db.Float, nullable=False)
    warranty = db.Column(db.String(256), nullable=False)
    location = db.Column(db.String(256), nullable=False)
    remark = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(256), nullable=False)
    internal_remark = db.Column(db.String(256), nullable=False)
    included_in_hq = db.Column(db.Enum('yes', 'no', 'disposal'), nullable=False)
    row_created = db.Column(db.DateTime, default=datetime.utcnow)
    row_updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
