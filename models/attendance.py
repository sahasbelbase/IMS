from app import db


class Attendance(db.Model):
    __tablename__ = 'attendance'

    att_id = db.Column(db.Integer, primary_key=True)
    staff_personal_id = db.Column(db.Integer, db.ForeignKey('staff_personal_info.staff_personal_id'), nullable=False)
    leave_type = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    remarks = db.Column(db.String(100))
    row_created = db.Column(db.DateTime)
    row_updated_date = db.Column(db.DateTime)

    staff_personal = db.relationship('StaffPersonalInfo', backref=db.backref('attendance', uselist=False))

    def __init__(self, staff_personal_id, leave_type, start_date, end_date, remarks, row_created, row_updated_date):
        self.staff_personal_id = staff_personal_id
        self.leave_type = leave_type
        self.start_date = start_date
        self.end_date = end_date
        self.remarks = remarks
        self.row_created = row_created
        self.row_updated_date = row_updated_date
