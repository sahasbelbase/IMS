# Importing required modules
import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime




# Creating an instance of the Flask class
app = Flask(__name__)

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

#Extension and function for allowing to upload different formats of images.
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#This is a class definition for an inventory, which inherits from the db.Model class.
#This class will define the structure of the database table that will hold information about an inventory item.

class Inventory(db.Model):
    inventory_id = db.Column(db.Integer, primary_key=True)
    proj_id = db.Column(db.Integer, db.ForeignKey('project.proj_id'))
    project = db.relationship('Project', backref='inventory_items')
    equipment = db.Column(db.String(256), nullable=False)
    technical_id = db.Column(db.String(256), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'))
    staff = db.relationship('Staff', backref='inventory_items')
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
    included_in_hq = db.Column(db.Enum('yes', 'no','disposal'), nullable=False)
    row_created = db.Column(db.DateTime, default=datetime.utcnow)
    row_updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#This class will define the structure of the database table that will hold information about an staff table
class Staff(db.Model):
    staff_id = db.Column(db.Integer, primary_key=True)
    proj_id = db.Column(db.Integer, db.ForeignKey('project.proj_id'), name='proj_id')
    project = db.relationship('Project', backref='staff_members')
    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    work_email = db.Column(db.String(256), nullable=False)
    personal_email = db.Column(db.String(256), nullable=False)
    contact_number = db.Column(db.String(256), nullable=False)
    emergency_contact_number = db.Column(db.String(256), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    disability_type = db.Column(db.String(256), nullable=False)
    department = db.Column(db.String(256), nullable=False)
    call_sign = db.Column(db.String(256), nullable=False)
    un_index_number = db.Column(db.String(256), nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    last_working_date = db.Column(db.Date, nullable=True)
    contract_type = db.Column(db.String(256), nullable=False)
    grade = db.Column(db.String(256), nullable=False)
    designation = db.Column(db.String(256), nullable=False)
    row_created_date = db.Column(db.DateTime)
    row_updated_date = db.Column(db.DateTime)

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
class Attendance(db.Model):
    att_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    leave_type = db.Column(db.Enum('Full Day', 'First Half', 'Second Half', 'Sick Leave'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    remarks = db.Column(db.String(256), nullable=False)
    row_created = db.Column(db.DateTime, nullable=False)
    row_updated_date = db.Column(db.DateTime, nullable=False)
    staff = db.relationship('Staff', backref=db.backref('attendances'))



# Define the route for the index page
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_inventory', methods=['GET', 'POST'])
@app.route('/add_inventory/<int:inventory_id>', methods=['GET', 'POST'])
def add_inventory(inventory_id=None):
    if inventory_id is not None:
        inventory_item = Inventory.query.get(inventory_id)
    else:
        inventory_item = None

    if request.method == 'POST':
        # Process the form submission
        proj_id = int(request.form['proj_id'])
        equipment = request.form['equipment']
        technical_id = request.form['technical_id']
        proj_id = int(request.form['proj_id'])
        equipment = request.form['equipment']
        technical_id = request.form['technical_id']
        asset_id = request.form['asset_id']
        inventory_labeling = request.form['inventory_labeling']
        category = request.form['category']
        item = request.form['item']
        staff_id = int(request.form['staff'])  # Changed from custodian_id to staff_id
        staff = Staff.query.get(staff_id)  # Changed from custodian to staff
        make = request.form['make']
        model = request.form['model']
        serial_no = request.form['serial_no']
        document_type = request.form['document_type']
        document_id = request.form['document_id']
        acquisition_date = request.form['acquisition_date']
        amount = request.form['amount']
        exchange_rate = request.form['exchange_rate']
        amount_in_usd = request.form['amount_in_usd']
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
            equipment=equipment,
            technical_id=technical_id,
            asset_id=asset_id,
            inventory_labeling=inventory_labeling,
            category=category,
            item=item,
            staff=staff,  # Changed from custodian to staff
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

        return 'Inventory item added!'
    
    projects = Project.query.all()
    staff_members = Staff.query.all()

    return render_template('add_inventory.html', projects=projects, staff_members=staff_members)

  
    
@app.route('/view_inventory')
def view_inventory():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page

    inventory_items = Inventory.query.paginate(page=page, per_page=per_page)

    return render_template('view_inventory.html', inventory_items=inventory_items)


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
def update_inventory(inventory_id):
    inventory = Inventory.query.get_or_404(inventory_id)

    if request.method == 'POST':
        inventory.proj_id = request.form['proj_id']
        inventory.equipment = request.form['equipment']
        inventory.technical_id = request.form['technical_id']
        inventory.asset_id = request.form['asset_id']
        inventory.inventory_labeling = request.form['inventory_labeling']
        inventory.category = request.form['category']
        inventory.item = request.form['item']
        inventory.staff_id = int(request.form['staff'])  # Changed from custodian_id to staff_id
        inventory.staff = Staff.query.get(inventory.staff_id)  # Changed from custodian to staff
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
    staff_members = Staff.query.all()

    return render_template('update_inventory.html', inventory=inventory, projects=projects, staff_members=staff_members)

@app.route('/delete_inventory/<int:inventory_id>')
def delete_inventory(inventory_id):
    inventory = Inventory.query.get_or_404(inventory_id)

    db.session.delete(inventory)
    db.session.commit()

    return redirect('/view_inventory')

@app.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    if request.method == 'POST':
        # Define the route for adding staff

        # Extract the data from the form
        proj_id = request.form['proj_id']
        first_name = request.form['first_name'].capitalize()
        last_name = request.form['last_name'].capitalize()
        gender = request.form['gender']
        dob = request.form['dob']
        work_email = request.form['work_email']
        personal_email = request.form['personal_email']
        contact_number = request.form['contact_number']
        emergency_contact_number = request.form['emergency_contact_number']
        address = request.form['address']
        disability_type = request.form['disability_type']
        department = request.form['department']
        call_sign = request.form['call_sign']
        un_index_number = request.form['un_index_number']
        joining_date = request.form['joining_date']
        last_working_date = request.form['last_working_date']
        contract_type = request.form['contract_type']
        grade = request.form['grade']
        designation = request.form['designation']
        

        # Check if the project ID exists in the Project table
        project = Project.query.filter_by(proj_id=proj_id).first()
        if project is None:
            return f"Invalid project ID: {proj_id}"

        new_staff = Staff(
            proj_id=proj_id,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            dob=dob,
            work_email=work_email,
            personal_email=personal_email,
            contact_number=contact_number,
            emergency_contact_number=emergency_contact_number,
            address=address,
            disability_type=disability_type,
            department=department,
            call_sign=call_sign,
            un_index_number=un_index_number,
            joining_date=joining_date,
            last_working_date=last_working_date,
            contract_type=contract_type,
            grade=grade,
            designation=designation,
            row_created_date=datetime.now(),
            row_updated_date=datetime.now()
        )

        db.session.add(new_staff)
        db.session.commit()

        # Check if the POST request has a file part
        if 'Image' in request.files:
            file = request.files['Image']
            
            # Check if the file has an allowed extension
            if file and allowed_file(file.filename):
                # Save the file with the desired name
                filename = f"{first_name}_{last_name}.{file.filename.rsplit('.', 1)[1].lower()}"
                file_path = os.path.join('static/staff_images', filename)
                file.save(file_path)

        return 'Staff added!'

    projects = Project.query.all()

    return render_template('add_staff.html', projects=projects)





@app.route('/view_staff')
def view_staff():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page

    staffs = Staff.query.paginate(page=page, per_page=per_page)

    return render_template('view_staff.html', staffs=staffs)


@app.route('/view_staff_one/<int:staff_id>')
def view_staff_one(staff_id):
    staff = Staff.query.get_or_404(staff_id)
    project_name = None
    if staff:
        project = Project.query.get(staff.proj_id)
        if project:
            project_name = project.proj_name
    return render_template('view_staff_one.html', staff=staff, project_name=project_name)


@app.route('/update_staff/<int:staff_id>', methods=['GET', 'POST'])
def update_staff(staff_id):
    staff = Staff.query.get_or_404(staff_id)

    if request.method == 'POST':
        staff.proj_id = request.form['proj_id']
        staff.first_name = request.form['first_name'].capitalize()
        staff.last_name = request.form['last_name'].capitalize()
        staff.gender = request.form['gender']
        staff.dob = request.form['dob']
        staff.work_email = request.form['work_email']
        staff.personal_email = request.form['personal_email']
        staff.contact_number = request.form['contact_number']
        staff.emergency_contact_number = request.form['emergency_contact_number']
        staff.address = request.form['address']
        staff.disability_type = request.form['disability_type']
        staff.department = request.form['department']
        staff.call_sign = request.form['call_sign']
        staff.un_index_number = request.form['un_index_number']
        staff.joining_date = request.form['joining_date']
        staff.last_working_date = request.form['last_working_date']
        staff.contract_type = request.form['contract_type']
        staff.grade = request.form['grade']
        staff.designation = request.form['designation']
        staff.row_updated_date = datetime.now()

        db.session.commit()
        return redirect('/view_staff_one/{}'.format(staff.staff_id))

    projects = Project.query.all()
    return render_template('update_staff.html', staff=staff, projects=projects)


@app.route('/delete_staff/<int:staff_id>')
def delete_staff(staff_id):
    staff = Staff.query.get_or_404(staff_id)

    db.session.delete(staff)
    db.session.commit()

    return redirect('/view_staff')

@app.route('/add_projects', methods=['GET', 'POST'])
def add_projects():
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
        
        return 'Project added!'
    
    return render_template('add_projects.html')

# Define the route for viewing projects

@app.route('/view_projects')
def view_projects():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page

    projects = Project.query.paginate(page=page, per_page=per_page)

    return render_template('view_projects.html', projects=projects)




@app.route('/update_project/<int:proj_id>', methods=['GET', 'POST'])
def update_project(proj_id):
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
def delete_project(proj_id):
    project = Project.query.get_or_404(proj_id)

    # Delete the project
    db.session.delete(project)
    db.session.commit()

    return redirect('/view_projects')


# Define the route for adding attendance

@app.route('/add_attendance', methods=['GET', 'POST'])
def add_attendance():
    if request.method == 'POST':
        staff_id = int(request.form['staff_id'])
        leave_type = request.form['leave_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        remarks = request.form['remarks']

        # Check if the staff ID exists in the Staff table
        staff = Staff.query.filter_by(staff_id=staff_id).first()
        if staff is None:
            return f"Invalid staff ID: {staff_id}"

        attendance = Attendance(
            staff_id=staff_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            remarks=remarks,
            row_created=datetime.now(),
            row_updated_date=datetime.now()
        )

        db.session.add(attendance)
        db.session.commit()

        return 'Attendance added!'

    staffs = Staff.query.all()

    return render_template('add_attendance.html', staffs=staffs)




# Update attendance
@app.route('/view_attendance')
def view_attendance():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page

    attendances = Attendance.query.paginate(page=page, per_page=per_page)

    return render_template('view_attendance.html', attendances=attendances)
# Update attendance
@app.route('/update_attendance/<int:att_id>', methods=['GET', 'POST'])
def update_attendance(att_id):
    attendance = Attendance.query.get_or_404(att_id)
    staffs = Staff.query.all()

    if request.method == 'POST':
        staff_id = int(request.form['staff_id'])
        leave_type = request.form['leave_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        remarks = request.form['remarks']

        # Check if the staff ID exists in the Staff table
        staff = Staff.query.filter_by(staff_id=staff_id).first()
        if staff is None:
            return f"Invalid staff ID: {staff_id}"

        attendance.staff_id = staff_id
        attendance.leave_type = leave_type
        attendance.start_date = start_date
        attendance.end_date = end_date
        attendance.remarks = remarks
        attendance.row_updated_date = datetime.now()

        db.session.commit()

        return redirect('/view_attendance')

    return render_template('update_attendance.html', attendance=attendance, staffs=staffs)

# Delete attendance
@app.route('/delete_attendance/<int:att_id>', methods=['GET', 'POST'])
def delete_attendance(att_id):
    attendance = Attendance.query.get_or_404(att_id)

    db.session.delete(attendance)
    db.session.commit()

    return redirect('/view_attendance')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)