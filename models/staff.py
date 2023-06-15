from datetime import datetime
from app import db




class StaffPersonalInfo(db.Model):
    __tablename__ = 'staff_personal_info'
    staff_personal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)
    photo_filename = db.Column(db.String(256), nullable=True)
    gender = db.Column(db.String(256), nullable=False)
    dob = db.Column(db.String(256), nullable=False)
    contact_number = db.Column(db.String(256), nullable=False, unique=True)
    personal_email = db.Column(db.String(256), nullable=False, unique=True)
    address = db.Column(db.String(256), nullable=False)
    disability_type = db.Column(db.String(256), nullable=False)
    emergency_contact_number = db.Column(db.String(256), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    staff_official_info = db.relationship('StaffOfficialInfo', backref='official_info', uselist=False)

class StaffOfficialInfo(db.Model):
    __tablename__ = 'staff_official_info'
    staff_official_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    staff_personal_id = db.Column(db.Integer, db.ForeignKey('staff_personal_info.staff_personal_id', ondelete='CASCADE'), unique=True)
    proj_id = db.Column(db.Integer, db.ForeignKey('project.proj_id'))
    project = db.relationship('Project', backref='staff_officials')
    department = db.Column(db.String(256), nullable=False)
    work_email = db.Column(db.String(256), nullable=False, unique=True)
    call_sign = db.Column(db.String(256), nullable=False)
    un_index_number = db.Column(db.String(256), nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    last_working_date = db.Column(db.Date)
    contract_type = db.Column(db.String(256), nullable=False)
    grade = db.Column(db.String(256), nullable=False)
    designation = db.Column(db.String(256), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    staff_personal = db.relationship('StaffPersonalInfo', backref='staff_official', uselist=False)

class StaffOfficialHistory(db.Model):
    __tablename__ = 'staff_official_history'
    id = db.Column(db.Integer, primary_key=True)
    staff_official_id = db.Column(db.Integer, db.ForeignKey('staff_official_info.staff_official_id', ondelete='CASCADE'))
    proj_id = db.Column(db.Integer, db.ForeignKey('project.proj_id'))
    department = db.Column(db.String(256), nullable=False)
    work_email = db.Column(db.String(256), nullable=False)
    call_sign = db.Column(db.String(256), nullable=False)
    un_index_number = db.Column(db.String(256), nullable=False)
    joining_date = db.Column(db.Date)  # Add the joining_date column here
    last_working_date = db.Column(db.Date)
    contract_type = db.Column(db.String(256), nullable=False)
    grade = db.Column(db.String(256), nullable=False)
    designation = db.Column(db.String(256), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    staff_official = db.relationship('StaffOfficialInfo', backref='history', uselist=False)
