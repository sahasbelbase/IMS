# Importing required modules
import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import url_for
from functools import wraps
from uuid import uuid4
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

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
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename):
    return os.path.splitext(filename)[1] if filename else ''


#This is a class definition for an inventory, which inherits from the db.Model class.
#This class will define the structure of the database table that will hold information about an inventory item.

class Inventory(db.Model):
    inventory_id = db.Column(db.Integer, primary_key=True)
    proj_id = db.Column(db.Integer, db.ForeignKey('project.proj_id'))
    project = db.relationship('Project', backref='inventory_items')
    equipment = db.Column(db.String(256), nullable=False)
    technical_id = db.Column(db.String(256), nullable=False)
    staff_personal_id = db.Column(db.Integer, db.ForeignKey('staff_personal_info.staff_personal_id'))
    staff_personal = db.relationship('StaffPersonalInfo', backref=db.backref('inventory_items'))
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


class StaffPersonalInfo(db.Model):
    staff_personal_id = db.Column(db.BigInteger, primary_key=True)
    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)
    gender = db.Column(db.String(256), nullable=False)
    dob = db.Column(db.String(256), nullable=False)
    contact_number = db.Column(db.String(256), nullable=False)
    personal_email = db.Column(db.String(256), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    disability_type = db.Column(db.String(256), nullable=False)
    emergency_contact_number = db.Column(db.String(256), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    staff_official_info = db.relationship('StaffOfficialInfo', backref='official_info', uselist=False)


class StaffOfficialInfo(db.Model):
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

    staff_personal = db.relationship('StaffPersonalInfo', backref='staff_official', uselist=False)


class StaffOfficialHistory(db.Model):
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



class Project(db.Model):
    proj_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proj_name = db.Column(db.String(256), nullable=False)
    doner = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Enum('yes', 'no'), nullable=False)
    row_created = db.Column(db.DateTime, nullable=False)
    row_updated_date = db.Column(db.DateTime, nullable=False)

# This is a class definition for an Attendance, which inherits from the db.Model class.
# This class will define the structure of the database table that will hold information about attendance.
#This class will define the structure of the database table that will hold information about attendance.
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
        equipment = request.form['equipment']
        technical_id = request.form['technical_id']
        asset_id = request.form['asset_id']
        inventory_labeling = request.form['inventory_labeling']
        category = request.form['category']
        item = request.form['item']
        staff_personal_id = int(request.form['staff'])
        staff = StaffPersonalInfo.query.get(staff_personal_id)
        make = request.form['make']
        model = request.form['model']
        serial_no = request.form['serial_no']
        document_type = request.form['document_type']
        document_id = request.form['document_id']
        acquisition_date = request.form['acquisition_date']
        amount = float(request.form['amount'])
        exchange_rate = float(request.form['exchange_rate'])
        amount_in_usd = float(request.form['amount_in_usd'])
        warranty = request.form['warranty']
        location = request.form['location']
        remark = request.form['remark']
        status = request.form['status']
        internal_remark = request.form['internal_remark']
        included_in_hq = request.form['included_in_hq']

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



@app.route('/view_inventory', methods=['GET'])
def view_inventory():
    order = request.args.get('order', 'asc')  # Get the order parameter from the URL

    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of items per page

    if order == 'asc':
        inventory_paginate = Inventory.query.join(Project).order_by(Inventory.inventory_id.asc()).paginate(page=page, per_page=per_page)
    else:
        inventory_paginate = Inventory.query.join(Project).order_by(Inventory.inventory_id.desc()).paginate(page=page, per_page=per_page)

    search_query = request.args.get('search_query', '')

    # Get the inventory items from the pagination object
    inventory_items = inventory_paginate.items

    return render_template('view_inventory.html', inventory_paginate=inventory_paginate, inventory_items=inventory_items, search_query=search_query)




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
    

@app.route('/search_inventory', methods=['GET'])
def search_inventory():
    search_query = request.args.get('search_query', '')

    # Perform the search query on the inventory items
    inventory_items = Inventory.query.filter(
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
    ).all()

    return render_template('view_inventory.html', inventory_items=inventory_items, search_query=search_query)


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
        inventory.equipment = request.form['equipment']
        inventory.technical_id = request.form['technical_id']
        inventory.asset_id = request.form['asset_id']
        inventory.inventory_labeling = request.form['inventory_labeling']
        inventory.category = request.form['category']
        inventory.item = request.form['item']
        
        staff_personal_id = request.form['staff']
        if staff_personal_id:
            inventory.staff_personal_id = int(staff_personal_id)
            inventory.staff_personal = StaffPersonalInfo.query.get(inventory.staff_personal_id)
        
        inventory.make = request.form['make']
        inventory.model = request.form['model']
        inventory.serial_no = request.form['serial_no']
        inventory.document_type = request.form['document_type']
        inventory.document_id = request.form['document_id']
        inventory.acquisition_date = request.form['acquisition_date']
        inventory.amount = request.form['amount']
        inventory.exchange_rate = request.form['exchange_rate']
        inventory.amount_in_usd = request.form['amount_in_usd']
        inventory.warranty = request.form['warranty']
        inventory.location = request.form['location']
        inventory.remark = request.form['remark']
        inventory.status = request.form['status']
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

        # Generate a unique ID for staff_personal_id
        staff_personal_id = str(uuid4())

        # Check if the project ID exists in the Project table
        project = Project.query.filter_by(proj_id=proj_id).first()
        if project is None:
            return f"Invalid project ID: {proj_id}"

        # Create a new StaffPersonalInfo record
        staff_personal_info = StaffPersonalInfo(
            staff_personal_id=staff_personal_id,
            first_name=first_name,
            last_name=last_name,
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
            # Handle the foreign key constraint failure
            db.session.rollback()
            return "Invalid staff_personal_id"

        # Check if the POST request has a file part
        if 'Image' in request.files:
            file = request.files['Image']

            # Check if the file has an allowed extension
            if file and allowed_file(file.filename):
                # Generate the file name
                filename = f"{first_name}_{last_name}_{contact_number}.{file.filename.rsplit('.', 1)[1].lower()}"
                file_path = os.path.join('static/staff_images', filename)
                file.save(file_path)

        return redirect('/index')

    projects = Project.query.all()

    return render_template('add_staff.html', projects=projects)

@app.route('/view_staff')
def view_staff():
    search_query = request.args.get('search_query', '')
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of items per page

    if search_query:
        staffs = StaffOfficialInfo.query.filter(
            or_(
                StaffOfficialInfo.staff_personal.has(StaffPersonalInfo.first_name.ilike(f'%{search_query}%')),
                StaffOfficialInfo.staff_personal.has(StaffPersonalInfo.last_name.ilike(f'%{search_query}%')),
                StaffOfficialInfo.department.ilike(f'%{search_query}%'),
                StaffOfficialInfo.staff_personal.has(StaffPersonalInfo.contact_number.ilike(f'%{search_query}%')),
                StaffOfficialInfo.work_email.ilike(f'%{search_query}%'),
                StaffOfficialInfo.call_sign.ilike(f'%{search_query}%'),
                StaffOfficialInfo.un_index_number.ilike(f'%{search_query}%'),
                StaffOfficialInfo.contract_type.ilike(f'%{search_query}%'),
                StaffOfficialInfo.grade.ilike(f'%{search_query}%'),
                StaffOfficialInfo.designation.ilike(f'%{search_query}%')
            )
        ).paginate(page=page, per_page=per_page)
    else:
        staffs = StaffOfficialInfo.query.paginate(page=page, per_page=per_page)

    return render_template('view_staff.html', staffs=staffs, search_query=search_query)

@app.route('/view_staff_one/<int:staff_personal_id>')
def view_staff_one(staff_personal_id):
    staff_official_info = StaffOfficialInfo.query.filter_by(staff_personal_id=staff_personal_id).first()
    project_name = None

    if staff_official_info:
        project = Project.query.get(staff_official_info.proj_id)
        if project:
            project_name = project.proj_name
        else:
            project_name = "Project not found"

    return render_template(
        'view_staff_one.html',
        staffofficial=staff_official_info,
        staffpersonal=staff_official_info.staff_personal if staff_official_info else None,
        project_name=project_name,
        first_name=staff_official_info.staff_personal.first_name if staff_official_info else None,
        last_name=staff_official_info.staff_personal.last_name if staff_official_info else None,
        contact_number=staff_official_info.staff_personal.contact_number if staff_official_info else None,
        get_file_extension=get_file_extension  
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
        doner = request.form['doner']
        description = request.form['description']
        is_active = request.form['is_active']
        
        # Create a new Project object with the extracted data
        project = Project(
            proj_name=proj_name,
            doner=doner,
            description=description,
            is_active=is_active,
            row_created = datetime.now(),
            row_updated_date = datetime.now()
        )
        
        db.session.add(project)
        db.session.commit()
        
        return redirect('/index')
    
    return render_template('add_projects.html')

# Define the route for viewing projects

@app.route('/view_projects')
def view_projects():
    search_query = request.args.get('search_query', '')
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of items per page

    if search_query:
        # Perform the search query to filter the projects
        projects = Project.query.filter(Project.proj_name.ilike(f'%{search_query}%')).paginate(page=page, per_page=per_page)
    else:
        # Retrieve all projects without filtering
        projects = Project.query.paginate(page=page, per_page=per_page)

    return render_template('view_projects.html', projects=projects, search_query=search_query)




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
        project.doner = request.form['doner']
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

# Update attendance
@app.route('/view_attendance')
def view_attendance():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of items per page
    search_query = request.args.get('search')

    if search_query:
        # Perform the search query to filter the attendance records
        attendances = Attendance.query.join(StaffPersonalInfo).filter(
            (Attendance.staff_personal_id == StaffPersonalInfo.staff_personal_id) &
            (StaffPersonalInfo.name.ilike(f'%{search_query}%'))
        ).paginate(page=page, per_page=per_page)
    else:
        # Retrieve all attendance records without filtering
        attendances = Attendance.query.paginate(page=page, per_page=per_page)

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