from flask import Blueprint, render_template, request, redirect, session

from datetime import datetime


attendance_bp = Blueprint('attendance', __name__)
from models.attendance import Attendance
from models.staff import StaffPersonalInfo
from app import login_required, db 

# Define the route for adding attendance
@attendance_bp.route('/add_attendance', methods=['GET', 'POST'])
@login_required
def add_attendance():
    # Check if the user has the ICT or Operator role
    if session['user_id'] not in ['ict', 'operator']:
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"

    if request.method == 'POST':
        # Check if the staff_personal_id field is present in the form
        if 'staff_personal_id' not in request.form:
            # The user did not submit the staff_personal_id field in the form, so return an error message.
            return "Please enter a staff_personal_id"

        # Convert the staff_personal_id field to an integer
        staff_personal_id = int(request.form['staff_personal_id'])

        # Check if the staff_personal_id exists in the StaffPersonalInfo table
        staff_personal_info = StaffPersonalInfo.query.get(staff_personal_id)
        if staff_personal_info is None:
            # The staff_personal_id is not in the database, so return an error message.
            return f"Invalid staff_personal_id: {staff_personal_id}"

        # Get the leave_type, start_date, end_date, and remarks fields from the form
        leave_type = request.form['leave_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        remarks = request.form['remarks']

        # Create a new Attendance record
        attendance = Attendance(
            staff_personal_id=staff_personal_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            remarks=remarks,
            row_created=datetime.now(),
            row_updated_date=datetime.now()
        )

        # Save the Attendance record to the database
        db.session.add(attendance)
        db.session.commit()

        # Redirect to the index page
        return redirect('/index')

    # Get all of the staff personal info records
    staff_personal_infos = StaffPersonalInfo.query.all()

    # Render the template
    return render_template('add_attendance.html', staff_personal_infos=staff_personal_infos)

# Update attendance

@attendance_bp.route('/view_attendance')
def view_attendance():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of items per page
    search_query = request.args.get('search')

    if search_query:
        # Perform the search query to filter the attendance records
        attendances = Attendance.query.join(StaffPersonalInfo).filter(
            (Attendance.staff_personal_id == StaffPersonalInfo.staff_personal_id) &
            (StaffPersonalInfo.name.ilike(f'%{search_query}%'))
        ).order_by(Attendance.att_id.desc()).paginate(page=page, per_page=per_page)
    else:
        # Retrieve all attendance records without filtering
        attendances = Attendance.query.order_by(Attendance.att_id.desc()).paginate(page=page, per_page=per_page)

    return render_template('view_attendance.html', attendances=attendances, search_query=search_query)


@attendance_bp.route('/update_attendance/<int:att_id>', methods=['GET', 'POST'])
@login_required
def update_attendance(att_id):
    # Check if the user has the ICT role
    if session['user_id'] not in ['ict', 'operator']:
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"

    attendance = Attendance.query.get_or_404(att_id)
    staff_personal_infos = StaffPersonalInfo.query.all()

    if request.method == 'POST':
        staff_personal_id = request.form['staff_personal_id']
        leave_type = request.form['leave_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        remarks = request.form['remarks']

        attendance.staff_personal_id = staff_personal_id
        attendance.leave_type = leave_type
        attendance.start_date = start_date
        attendance.end_date = end_date
        attendance.remarks = remarks

        db.session.commit()

        return redirect('/view_attendance')

    return render_template('update_attendance.html', attendance=attendance, staff_personal_infos=staff_personal_infos)


# Delete attendance
@attendance_bp.route('/delete_attendance/<int:att_id>', methods=['GET', 'POST'])
@login_required
def delete_attendance(att_id):
    # Check if the user has the ICT role
    if session['user_id'] != 'ict':
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"
    attendance = Attendance.query.get_or_404(att_id)

    db.session.delete(attendance)
    db.session.commit()

    return redirect('/view_attendance')
