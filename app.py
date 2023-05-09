import os
from flask import Flask, render_template, request

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_inventory', methods=['GET', 'POST'])
def add_inventory():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        item = Item(name=name, quantity=quantity)
        db.session.add(item)
        db.session.commit()
        return 'Inventory item added!'
    return render_template('add_inventory.html')
    

@app.route('/view_inventory')
def view_inventory():
    items = Item.query.all()
    return render_template('view_inventory.html', items=items)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        job_title = request.form['job_title']
        employee = Employee(name=name, job_title=job_title)
        db.session.add(employee)
        db.session.commit()
        return 'Employee added!'
    return render_template('add_employee.html')

@app.route('/view_employee')
def view_employee():
    employees = Employee.query.all()
    return render_template('view_employee.html', employees=employees)

if __name__ == '__main__':
    app.run(debug=True)
