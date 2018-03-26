# Imports
import random
import string
import httplib2
import json
import requests

from flask import (Flask,
                   render_template,
                   flash,
                   request,
                   url_for,
                   redirect,
                   jsonify,
                   json,
                   make_response,
                   session as login_session)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databaseSetup import (Base,
                           User,
                           CatalogCategory,
                           CatalogCategoryItem)

from oauth2client.client import (flow_from_clientsecrets,
                                 FlowExchangeError)


CLIENT_ID = json.loads(
    open("client_secrets.json", "r").read())["web"]["client_id"]

app = Flask(__name__)

engine = create_engine('sqlite:///catalogCategoryItems.db')
Base.metadata.bind = engine
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# -----------------------------
# HELPER FUNCTIONS - DB queries
# -----------------------------
def category(category_name):
    '''
    Return an entry from 'catalog_categories' table using 'name' as filter
    Input: category_name
    '''
    return session.query(
        CatalogCategory).filter_by(
            name=category_name).one()


def categories():
    '''
    Return all entries from 'catalog_categories' table sorted by name
    '''
    return session.query(
        CatalogCategory).order_by(
            CatalogCategory.name.asc())


def item(item_name, category_name):
    '''
    Return an entry from 'CatalogCategoryItem' table
    using 'name' and 'category name' as filter
    Input: item_name
           category_name
    '''
    return session.query(
        CatalogCategoryItem).filter_by(
            name=item_name, category_id=category(
                category_name).id).one()


def items(count="all", category_name=None):
    '''
    Return the Items for a Category
    Input: count
           category_name
    '''
    # Execute query for last 10 items added in the database
    if count == "latest":
        return session.query(
            CatalogCategoryItem).order_by(
                CatalogCategoryItem.id.desc()).limit(10)
    # Execute query for items based on a category
    elif category_name:
        # Call method 'category' for getting category ID
        current_category = category(category_name)
        # Return the items bases on a specific category
        return session.query(
            CatalogCategoryItem).filter_by(
                category_id=current_category.id).order_by(
                    CatalogCategoryItem.name.asc())
    # Execute query for all items
    else:
        return session.query(
            CatalogCategoryItem).order_by(
                CatalogCategoryItem.name.asc())


