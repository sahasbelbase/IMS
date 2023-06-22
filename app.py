# Importing required modules
import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import url_for
from functools import wraps
from sqlalchemy import asc, or_, desc
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from sqlalchemy.orm import backref


# Creating an instance of the Flask class
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuring the connection to the MySQL database
# 'mysql+mysqlconnector' specifies the database connector to use
# 'root' is the database user and '' is the password
# 'localhost' specifies the database server to connect to
# 'ims_un' is the name of the database to use
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/ims_un'

# Disabling track modifications to avoid warning messages
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creating an instance of the SQLAlchemy class and passing in the Flask app instance
db = SQLAlchemy(app)

# Extension and function for allowing to upload different formats of images.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename):
    return os.path.splitext(filename)[1] if filename else ''

app.config['UPLOAD_FOLDER'] = 'static/staff_images'


#This is a class definition for an inventory, which inherits from the db.Model class.
#This class will define the structure of the database table that will hold information about an inventory item.



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
    serial_no = db.Column(db.String(256), nullable=False, unique=True)
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

    staff_official_info = db.relationship('StaffOfficialInfo', backref=backref('staff_personal', cascade='all, delete', uselist=False))

class StaffOfficialInfo(db.Model):
    __tablename__ = 'staff_official_info'
    staff_official_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    staff_personal_id = db.Column(db.Integer, db.ForeignKey('staff_personal_info.staff_personal_id', ondelete='CASCADE'), unique=True)
    proj_id = db.Column(db.Integer, db.ForeignKey('project.proj_id'))
    project = db.relationship('Project', backref='staff_officials')
    department = db.Column(db.String(256), nullable=False)
    work_email = db.Column(db.String(256), nullable=False)
    call_sign = db.Column(db.String(256), nullable=False)
    un_index_number = db.Column(db.String(256), nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    last_working_date = db.Column(db.Date)
    contract_type = db.Column(db.String(256), nullable=False)
    grade = db.Column(db.String(256), nullable=False)
    designation = db.Column(db.String(256), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    history = db.relationship('StaffOfficialHistory', backref=backref('official_info', cascade='all, delete', uselist=False))

class StaffOfficialHistory(db.Model):
    __tablename__ = 'staff_official_history'
    id = db.Column(db.Integer, primary_key=True)
    staff_official_id = db.Column(db.Integer, db.ForeignKey('staff_official_info.staff_official_id', ondelete='CASCADE'))
    proj_id = db.Column(db.Integer, db.ForeignKey('project.proj_id'))
    project = db.relationship('Project', backref='staff_history')
    department = db.Column(db.String(256), nullable=False)
    work_email = db.Column(db.String(256), nullable=False, unique=True)
    call_sign = db.Column(db.String(256), nullable=False)
    un_index_number = db.Column(db.String(256), nullable=False)
    joining_date = db.Column(db.Date)  # Add the joining_date column here
    last_working_date = db.Column(db.Date)
    contract_type = db.Column(db.String(256), nullable=False)
    grade = db.Column(db.String(256), nullable=False)
    designation = db.Column(db.String(256), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    staff_official = db.relationship('StaffOfficialInfo', backref=backref('history_entries', cascade='all, delete'))



class Project(db.Model):
    __tablename__ = 'project'
    proj_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proj_name = db.Column(db.String(256), nullable=False)
    donor = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Enum('yes', 'no'), nullable=False)
    row_created = db.Column(db.DateTime, nullable=False)
    row_updated_date = db.Column(db.DateTime, nullable=False)


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




def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is logged in
        if not is_user_logged_in():
            # User is not logged in, redirect to the login page
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Function to check if the user is logged in
def is_user_logged_in():
    # Check if 'user_id' key exists in the session
    return 'user_id' in session

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        password = request.form.get('password')

        # Perform the login logic based on the role and password
        if role == 'Admin' and password == 'admin_password':
            # Login successful, store user_id in session
            session['user_id'] = 'admin'
            # Redirect to index.html or desired page
            return redirect(url_for('index'))
        elif role == 'ICT' and password == 'ict_password':
            # Login successful, store user_id in session
            session['user_id'] = 'ict'
            # Redirect to index.html or desired page
            return redirect(url_for('index'))
        elif role == 'Manager' and password == 'manager_password':
            # Login successful, store user_id in session
            session['user_id'] = 'manager'
            # Redirect to index.html or desired page
            return redirect(url_for('index'))
        elif role == 'Operator' and password == 'operator_password':
            # Login successful, store user_id in session
            session['user_id'] = 'operator'
            # Redirect to index.html or desired page
            return redirect(url_for('index'))
        else:
            # Invalid role or password, display error message
            error = 'Invalid role or password'
            return render_template('login.html', error=error)

    # Render the login page
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Perform logout logic, such as clearing session data or cookies
    # Clear the 'user_id' key from the session
    session.pop('user_id', None)
    # Redirect to the login page
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/no_match_found')
def no_match_found():
    return render_template('no_match_found.html')

@app.route('/add_inventory', methods=['GET', 'POST'])
@login_required
def add_inventory():
    # Check if the user has the ICT or Operator role
    if session['user_id'] not in ['ict', 'operator']:
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"

    if request.method == 'POST':
        # Process the form submission
        proj_id = int(request.form['proj_id'])
        equipment = request.form['equipment'].capitalize()
        technical_id = request.form['technical_id']
        asset_id = request.form['asset_id']
        inventory_labeling = request.form['inventory_labeling']
        category = request.form['category'].capitalize()
        item = request.form['item']
        staff_personal_id = int(request.form['staff'])
        staff = StaffPersonalInfo.query.get(staff_personal_id)
        make = request.form['make'].capitalize()
        model = request.form['model']
        serial_no = request.form['serial_no']
        document_type = request.form['document_type']
        document_id = request.form['document_id']
        acquisition_date = request.form['acquisition_date']
        amount = float(request.form['amount'])
        exchange_rate = float(request.form['exchange_rate'])
        amount_in_usd = float(request.form['amount_in_usd'])
        warranty = request.form['warranty']
        location = request.form['location'].capitalize()
        remark = request.form['remark'].capitalize()
        status = request.form['status'].capitalize()
        internal_remark = request.form['internal_remark'].capitalize()
        included_in_hq = request.form['included_in_hq'].capitalize()

        # Check if the project ID exists in the Project table
        project = Project.query.filter_by(proj_id=proj_id).first()
        if project is None:
            return f"Invalid project ID: {proj_id}"

        inventory_item = Inventory(
            proj_id=proj_id,
            project=project,  # Assign the project object to the inventory item
            equipment=equipment,
            technical_id=technical_id,
            asset_id=asset_id,
            inventory_labeling=inventory_labeling,
            category=category,
            item=item,
            staff_personal=staff,
            make=make,
            model=model,
            serial_no=serial_no,
            document_type=document_type,
            document_id=document_id,
            acquisition_date=acquisition_date,
            amount=amount,
            exchange_rate=exchange_rate,
            amount_in_usd=amount_in_usd,
            warranty=warranty,
            location=location,
            remark=remark,
            status=status,
            internal_remark=internal_remark,
            included_in_hq=included_in_hq,
            row_created=datetime.now(),
            row_updated_date=datetime.now()
        )

        db.session.add(inventory_item)
        db.session.commit()

        return redirect('/index')

    projects = Project.query.all()
    staff_members = StaffPersonalInfo.query.all()

    return render_template('add_inventory.html', projects=projects, staff_members=staff_members)

@app.route('/view_inventory')
def view_inventory():
    sort = request.args.get('sort', 'inventory_id')
    order = request.args.get('order', 'asc')

    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of items per page

    query = Inventory.query.join(Project)

    if sort == 'inventory_id':
        if order == 'asc':
            query = query.order_by(Inventory.inventory_id.asc())
        else:
            query = query.order_by(Inventory.inventory_id.desc())

    search_query = request.args.get('search_query', '')

    if search_query:
        query = query.filter(
            or_(
                Inventory.equipment.ilike(f'%{search_query}%'),
                Inventory.technical_id.ilike(f'%{search_query}%'),
                Inventory.asset_id.ilike(f'%{search_query}%'),
                Inventory.inventory_labeling.ilike(f'%{search_query}%'),
                Inventory.category.ilike(f'%{search_query}%'),
                Inventory.item.ilike(f'%{search_query}%'),
                Inventory.make.ilike(f'%{search_query}%'),
                Inventory.model.ilike(f'%{search_query}%'),
                Inventory.serial_no.ilike(f'%{search_query}%'),
                Inventory.document_type.ilike(f'%{search_query}%'),
                Inventory.document_id.ilike(f'%{search_query}%'),
                Inventory.location.ilike(f'%{search_query}%'),
                Inventory.remark.ilike(f'%{search_query}%'),
                Inventory.status.ilike(f'%{search_query}%'),
                Inventory.internal_remark.ilike(f'%{search_query}%')
            )
        )

    inventory_paginate = query.paginate(page=page, per_page=per_page)
    inventory_items = inventory_paginate.items

    if not inventory_items and search_query:
        return render_template('no_match_found.html')
    else:
        return render_template('view_inventory.html', inventory_paginate=inventory_paginate, inventory_items=inventory_items, sort=sort, order=order, search_query=search_query)



#view_inventory_one
@app.route('/view_inventory_one/<int:inventory_id>', methods=['GET'])
def view_inventory_one(inventory_id):
    # Retrieve the inventory item from the database
    inventory_item = Inventory.query.get(inventory_id)
    
    if inventory_item:
        project = db.session.query(Project).get(inventory_item.proj_id)
        return render_template('view_inventory_one.html', inventory_item=inventory_item, project=project)
    else:
        return 'Inventory item not found'
 

@app.route('/update_inventory/<int:inventory_id>', methods=['GET', 'POST'])
@login_required
def update_inventory(inventory_id):
    # Check if the user has the ICT or Operator role
    if session['user_id'] not in ['ict', 'operator']:
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"

    inventory = Inventory.query.get_or_404(inventory_id)

    if request.method == 'POST':
        inventory.proj_id = request.form['proj_id']
        inventory.equipment = request.form['equipment'].capitalize()
        inventory.technical_id = request.form['technical_id']
        inventory.asset_id = request.form['asset_id']
        inventory.inventory_labeling = request.form['inventory_labeling']
        inventory.category = request.form['category']
        inventory.item = request.form['item']
        
        staff_personal_id = request.form['staff']
        if staff_personal_id:
            inventory.staff_personal_id = int(staff_personal_id)
            inventory.staff_personal = StaffPersonalInfo.query.get(inventory.staff_personal_id)
        
        inventory.make = request.form['make'].capitalize()
        inventory.model = request.form['model']
        inventory.serial_no = request.form['serial_no']
        inventory.document_type = request.form['document_type'].capitalize()
        inventory.document_id = request.form['document_id']
        inventory.acquisition_date = request.form['acquisition_date']
        inventory.amount = request.form['amount']
        inventory.exchange_rate = request.form['exchange_rate']
        inventory.amount_in_usd = request.form['amount_in_usd']
        inventory.warranty = request.form['warranty']
        inventory.location = request.form['location'].capitalize()
        inventory.remark = request.form['remark'].capitalize()
        inventory.status = request.form['status'].capitalize()
        inventory.internal_remark = request.form['internal_remark']
        inventory.included_in_hq = request.form['included_in_hq']

        db.session.commit()

        return redirect('/view_inventory_one/{}'.format(inventory.inventory_id))
    
    projects = Project.query.all()
    staff_members = StaffPersonalInfo.query.all()

    return render_template('update_inventory.html', inventory=inventory, projects=projects, staff_members=staff_members)



@app.route('/delete_inventory/<int:inventory_id>')
@login_required
def delete_inventory(inventory_id):
    # Check if the user has the ICT role
    if session['user_id'] != 'ict':
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"

    inventory = Inventory.query.get_or_404(inventory_id)

    db.session.delete(inventory)
    db.session.commit()

    return redirect('/view_inventory')

@app.route('/add_staff', methods=['GET', 'POST'])
@login_required
def add_staff():
    if session['user_id'] not in ['ict', 'operator']:
        return "Unauthorized access"

    if request.method == 'POST':
        proj_id = request.form['proj_id']
        first_name = request.form['first_name'].capitalize()
        last_name = request.form['last_name'].capitalize()
        gender = request.form['gender']
        dob = request.form['dob']
        contact_number = request.form['contact_number']
        personal_email = request.form['personal_email']
        address = request.form['address'].capitalize()
        disability_type = request.form['disability_type'].capitalize()
        emergency_contact_number = request.form['emergency_contact_number']
        department = request.form['department'].capitalize()
        work_email = request.form['work_email']
        call_sign = request.form['call_sign']
        un_index_number = request.form['un_index_number']
        joining_date = request.form['joining_date']
        contract_type = request.form['contract_type'].capitalize()
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
            photo_filename=None,
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

            # Generate the staff_personal_id after committing to the database
            staff_personal_id = staff_personal_info.staff_personal_id

            # Create a new StaffOfficialInfo record
            staff_official_info = StaffOfficialInfo(
                staff_personal_id=staff_personal_id,
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
            db.session.rollback()
            return redirect('/index')

        if 'Image' in request.files:
            file = request.files['Image']
            if file and allowed_file(file.filename):
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



# Route for viewing staff members
@app.route('/view_staff', methods=['GET', 'POST'])
def view_staff():
    search_query = request.args.get('search_query', '')
    sort = request.args.get('sort', 'first_name')  # Default sorting by first name
    order = request.args.get('order', 'asc')  # Default order as ascending

    

    if request.method == 'POST':
        search_query = request.form.get('search_query', '')

        if not search_query:
        # If the search query is empty, redirect to 'no_match_found' page
         return redirect(url_for('no_match_found'))

    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of items per page

    # Create a session
    db_session = db.session

    query = db_session.query(StaffOfficialInfo).join(StaffPersonalInfo)

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

    if not staffs.items and search_query:
        # If no matching staff records found and a search query was entered, redirect to the 'no_match_found' page
        return redirect(url_for('no_match_found'))

    return render_template('view_staff.html', staffs=staffs, search_query=search_query, sort=sort, order=order)



@app.route('/view_staff_one/<int:staff_personal_id>')
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

@app.route('/update_staff/<int:staff_personal_id>', methods=['GET', 'POST'])
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
        staff_personal_info.gender = request.form['gender'].capitalize()
        staff_personal_info.dob = request.form['dob']
        staff_personal_info.contact_number = request.form['contact_number']
        staff_personal_info.personal_email = request.form['personal_email']
        staff_personal_info.address = request.form['address'].capitalize()
        staff_personal_info.disability_type = request.form['disability_type'].capitalize()
        staff_personal_info.emergency_contact_number = request.form['emergency_contact_number']

        # Update staff official info
        staff_official_info.staff_official_id = request.form['staff_official_id']
        staff_official_info.department = request.form['department'].capitalize()
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
        staff_official_info.designation = request.form['designation'].capitalize()

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
            proj_id=project_id,  # Set the proj_id to the updated project ID
            department=staff_official_info.department,
            work_email=staff_official_info.work_email,
            call_sign=staff_official_info.call_sign,
            un_index_number=staff_official_info.un_index_number,
            joining_date=staff_official_info.joining_date,
            last_working_date=staff_official_info.last_working_date,
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


@app.route('/official_history/<int:staff_personal_id>', methods=['GET'])
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
    # Check if the user is logged in
    if not is_user_logged_in():
        # User is not logged in, redirect to the login page
        return redirect(url_for('login'))

    staff_personal_info = StaffPersonalInfo.query.get_or_404(staff_personal_id)

    if staff_personal_info:
        staff_official_info = staff_personal_info.staff_official_info
        if staff_official_info:
            attendance_entries = Attendance.query.filter_by(staff_personal_id=staff_personal_id).all()
            for attendance_entry in attendance_entries:
                attendance_entry.staff_personal_id = None

            for item in staff_official_info:
                db.session.delete(item)

        db.session.delete(staff_personal_info)
        db.session.commit()

    return redirect('/view_staff')


@app.route('/add_projects', methods=['GET', 'POST'])
@login_required
def add_projects():
    # Check if the user has the ICT or Operator role
    if session['user_id'] not in ['ict', 'operator']:
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"


    if request.method == 'POST':
        # Extract the data from the form
        proj_name = request.form['proj_name'].capitalize()
        donor = request.form['donor'].capitalize()
        description = request.form['description'].capitalize()
        is_active = request.form['is_active']
        
        # Create a new Project object with the extracted data
        project = Project(
            proj_name=proj_name,
            donor=donor,
            description=description,
            is_active=is_active,
            row_created = datetime.now(),
            row_updated_date = datetime.now()
        )
        
        db.session.add(project)
        db.session.commit()
        
        return redirect('/index')
    
    return render_template('add_projects.html')


@app.route('/view_projects')
def view_projects():
    search_query = request.args.get('search_query', '')
    sort_order = request.args.get('sort_order', 'asc')  # Default sort order is ascending

    if search_query:
        # Perform the search query to filter the projects
        projects = Project.query.filter(Project.proj_name.ilike(f'%{search_query}%'))

        # If no matching project records found, redirect to the 'no_match_found' page
        if not projects.count():
            return redirect(url_for('no_match_found'))

    else:
        # Retrieve all projects without filtering
        projects = Project.query

    # Sorting
    if sort_order == 'asc':
        projects = projects.order_by(Project.proj_name.asc())
        next_sort_order = 'desc'  # Set the next sort order to descending
    elif sort_order == 'desc':
        projects = projects.order_by(Project.proj_name.desc())
        next_sort_order = 'asc'  # Set the next sort order to ascending

    # Paginate the projects
    projects = projects.paginate(per_page=5)

    return render_template('view_projects.html', projects=projects, search_query=search_query, sort_order=sort_order, next_sort_order=next_sort_order)





@app.route('/update_project/<int:proj_id>', methods=['GET', 'POST'])
@login_required
def update_project(proj_id):
    # Check if the user has the ICT or Operator role
    if session['user_id'] not in ['ict', 'operator']:
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"

    project = Project.query.get_or_404(proj_id)

    if request.method == 'POST':
        # Update the project with the form data
        project.proj_name = request.form['proj_name'].capitalize()
        project.donor = request.form['donor']
        project.description = request.form['description']
        project.is_active = request.form['is_active']
        project.row_updated_date = datetime.now()

        db.session.commit()
        return redirect('/view_projects')

    return render_template('update_projects.html', project=project)


@app.route('/delete_projects/<int:proj_id>', methods=['GET', 'POST'])
@login_required
def delete_project(proj_id):
    
    # Check if the user has the ICT role
    if session['user_id'] != 'ict':
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"
    project = Project.query.get_or_404(proj_id)

    # Delete the project
    db.session.delete(project)
    db.session.commit()

    return redirect('/view_projects')


# Define the route for adding attendance
@app.route('/add_attendance', methods=['GET', 'POST'])
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

@app.route('/view_attendance', methods=['GET'])
@login_required
def view_attendance():
    # Check if the user has the ICT or Operator role
    if session['user_id'] not in ['ict', 'operator']:
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"

    # Get the sorting parameter from the request query parameters
    sort_param = request.args.get('sort', 'latest')

    # Set the default sorting column and order
    sort_column = Attendance.start_date
    sort_order = desc

    if sort_param == 'name':
        # Sort by staff's first name
        sort_column = StaffPersonalInfo.first_name
        if 'sort_order' in session and session['sort_order'] == 'asc':
            # Toggle the sorting order if 'sort_order' session variable exists and is set to 'asc'
            sort_order = desc
            session['sort_order'] = 'desc'
        else:
            sort_order = asc
            session['sort_order'] = 'asc'
    else:
        # Reset the sorting order if the sorting parameter is not 'name'
        if 'sort_order' in session:
            del session['sort_order']

    # Query all attendances with the desired sorting
    attendances = Attendance.query.join(StaffPersonalInfo).order_by(sort_order(sort_column)).paginate(page=1, per_page=10)

    # Render the template with the attendances
    return render_template('view_attendance.html', attendances=attendances)


@app.route('/search_attendance', methods=['GET'])
@login_required
def search_attendance():
    # Check if the user has the ICT or Operator role
    if session['user_id'] not in ['ict', 'operator']:
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"

    search_query = request.args.get('search_query', '')

    if not search_query:
        # Empty search query, redirect to the 'no_match_found' page
        return redirect('/no_match_found')

    # Query the attendances with the desired search
    attendances = Attendance.query.join(StaffPersonalInfo).filter(
        or_(
            StaffPersonalInfo.first_name.ilike(f'%{search_query}%'),
            StaffPersonalInfo.last_name.ilike(f'%{search_query}%')
        )
    ).paginate(page=1, per_page=10)

    # Render the template with the attendances and search query
    if attendances.total == 0:
        # No matches found, redirect to the 'no_match_found' page
        return redirect('/no_match_found')
    else:
        return render_template('view_attendance.html', attendances=attendances, search_query=search_query)




@app.route('/update_attendance/<int:att_id>', methods=['GET', 'POST'])
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
@app.route('/delete_attendance/<int:att_id>', methods=['GET', 'POST'])
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



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)