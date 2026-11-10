from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from MySQLdb import IntegrityError
from db import mysql

contacts = Blueprint('contacts', __name__)


def _form_data():
    return (
        request.form.get('fullname', '').strip(),
        request.form.get('phone', '').strip(),
        request.form.get('email', '').strip(),
    )


@contacts.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts')
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', contacts=data)


@contacts.route('/add_contact', methods=['POST'])
def add_contact():
    fullname, phone, email = _form_data()
    if not email:
        flash('Email is required', 'danger')
        return redirect(url_for('contacts.Index'))
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO contacts (fullname, phone, email) VALUES (%s, %s, %s)",
            (fullname, phone, email))
        mysql.connection.commit()
        flash('Contact Added successfully', 'success')
    except IntegrityError:
        mysql.connection.rollback()
        flash(f'A contact with email {email} already exists', 'danger')
    finally:
        cur.close()
    return redirect(url_for('contacts.Index'))


@contacts.route('/edit/<int:id>')
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE id = %s', (id,))
    contact = cur.fetchone()
    cur.close()
    if contact is None:
        abort(404)
    return render_template('edit-contact.html', contact=contact)


@contacts.route('/update/<int:id>', methods=['POST'])
def update_contact(id):
    fullname, phone, email = _form_data()
    if not email:
        flash('Email is required', 'danger')
        return redirect(url_for('contacts.get_contact', id=id))
    cur = mysql.connection.cursor()
    cur.execute('SELECT id FROM contacts WHERE id = %s', (id,))
    if cur.fetchone() is None:
        cur.close()
        abort(404)
    try:
        cur.execute("""
            UPDATE contacts
            SET fullname = %s,
                email = %s,
                phone = %s
            WHERE id = %s
        """, (fullname, email, phone, id))
        mysql.connection.commit()
        flash('Contact Updated Successfully', 'success')
    except IntegrityError:
        mysql.connection.rollback()
        flash(f'A contact with email {email} already exists', 'danger')
        return redirect(url_for('contacts.get_contact', id=id))
    finally:
        cur.close()
    return redirect(url_for('contacts.Index'))


@contacts.route('/delete/<int:id>', methods=['POST'])
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts WHERE id = %s', (id,))
    mysql.connection.commit()
    deleted = cur.rowcount
    cur.close()
    if deleted:
        flash('Contact Removed Successfully', 'success')
    else:
        flash('Contact not found', 'danger')
    return redirect(url_for('contacts.Index'))
