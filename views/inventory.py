from flask import Blueprint, render_template, request, redirect, session


from datetime import datetime
from sqlalchemy import or_


inventory_bp = Blueprint('inventory', __name__)
from models.inventory import Inventory
from models.project import Project
from models.staff_personal_info import StaffPersonalInfo
from app import db
from app import login_required


@inventory_bp.route('/add_inventory', methods=['GET', 'POST'])
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



@inventory_bp.route('/view_inventory')
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

    inventory_paginate = query.paginate(page=page, per_page=per_page)

    search_query = request.args.get('search_query', '')

    inventory_items = inventory_paginate.items

    return render_template('view_inventory.html', inventory_paginate=inventory_paginate, inventory_items=inventory_items, sort=sort, order=order, search_query=search_query)




#view_inventory_one
@inventory_bp.route('/view_inventory_one/<int:inventory_id>', methods=['GET'])
def view_inventory_one(inventory_id):
    # Retrieve the inventory item from the database
    inventory_item = Inventory.query.get(inventory_id)
    
    if inventory_item:
        project = db.session.query(Project).get(inventory_item.proj_id)
        return render_template('view_inventory_one.html', inventory_item=inventory_item, project=project)
    else:
        return 'Inventory item not found'
    

@inventory_bp.route('/search_inventory', methods=['GET'])
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


@inventory_bp.route('/update_inventory/<int:inventory_id>', methods=['GET', 'POST'])
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



@inventory_bp.route('/delete_inventory/<int:inventory_id>')
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

from app import app