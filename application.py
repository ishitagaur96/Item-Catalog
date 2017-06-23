from flask import Flask, render_template, url_for, request
from flask import redirect, flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import *
from flask import session as login_session
import random
import string
from functools import wraps

# IMPORTS FOR Login
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Making Flask App
app = Flask(__name__)

# Getting Client Id from json file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

# Creating session
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

# Returns Home Page


@app.route('/')
def home():
    categories = session.query(Category).all()
    items = session.query(Items).all()
    if 'username' not in login_session:
        return render_template(
                                'catalog.html',
                                categories=categories,
                                items=items)
    else:
        return render_template(
                                'catalogprivate.html',
                                categories=categories,
                                items=items)

# Return Category Items


@app.route('/catalog/<path:category_name>/items')
def getCategoryItems(category_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category=category)
    count = items.count()
    if 'username' not in login_session:
        return render_template(
                                'items.html',
                                category=category.name,
                                categories=categories,
                                items=items,
                                count=count)
    else:
        return render_template(
                                'itemsprivate.html',
                                category=category.name,
                                categories=categories,
                                items=items,
                                count=count)

# Return Category Item Discription


@app.route('/catalog/<path:category_name>/<path:category_item>')
def getItemDetail(category_name, category_item):
    item = session.query(Items).filter_by(name=category_item).one()
    categories = session.query(Category)
    if 'username' not in login_session:
        return render_template(
                                'itemdetails.html',
                                item=item,
                                category=category_name,
                                categories=categories)
    else:
        return render_template(
                                'itemdetailsprivate.html',
                                item=item,
                                category=category_name,
                                categories=categories)

# Checks if the user is logged in or not


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect('/login')
    return decorated_function


# Logged Users Can Make Changes

# Create New Item


@app.route('/catalog/new', methods=['GET', 'POST'])
@login_required
def newCatalog():
    if request.method == 'POST':
        newCategory = Category(
                                name=request.form['name'],
                                user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash('Category Successfully Added!')
        return redirect(url_for('home'))
    else:
        return render_template('newcategory.html')

# Edit a Category


@app.route('/catalog/<path:category_name>/edit', methods=['GET', 'POST'])
@login_required
def editCategory(category_name):
    editedCategory = session.query(Category).filter_by(
                                name=category_name).one()
    category = session.query(Category).filter_by(name=category_name).one()
    # See if the logged in user is the owner of item
    creator = getUserInfo(editedCategory.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("""You cannot edit this item.
            This item belongs to %s""" % creator.name)
        return redirect(url_for('home'))
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        session.commit()
        flash('Category Item Successfully Edited!')
        return redirect(url_for('home'))
    else:
        return render_template(
                                'editcategory.html',
                                categories=editedCategory,
                                category=category)

# Delete a Category


@app.route('/catalog/<path:category_name>/delete', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_name):
    deletecategory = session.query(Category).filter_by(
                    name=category_name).one()
    deleteItems = session.query(Items).filter_by(
                    category_id=deletecategory.id).all()
    # See if the logged in user is the owner of item
    creator = getUserInfo(deletecategory.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("""You cannot delete this item.
            This item belongs to %s""" % creator.name)
        return redirect(url_for('home'))
    if request.method == 'POST':
        for deleteItem in deleteItems:
            session.delete(deleteItem)
        session.delete(deletecategory)
        flash('Category Successfully Deleted! '+deletecategory.name)
        session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('deletecategory.html', category=deletecategory)

# Returns Json


@app.route('/catalog.json')
def categoryJson():
    rand = random.randrange(1, int(session.query(Items).count())+1)
    row = session.query(Items).filter_by(id=rand).one()
    return jsonify(Item=row.serialize)

# Google Login


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = access_token
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # see if user exists, if it doesn't make a new one

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += """ style="width: 300px; height: 300px;
                border-radius: 150px;-webkit-border-radius: 150px;
                -moz-border-radius: 150px;"> """
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Google Disconnect


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = redirect(url_for('home'))
        flash("You are now logged out.")
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.secret_key = 'My_Secret_Key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
