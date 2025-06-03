from flask import Blueprint

my_blueprint = Blueprint('my_blueprint', __name__)

@my_blueprint.route('/some_route')
def some_function():
          return "Hello from the blueprint!"