def getUserID(email):
    '''
    Get user object by email from the database 'User'
    input: email
    '''
    try:
        user = session.query(
            User).filter_by(
                email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    '''
    Get user object by user_id from the database User
    input: user_id
    '''
    user = session.query(
        User).filter_by(
            id=user_id).one()
    return user


def createUser(login_session):
    '''
    Create a new user in the database User
    input: login_session
    '''
    new_user = User(
        name=login_session["username"],
        email=login_session["email"],
        picture=login_session["picture"]
    )
    session.add(new_user)
    session.commit()
    user = session.query(
        User).filter_by(
            email=login_session["email"]).one()
    return user.id


# ----------
# API ROUTES
# ----------
@app.route("/catalog/JSON/")
def showCatalogJSON():
    '''
    JSON API for Catalog Categories (GET)
    '''
    json_categories = categories()
    return jsonify(Categories=[i.serialize for i in json_categories])


@app.route('/catalog/<string:category_name>/items/JSON/')
def showCatalogCategoryItemsJSON(category_name):
    '''
    JSON API for Catalog Category Items (GET)
    '''
    json_items = items("all", category_name=category_name)
    return jsonify(CategoryItems=[i.serialize for i in json_items])


@app.route("/catalog/<category_name>/items/<item_name>/JSON/")
def showCatalogCategoryItemInfoJSON(category_name, item_name):
    '''
    # JSON API for item
    '''
    json_item = item(item_name, category_name)
    return jsonify(CategoryItem=json_item.serialize)


# ---------------
# SECURITY ROUTES
# ---------------
@app.route("/login")
def showLogin():
    '''
    Create anti-forgery state token
    '''
    # create an random state string
    state = "".join(random.choice(
        string.ascii_uppercase + string.digits) for x in range(32))
    login_session["state"] = state
    return render_template("login.html", STATE=state)


@app.route("/gconnect", methods=["POST"])
def gconnect():
    '''
    Google+ logon
    '''
    # Validate state token
    if request.args.get("state") != login_session["state"]:
        response = make_response(json.dumps("Invalid State Parameter."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets("client_secrets.json", scope="")
        oauth_flow.redirect_uri = "postmessage"
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(
            json.dumps("Failed to upgrade the authorization code."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s"
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, "GET")[1])

    # If there was an error in the access token info, abort.
    if result.get("error") is not None:
        response = make_response(json.dumps(result.get("error")), 500)
        response.headers["Content-Type"] = "application/json"
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token["sub"]
    if result["user_id"] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Verify that the access token is valid for this app.
    if result["issued_to"] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    stored_access_token = login_session.get("access_token")
    stored_gplus_id = login_session.get("gplus_id")

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            "Current user is already connected."), 200)
        response.headers["Content-Type"] = "application/json"
        return response

    # Store the access token in the session for later use.
    login_session["access_token"] = credentials.access_token
    login_session["gplus_id"] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {"access_token": credentials.access_token, "alt": "json"}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session["username"] = data["name"]
    login_session["picture"] = data["picture"]
    login_session["email"] = data["email"]

    # Add provider to login session
    login_session["provider"] = "google"

    # See if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session["user_id"] = user_id

    output = ""
    output += "<h1>Welcome, "
    output += login_session["username"]
    output += "!</h1>"
    output += '<img src="'
    output += login_session["picture"]
    output += ' " style = "width: 200px; height: 200px;border-radius: \
        150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Welcome %s" % login_session["username"])
    return output


@app.route("/disconnect")
def disconnect():
    '''
    User logoff
    '''
    if "username" in login_session:
        # Google+ disconnect
        gdisconnect()
        del login_session["access_token"]
        del login_session["gplus_id"]
        del login_session["username"]
        del login_session["email"]
        del login_session["picture"]
        del login_session["user_id"]
        del login_session["provider"]
        flash("You have successfully been logged out.")
    else:
        flash("You were not logged in.")
    return redirect(url_for("showCatalog"))


@app.route("/gdisconnect")
def gdisconnect():
    '''
    Google+ - Revoke a current user's token and reset their login_session
    '''
    # Only disconnect a connected user
    access_token = login_session.get("access_token")
    if access_token is None:
        response = make_response(
            json.dumps("Current user not connected."), 401)
        response.headers["Content-Type"] = "application/json"
        return response
    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" % access_token
    h = httplib2.Http()
    result = h.request(url, "GET")[0]
    if result["status"] == "200":
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers["Content-Type"] = "application/json"
    else:
        response = make_response(
            json.dumps("Failed to revoke token for given user."),
            400)
        response.headers["Content-Type"] = "application/json"
    return response


# -------------------------
# CATALOG APP - HTML ROUTES
# -------------------------
@app.route("/")
@app.route("/catalog/")
def showCatalog():
    '''
    The homepage displays all current categories with the latest added items.
    '''
    # Call helper methods 'categories' and 'items'
    current_categories = categories()
    current_items = items(count="latest")

    if current_categories.first() is None:
        flash("Catalog Catagories are not loaded, Please contact Admin!")
    else:
        if current_items.first() is None:
            flash("The Catalog doesn't contain any items!")

    if "username" not in login_session:
        # show public webpage without edit functions
        webpage = "catalogPublic.html"
    else:
        # show webpage with edit functions
        webpage = "catalog.html"

    return render_template(
        webpage, categories=current_categories, items=current_items)


@app.route("/catalog/<string:category_name>/items/")
def showCatalogCategoryItems(category_name):
    '''
    Selecting a specific category shows all the items available
    for that category.
    '''
    # Call helper methods 'categories', 'category' and 'items
    current_categories = categories()
    current_category = category(category_name)
    current_items = items("all", category_name)

    # Check if there are any items to display
    if current_items.first() is None:
        rows = 0
        flash("There are no items for this category to display!")
    else:
        # Count rows, needed for presenting on webpage
        rows = session.query(CatalogCategoryItem).filter_by(
            category_id=current_category.id).count()

    # Check if user has been logged on
    if "username" not in login_session:
        # show public webpage without edit functions
        webpage = "showCategoryItemsPublic.html"
    else:
        # show webpage with edit functions
        webpage = "showCategoryItems.html"

    return render_template(
        webpage, categories=current_categories, items=current_items,
        category_name=category_name, rows=rows)


@app.route('/catalog/<string:category_name>/<string:item_name>/')
def showCatalogCategoryItemInfo(category_name, item_name):
    '''
    Selecting a specific item shows the specific information about that item.
    '''
    # call helper method item
    current_item = item(item_name, category_name)

    if 'username' not in login_session:
        # show public webpage without edit functions
        webpage = "showCategoryItemInfoPublic.html"
    else:
        # show webpage with edit functions
        webpage = "showCategoryItemInfo.html"

    return render_template(webpage, item=current_item)


@app.route('/catalog/add/', methods=['GET', 'POST'])
def newCatalogCategoryItem():
    '''
    Create an item within the catalog.
    The method GET will open the 'newCategoryItem.html' page.
    The method POST will capture the input in the DB and redirect the user to
    the 'showCatalogCategoryItem.html' page
    '''
    # check if user has been logged in, otherwise re-route to login page
    if "username" not in login_session:
        return redirect("/login")

    if request.method == "POST":
        # Call method category for getting ID
        current_category = category(request.form["category"])

        # Create an entry 'CatalogCategoryItem' Table
        newItem = CatalogCategoryItem(
            name=request.form['title'],
            description=request.form['description'],
            category_id=current_category.id,
            user_id=login_session["user_id"])
        session.add(newItem)
        session.commit()

        flash("New Item '%s' Successfully Created" % request.form['title'])
        return redirect(url_for(
            "showCatalogCategoryItems",
            category_name=request.form["category"]))
    else:
        # call helper methode categories
        current_categories = categories()
        return render_template(
            "newCategoryItem.html", categories=current_categories)


@app.route('/catalog/<string:item_name>/edit/', methods=['GET', 'POST'])
def editCatalogCategoryItem(item_name):
    '''
    Edit an item within the catalog
    '''
    # check if user has been logged in, otherwise re-route to login page
    if "username" not in login_session:
        return redirect("/login")

    # Read one entry from 'catalog_category_items' table on filter 'item name'
    item = session.query(CatalogCategoryItem).filter_by(name=item_name).one()

    if request.method == 'POST':
        # call helper method category
        current_category = category(request.form['category'])

        item.name = request.form['title']
        item.description = request.form['description']
        item.category_id = current_category.id
        session.add(item)
        session.commit()
        flash("Item '%s' has been changed!" % request.form['title'])
        return redirect(url_for("showCatalog"))
    else:
        # check if user who is logged in is authorized to edit item
        if login_session["user_id"] != item.user_id:
            flash("You are not authorized to edit item '%s' !" % item_name)
            flash("Please add your own item first.")
            return redirect(url_for("showCatalog"))
        else:
            # call helper method categories
            current_categories = categories()
            return render_template(
                'editCategoryItem.html',
                categories=current_categories, item=item)


@app.route('/catalog/<string:item_name>/delete/', methods=['GET', 'POST'])
def deleteCatalogCategoryItem(item_name):
    '''
    Delete an item.
    '''
    # check if user has been logged in, otherwise re-route to login page
    if "username" not in login_session:
        return redirect("/login")

    # read one entry from 'catalog_category_items' table on filter 'item name'
    item = session.query(CatalogCategoryItem).filter_by(name=item_name).one()

    if request.method == "POST":
        session.delete(item)
        session.commit()
        flash("Item '%s' has been deleted!" % item_name)
        return redirect(url_for("showCatalog"))
    else:
        # check if user who is logged in is authorized to delete item
        if login_session["user_id"] != item.user_id:
            flash("You are not authorized to delete item '%s' !" % item_name)
            flash("Please add your own item first.")
            return redirect(url_for("showCatalog"))
        else:
            return render_template("deleteCategoryItem.html", item=item)


if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
