"""
Code for handling sessions in our web application
"""

from bottle import request, response
import uuid
import json

import model
import dbschema

COOKIE_NAME = 'session'


def get_or_create_session(db):
    """Get the current sessionid either from a
    cookie in the current request or by creating a
    new session if none are present.

    If a new session is created, a cookie is set in the response.

    Returns the session key (string)
    """
    if request.get_cookie('session') is not None:
        # Fetch from DB
        session_key = request.get_cookie('session')
        cursor = db.cursor()
        cursor.execute("SELECT sessionid FROM sessions WHERE sessionid=?", (session_key,))
        row = cursor.fetchone()
        if not row:
            # no existing session in database then we will have create a new one (Exception Handling)
            response.delete_cookie('session')
            session_key = str(uuid.uuid4())
            cart = []
            item = {
                'id': '',
                'quantity': 0,
                'name': '',
                'cost': ''
            }
            cart.append(item)
            data = json.dumps(cart)
            cursor = db.cursor()
            cursor.execute("INSERT INTO sessions VALUES (?,?)", (session_key, data))
            db.commit()
            response.set_cookie('session', session_key)
        else:
            session_key = row['sessionid']

    else:
        # Create a new Session and insert it to DB
        session_key = str(uuid.uuid4())
        cart = []
        item = {
            'id': '',
            'quantity': 0,
            'name': '',
            'cost': ''
        }
        # cart.append(item)
        data = json.dumps(cart)
        cursor = db.cursor()
        cursor.execute("INSERT INTO sessions VALUES (?,?)", (session_key, data))
        db.commit()
        response.set_cookie('session', session_key, path="/")
    return session_key


def add_to_cart(db, itemid, quantity):
    """Add an item to the shopping cart"""
    product = model.product_get(db, itemid)
    product_name = product['name']
    product_cost = product['unit_cost']

    session_id = get_or_create_session(db)
    cursor = db.cursor()
    cursor.execute("SELECT sessionid, data FROM sessions WHERE sessionid=?", (session_id,))
    row = cursor.fetchone()
    if row is not None:
        cart = json.loads(row['data'])
        if len(cart) != 0:
            for i in range(len(cart)):
                if str("") in cart[i].values():
                    del cart[i]
                    item = {
                        'id': itemid,
                        'quantity': int(quantity),
                        'name': product_name,
                        'cost': product_cost
                    }
                    cart.append(item)
                    break
                elif str(cart[i]['id']) == str(itemid):
                    cart[i]['quantity'] = int(cart[i]['quantity']) + int(quantity)
                    break
                elif i == len(cart) - 1:
                    item = {
                        'id': itemid,
                        'quantity': int(quantity),
                        'name': product_name,
                        'cost': product_cost
                    }
                    cart.append(item)
                    break
        else:
            item = {
                'id': itemid,
                'quantity': int(quantity),
                'name': product_name,
                'cost': product_cost
            }
            cart.append(item)
        data = json.dumps(cart)
        cursor1 = db.cursor()
        cursor1.execute("UPDATE sessions SET data=? WHERE sessionid=?", (data, session_id))
        db.commit()


def get_cart_contents(db):
    """Return the contents of the shopping cart as
    a list of dictionaries:
    [{'id': <id>, 'quantity': <qty>, 'name': <name>, 'cost': <cost>}, ...]
    """
    session_id = get_or_create_session(db)
    cursor = db.cursor()
    cursor.execute("SELECT data FROM sessions WHERE sessionid=?", (session_id,))
    return json.loads(cursor.fetchone()['data'])
