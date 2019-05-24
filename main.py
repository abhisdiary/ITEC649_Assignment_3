import random
from bottle import Bottle, template, static_file, request, redirect, HTTPError

import model
import session

app = Bottle()


# # Local Session Saving
# shopping_cart = dict()
#
#
# def add_to_cart(product_id, quantity):
#     if product_id in shopping_cart:
#         shopping_cart[product_id] = int(shopping_cart[product_id]) + int(quantity)
#     else:
#         shopping_cart[product_id] = int(quantity)
#
#
# def get_product_quantity(product_id):
#     for p in shopping_cart:
#         if int(p) == int(product_id):
#             return shopping_cart[p]


# --------------------- routes ---------------------------

@app.route('/')
def index(db):
    session.get_or_create_session(db)
    products = dict()
    products['title'] = "The WT"
    products['product_list'] = model.product_list(db)
    return template('index', products)


@app.route('/about')
def about(db):
    """Generates the about page"""
    session.get_or_create_session(db)
    about_content = dict()
    about_content['title'] = "Welcome to WT! The innovative online store"
    about_content['description'] = "Designed by Roy"
    return template('about', about_content)


@app.route('/category/<cat>')
def category(db, cat):
    """Generates the category page, where products are shown according to the category (male, female) requests"""
    if cat is not None:
        session.get_or_create_session(db)
        products = dict()
        products['product_list'] = model.product_list(db, cat)
        if len(products['product_list']) == 0:
            products['title'] = "No products in this category"
        else:
            products['title'] = "Category: " + cat.capitalize()
        # print(products['product_list'])
        return template('index', products)
    else:
        return HTTPError(404, "There is no content to show!")


@app.route('/product/<id>')
def product(db, id):
    """Return the page with the information of the single product (id)"""
    session.get_or_create_session(db)
    product_individual = dict()
    product_individual['individual_product'] = []
    product_individual['individual_product'].append(model.product_get(db, int(id)))

    # if product_individual['individual_product'][0]['name'] is not None:
    #     product_individual['title'] = product_individual['individual_product'][0]['name']
    #     return template('product_individual', product_individual)
    # else:
    #     return error404(404)
    try:
        product_individual['title'] = product_individual['individual_product'][0]['name']
        return template('product_individual', product_individual)
    except(TypeError, AttributeError):
        # return error404(404)
        return HTTPError(status=404)


@app.route('/cart', method="GET")
def show_cart(db):
    """a GET request to this URL shows the current contents of the shopping cart. The resulting page
includes a listing of all items in the cart, including their name, quantity and overall cost. It also
includes the total cost of the items in the cart."""
    # product_id = request.query.get('item')
    # product_quantity = request.query.get('quantity')
    # add_to_cart(product_id, product_quantity)
    session.get_or_create_session(db)
    cart = dict()
    cart['title'] = "Your Cart: "
    cart['product_list'] = session.get_cart_contents(db)
    return template('cart', cart)


@app.route('/cart', method="POST")
def cart(db):
    """with variables `product` (the product id, an integer) and `quantity` (an integer) adds a new entry to the
shopping cart.  The response to the POST request is a **redirect to the cart page `/cart`**. When
the browser gets this redirect response it will make a new GET request to `/cart` and the
resulting page will contain the updated shopping cart contents."""
    session.get_or_create_session(db)
    product_id = request.forms.get('product')
    product_quantity = request.forms.get('quantity')
    if int(product_quantity) < 0:
        product_quantity = 0
    # add_to_cart(product_id, product_quantity)
    session.add_to_cart(db, product_id, product_quantity)
    # return show_cart(db)
    return redirect("/cart")


@app.route('/static/<filename:path>')
def static(filename):
    return static_file(filename=filename, root='static')


@app.error(404)
def error404(error):
    error_dict = dict()
    error_dict['title'] = "There is No Content Here!"
    error_dict['description'] = "New Collection"
    return template('error', error_dict)


if __name__ == '__main__':
    from bottle.ext import sqlite
    from dbschema import DATABASE_NAME

    # install the database plugin
    app.install(sqlite.Plugin(dbfile=DATABASE_NAME))
    app.run(debug=True, port=8010)
