import os
from flask import Blueprint, request, redirect, render_template, url_for, session
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from werkzeug.utils import secure_filename



staff_bp = Blueprint('staff', __name__)
from models.staff import StaffPersonalInfo, StaffOfficialInfo, Project, StaffOfficialHistory
from app import app, allowed_file, db, login_required

@staff_bp.route('/add_staff', methods=['GET', 'POST'])
@login_required
def add_staff():
    if session['user_id'] not in ['ict', 'operator']:
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"

    if request.method == 'POST':
        proj_id = request.form['proj_id']
        first_name = request.form['first_name'].capitalize()
        last_name = request.form['last_name'].capitalize()
        gender = request.form['gender']
        dob = request.form['dob']
        contact_number = request.form['contact_number']
        personal_email = request.form['personal_email']
        address = request.form['address']
        disability_type = request.form['disability_type']
        emergency_contact_number = request.form['emergency_contact_number']
        department = request.form['department']
        work_email = request.form['work_email']
        call_sign = request.form['call_sign']
        un_index_number = request.form['un_index_number']
        joining_date = request.form['joining_date']
        contract_type = request.form['contract_type']
        grade = request.form['grade']
        designation = request.form['designation']

        # Check if the project ID exists in the Project table
        project = Project.query.filter_by(proj_id=proj_id).first()
        if project is None:
            return f"Invalid project ID: {proj_id}"

        # Create a new StaffPersonalInfo record
        staff_personal_info = StaffPersonalInfo(
            first_name=first_name,
            last_name=last_name,
            photo_filename=None,  # Set the initial value to None
            gender=gender,
            dob=dob,
            contact_number=contact_number,
            personal_email=personal_email,
            address=address,
            disability_type=disability_type,
            emergency_contact_number=emergency_contact_number
        )

        # Add the staff_personal_info record to the session
        db.session.add(staff_personal_info)

        try:
            # Commit the changes to the database
            db.session.commit()

            # Create a new StaffOfficialInfo record
            staff_official_info = StaffOfficialInfo(
                staff_personal_id=staff_personal_info.staff_personal_id,
                proj_id=proj_id,
                department=department,
                work_email=work_email,
                call_sign=call_sign,
                un_index_number=un_index_number,
                joining_date=joining_date,
                contract_type=contract_type,
                grade=grade,
                designation=designation,
                created_date=datetime.now()
            )

            # Add the staff_official_info record to the session
            db.session.add(staff_official_info)

            # Commit the changes to the database
            db.session.commit()
        except IntegrityError:
            # Handle the foreign key constraint failure
            db.session.rollback()
            return redirect('/index')

        # Check if the POST request has a file part
        if 'Image' in request.files:
            file = request.files['Image']

            # Check if the file has an allowed extension
            if file and allowed_file(file.filename):
                # Generate the file name
                filename = f"{first_name}_{last_name}_{contact_number}.{file.filename.rsplit('.', 1)[1].lower()}"
                file_path = os.path.join('static/staff_images', filename)
                file.save(file_path)

                # Update the photo_filename column in staff_personal_info
                staff_personal_info.photo_filename = filename

                # Commit the changes to the database
                db.session.commit()

        return redirect('/index')

    projects = Project.query.all()
    return render_template('add_staff.html', projects=projects, staff_personal_info=None)


@staff_bp.route('/view_staff')
def view_staff():
    search_query = request.args.get('search_query', '')
    sort = request.args.get('sort', 'first_name')  # Default sorting by first name
    order = request.args.get('order', 'asc')  # Default order as ascending

    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of items per page

    query = StaffOfficialInfo.query.join(StaffPersonalInfo)

    if search_query:
        query = query.filter(
            or_(
                StaffPersonalInfo.first_name.ilike(f'%{search_query}%'),
                StaffPersonalInfo.last_name.ilike(f'%{search_query}%'),
                StaffOfficialInfo.department.ilike(f'%{search_query}%'),
                StaffPersonalInfo.contact_number.ilike(f'%{search_query}%'),
                StaffOfficialInfo.work_email.ilike(f'%{search_query}%'),
                StaffOfficialInfo.call_sign.ilike(f'%{search_query}%'),
                StaffOfficialInfo.un_index_number.ilike(f'%{search_query}%'),
                StaffOfficialInfo.contract_type.ilike(f'%{search_query}%'),
                StaffOfficialInfo.grade.ilike(f'%{search_query}%'),
                StaffOfficialInfo.designation.ilike(f'%{search_query}%')
            )
        )

    # Determine the column to sort by
    if sort == 'first_name':
        column = StaffPersonalInfo.first_name
    elif sort == 'last_name':
        column = StaffPersonalInfo.last_name
    elif sort == 'contact_number':
        column = StaffPersonalInfo.contact_number
    elif sort == 'department':
        column = StaffOfficialInfo.department
    else:
        column = StaffPersonalInfo.first_name  # Default sorting by first name

    # Apply sorting based on the column and order
    if order == 'asc':
        query = query.order_by(column.asc())
    else:
        query = query.order_by(column.desc())

    staffs = query.paginate(page=page, per_page=per_page)

    return render_template('view_staff.html', staffs=staffs, search_query=search_query, sort=sort, order=order)


