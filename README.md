COMP249 Web Technology 2019: Web Development Assignment
===


This year's web application project is an online store.  In this assignment you will
write the code to display products and support a shopping cart on the store.  You are
provided with a basic outline implementation of a web application. You must extend this to meet
the requirements below.

dbschema.py
-----------

Provides the database schema and code to create the database and populate it with
sample data from the file `apparel.csv`.   _Run this file to create your initial database._
This file is used by the tests but you should not need to import it in your code.

All database connections in the project are managed by Bottle and by the test framework.
Using the bottle sqlite plugin, each of your @route handlers takes a first argument
called `db` which will be a valid database connection.  You should use this to access
the database rather than making new connections in your code.   Similarly all of the
functions that need to access the database take a database connection as an argument.

Creating your own connections using the sqlite3 module is likely to lead to errors and
test failures.

The database connection is configured to return Row objects as results; Row objects
behave like dictionaries and can be accessed using the field name as a key.

model.py
--------

Provides the _Model_ component to interface to the database with two functions to get
data from the `products` table.

- `product_get` takes a product id and returns the information about that product
- `product_list` returns a list of products, it has an optional `category` argument which
  if set, returns only products in that category (not used in this project)

The results of these functions are Row objects (or a list of them) and these can be used
like dictionaries, eg:

```python
  product = model.product_get(db, 3)
  print(product['name'], product['description']

  for product in model.product_list(db):
       print(product['name'], product['description']
```

There is nothing for you to complete in this module, you will make use of these functions
in the code in `main.py`.

session.py
----------

Provides an interface to session data.   The database has a table `sessions` that stores user
session data. Each session is identified by a unique sessionid which is sent to the user in a
cookie the first time they visit the site.  Associated with that key is a `data` field that is used
to hold a JSON representation of the shopping cart - a list of dictionaries. 

The shopping cart is stored in the `data` field of the session table as a JSON string.  This is a
way of converting Python data structures to strings.  The Python data structure will be a list
of dictionaries, each one representing one item in the shopping cart. Eg.

```python
    item = {
        'id': <id of item in product table>,
        'quantity': <quantity>,
        'name': <name of item in product table>,
        'cost': <quantity * unit cost of the item>
    }
```

The shopping cart is a list of these dictionaries.  To convert it to JSON before inserting into 
the database you use the `json` module, eg.

```python
  cart = <list of dictionaries>
  data = json.dumps(cart)
  # sql query: UPDATE sessions SET data=? WHERE ...
```

similarly to get the list of dictionaries back from the database:

```python
    
    # sql query: SELECT data FROM sessions WHERE ...
    row = cursor.fetchone()
    cart = json.loads(row['data'])
```

Your task is to write the functions in this module to handle the shopping cart via the sessions table. 

`get_or_create_session(db)`  This function is called to either retrieve the current 
session key from a cookie or create a new session for a new user. 

If a cookie with the name `COOKIE_NAME` (a variable defined in this file) is found in the request
then this function uses the value in the cookie as the sessionid and tries to retrieve session data
from the database.  If it finds a matching sessionid, it returns the sessionid as a result.  

