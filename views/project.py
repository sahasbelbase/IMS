from flask import Blueprint, render_template, request, redirect, session


from datetime import datetime
from sqlalchemy import desc

project_bp = Blueprint('project', __name__)
from models.project import Project
from app import db, login_required

@project_bp.route('/add_projects', methods=['GET', 'POST'])
@login_required
def add_projects():
    # Check if the user has the ICT or Operator role
    if session['user_id'] not in ['ict', 'operator']:
        # User does not have the required role, show an error message or redirect to an unauthorized page
        return "Unauthorized access"


    if request.method == 'POST':
        # Extract the data from the form
        proj_name = request.form['proj_name'].capitalize()
        donor = request.form['donor']
        description = request.form['description']
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

# Define the route for viewing projects

@project_bp.route('/view_projects')
def view_projects():
    search_query = request.args.get('search_query', '')
    sort_order = request.args.get('sort_order', 'asc')  # Default sort order is ascending
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of items per page

    if search_query:
        # Perform the search query to filter the projects
        projects = Project.query.filter(Project.proj_name.ilike(f'%{search_query}%'))
    else:
        # Retrieve all projects without filtering
        projects = Project.query

    # Sort the projects based on the sort order
    if sort_order == 'asc':
        projects = projects.order_by(Project.proj_id.asc())
    elif sort_order == 'desc':
        projects = projects.order_by(desc(Project.proj_id))

    # Paginate the sorted projects
    projects = projects.paginate(page=page, per_page=per_page)

    return render_template('view_projects.html', projects=projects, search_query=search_query, sort_order=sort_order)




@project_bp.route('/update_project/<int:proj_id>', methods=['GET', 'POST'])
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


@project_bp.route('/delete_projects/<int:proj_id>', methods=['GET', 'POST'])
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