@staff_bp.route('/view_staff_one/<int:staff_personal_id>')
def view_staff_one(staff_personal_id):
    staff_official_info = StaffOfficialInfo.query.filter_by(staff_personal_id=staff_personal_id).first()
    project_name = None
    profile_picture = None

    if staff_official_info:
        project = Project.query.get(staff_official_info.proj_id)
        if project:
            project_name = project.proj_name
        else:
            project_name = "Project not found"

        staff_personal = staff_official_info.staff_personal

        if staff_personal.photo_filename:
            profile_picture = url_for('static', filename=f'staff_images/{staff_personal.photo_filename}')

    return render_template(
        'view_staff_one.html',
        staffofficial=staff_official_info,
        staffpersonal=staff_personal,
        project_name=project_name,
        profile_picture=profile_picture
    )

@staff_bp.route('/update_staff/<int:staff_personal_id>', methods=['GET', 'POST'])
@login_required
def update_staff(staff_personal_id):
    staff_official_info = StaffOfficialInfo.query.filter_by(staff_personal_id=staff_personal_id).first()

    # Check if the user has the ICT or Operator role
    if session['user_id'] not in ['ict', 'operator']:
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return render_template('unauthorized.html')  # Update to your unauthorized page template

    if staff_official_info is None:
        # Staff with the given staff_personal_id doesn't exist
        return "Staff not found"

    staff_personal_info = staff_official_info.staff_personal

    if request.method == 'POST':
        # Update staff personal info
        staff_personal_info.first_name = request.form['first_name'].capitalize()
        staff_personal_info.last_name = request.form['last_name'].capitalize()
        staff_personal_info.gender = request.form['gender']
        staff_personal_info.dob = request.form['dob']
        staff_personal_info.contact_number = request.form['contact_number']
        staff_personal_info.personal_email = request.form['personal_email']
        staff_personal_info.address = request.form['address']
        staff_personal_info.disability_type = request.form['disability_type']
        staff_personal_info.emergency_contact_number = request.form['emergency_contact_number']

        # Update staff official info
        staff_official_info.staff_official_id = request.form['staff_official_id']
        staff_official_info.department = request.form['department']
        staff_official_info.work_email = request.form['work_email']
        staff_official_info.call_sign = request.form['call_sign']
        staff_official_info.un_index_number = request.form['un_index_number']
        staff_official_info.joining_date = datetime.strptime(request.form['joining_date'], '%Y-%m-%d')
        last_working_date_str = request.form['last_working_date']
        if last_working_date_str.strip():
            staff_official_info.last_working_date = datetime.strptime(last_working_date_str, '%Y-%m-%d')
        else:
            staff_official_info.last_working_date = None
        staff_official_info.contract_type = request.form['contract_type']
        staff_official_info.grade = request.form['grade']
        staff_official_info.designation = request.form['designation']

        # Update project name
        project_id = request.form['proj_id']
        project = Project.query.get(project_id)
        if project:
            staff_official_info.project = project

        # Check if a new profile picture file was uploaded
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '':
                # Save the new profile picture with a secure filename
                filename = secure_filename(f"{staff_personal_info.first_name}_{staff_personal_info.last_name}_{staff_personal_info.contact_number}.{file.filename.rsplit('.', 1)[1].lower()}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                staff_personal_info.photo_filename = filename

        db.session.commit()

        # Create a new entry in StaffOfficialHistory
        staff_official_history = StaffOfficialHistory(
            staff_official_id=staff_official_info.staff_official_id,
            joining_date=staff_official_info.joining_date,
            last_working_date=datetime.now().date().strftime("%Y-%m-%d"),
            department=staff_official_info.department,
            work_email=staff_official_info.work_email,
            call_sign=staff_official_info.call_sign,
            un_index_number=staff_official_info.un_index_number,
            contract_type=staff_official_info.contract_type,
            grade=staff_official_info.grade,
            designation=staff_official_info.designation
        )

        db.session.add(staff_official_history)
        db.session.commit()

        # Redirect to the index page
        return redirect(url_for('index'))

    # Fetch projects from the database
    projects = Project.query.all()

    return render_template('update_staff.html', staff_personal_info=staff_personal_info, staff_official_info=staff_official_info, projects=projects)




@staff_bp.route('/official_history/<int:staff_personal_id>', methods=['GET'])
def official_history(staff_personal_id):
    # Retrieve staff personal info and staff official info from the database
    staff_personal_info = StaffPersonalInfo.query.get(staff_personal_id)
    staff_official_info = StaffOfficialInfo.query.filter_by(staff_personal_id=staff_personal_id).first()

    # Retrieve staff official history from the database
    staff_official_history = StaffOfficialHistory.query.filter_by(staff_official_id=staff_official_info.staff_official_id).all()

    # Retrieve the project from the staff official info
    project = staff_official_info.project

    return render_template('official_history.html', staff_personal_info=staff_personal_info,
                           staff_official_info=staff_official_info, staff_official_history=staff_official_history,
                           project=project)


@app.route('/delete_staff/<int:staff_personal_id>')
@login_required
def delete_staff(staff_personal_id):
    # Check if the user has the ICT role
    if session['user_id'] != 'ict':
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"

    staff_personal_info = StaffPersonalInfo.query.get_or_404(staff_personal_id)

    if staff_personal_info:
        staff_official_info = staff_personal_info.staff_official_info
        if staff_official_info:
            db.session.delete(staff_official_info)

        db.session.delete(staff_personal_info)
        db.session.commit()

    return redirect('/view_staff')