If no cookie is found or if there is no sessionid matching the one in the cookie, a new session is
created.  To do this it makes a new unique identifier (using the `uuid` module, see 
[the notes](http://pwp.stevecassidy.net/bottle/sessions.html)) and inserts it
along with an empty shopping cart into the database.  It then returns this sessionid as the result.

`add_to_cart(db, itemid, quantity)` This function adds a new entry to the shopping cart. It will
need to use `model.product_get` to get details of the product and update the shopping cart
with a new entry.  The function does not return a value.  If the item being added to the cart is 
already in the cart, **then the current quantity is added to the new quantity and the overall
cost is updated** - there should only ever be one entry for a product in the cart.

`get_cart_contents(db)` This function returns the current contents of the shopping cart as a list
of dictionaries.  


main.py
-------

This is the main web application module that provides the different route handlers for the app.  The
version distributed only contains handlers for '/' and '/static/<filename:path>'.  You need to 
extend these and add handlers for other URLs. 

Note that as mentioned before, all handlers take a `db` argument that is a valid database connection,
 they should never make a new connection themselves.  The database connection is managed by the bottle
 sqlite plugin.   
 
You should handle the following URLs:

`/` - you should extend the root page to include a list of all products in the database (product names should
be shown) with each product being linked to a page for that product (see below). 

`/about` - generates a page describing the application that has the same overall design (shares the same 
base HTML structure and CSS stylesheet) and contains the text `"Welcome to WT! The innovative online store"`.

`/category/<cat>` - generates a page containing only the products with the given category.  The category
is stored in the database and can either be 'male' or 'female'.  The display generated by this 
page should have the same structure as the main page but only contain the products in the given
category.   If a category other than 'male' or 'female' is requested (eg `/category/child`) then
a page with no products is returned containing the text `"No products in this category"`.

`/product/<id>` a view of an individual product with the given id.  This page should show all of
the product details including the name, unit_cost and description fields.   Note that the product
description will contain HTML markup so needs to be inserted into the template without escaping 
(using the `{{!description}}` syntax (note the exclaimation mark). 

The product page should also contain a form to add the product to the shopping cart (via a 
POST request to `/cart` - see below)

So, for example, the URL `/product/2` would show all details of the product with id `2` 
(Classic Varsity Top) and include a form that allows the user to add this to their shopping cart. 

`/cart`  a GET request to this URL shows the current contents of the shopping cart. The resulting page
includes a listing of all items in the cart, including their name, quantity and overall cost. It also 
includes the total cost of the items in the cart. 
 
`/cart` a POST request
with variables `product` (the product id, an integer) and `quantity` (an integer) adds a new entry to the 
shopping cart.  The response to the POST request is a **redirect to the cart page `/cart`**. When 
the browser gets this redirect response it will make a new GET request to `/cart` and the
resulting page will contain the updated shopping cart contents.

**COOKIES** All requests to pages in the app should result in the creation of a new session on the first visit. 
This means that for all requests there will be a valid session in the database, either on newly created
or one identified from a session cookie.  This can be achieved by calling `session.get_or_create_session(db)`
at the start of every route handler. 

Views
-----

The initial project has one template (view) called `index.html` that includes `base.html` via the
rebase function.  You will need to extend this and add new views as needed to support the URLs 
mentioned above. 

Static Files
------------

The standard static file handler is included along with a simple CSS file. You may extend this to
achieve a good page layout as you see fit.  You may adapt your first assignment design to the new
app.  Note though that this assignment is not about design and we won't be giving any marks for 
page layout etc. 


Design
------

You will be marked on the overall design of your site, including the usability of your application. 
You may use the CSS stylesheet you made for Assignment 1 as the basis of your design, but you will
need to extend it to handle the additional requirements of this application.  

Usability means that your application should be easy to use - information is presented clearly and
forms are easy to understand.  Navigation between different pages is clear.

Unit and Functional Tests
-------------------------

All of the requirements above are tested automatically via a set of tests in the `tests` 
directory.   Your final mark will be largely based on whether you pass these tests or not.  You can
run each test file individually in PyCharm (right click on the test file and select "Run Unittests in ..."). 


`test_model.py` tests the funcitons in `model.py`, all tests should work already.

`test_session.py`  tests the functions in `session.py`

`test_views.py` provides functional tests of the app by making requests to the URLs defined
above and checking the responses. 

Grading
========

This assignment is worth 20% of the final marks for ITEC649.  The marks will be assigned as follows:

 * Passing all automated tests: 12%
 * Design and usability: 4%
 * Manual assessment of code quality and documentation: 4% 
 
Code quality means well laid out code, good use of variable names, functions and use of appropriate 
 control flow and data structures. 
 
Documentation means that all functions that you write have suitable docstrings and where appropriate you 
 use comments in your code to explain yourself. 
 
 
