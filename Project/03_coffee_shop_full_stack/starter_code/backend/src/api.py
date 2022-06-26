import os
import dotenv
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db,db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()



# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
# get all drinks from db
@app.route('/drinks')
def get_drinks():
    # get all drinks from db
    drinks = Drink.query.all()
    # convert to list of dicts
    drinks_short = [drink.short() for drink in drinks]
    # return json
    return jsonify({
        'success': True,
        'drinks': drinks_short
    })




'''

@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        # get all drinks from db
        drinks = Drink.query.order_by(Drink.id).all()
        # convert to list of dicts
        drinks_long = [drink.long() for drink in drinks]
        # return json
        return jsonify({
            'success': True,
            'drinks': drinks_long
        })
    except:
        abort(422)



'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(pay_load):
#    get data from request
    data = request.get_json()

    if 'title' not in data or 'recipe' not in data:
        abort(422)
    #destructure data
    title,recipe = data['title'],data['recipe']
    
    try:
        if isinstance(recipe, dict):
            new_drink = Drink(title=title, recipe=json.dumps([recipe]))
        else:
            new_drink = Drink(title=title, recipe=json.dumps(recipe))
        # insert new drink into db
        new_drink.insert()
        # get new drink 
        drinks_long= [new_drink.long()]
        # return json
        return jsonify({
            'success': True,
            'drinks': drinks_long
        })
    except:
        db.session.rollback()
        raise AuthError({
            'code': 'duplicates drink title',
            'description': 'Drink title already exists.'
        },422)
    finally:
        db.session.close()
        

        



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(token, id):
    # get data from request
    data = request.get_json()
    # check if data is valid
    if 'title' not in data or 'recipe' not in data:
        abort(422)
    # get drink from db
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    # check if drink exists
    if not drink:
        abort(404)
    # destructure title and recipe
    title, recipe = data['title'], data['recipe']
    
    if title:
        drink.title = title
    
    if recipe:
        drink.recipe = json.dumps(recipe)
    # add to db
    drink.update()
    # get new drink from db
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    # convert to dict
    drink = drink.long()
    # return json
    return jsonify({
        'success': True,
        'drinks': [drink]
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(token, id):
    # get drink from db
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    # check if drink exists
    if not drink:
        abort(404)
    # delete drink
    drink.delete()
    # return json
    return jsonify({
        'success': True,
        'delete': id
    })

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
# implementing 404 errors
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

# implementing error for internal server error
@app.errorhandler(500)
def error_handler(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code



def getll():
    drinks = Drink.query.all()
    # convert to list of dicts
    drinks_short = [drink.short() for drink in drinks]
    return drinks_short

print(getll())
