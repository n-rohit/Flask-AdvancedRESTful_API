from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required
from security import authenticate, identity

app = Flask(__name__)
app.secret_key = 'nrohit'
api = Api(app)

jwt = JWT(app, authenticate, identity)

items = []

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price",
        type=float,
        required=True,
        help="This Field cannot be left Blank!"
    ) #^ If you have a HTML Form, you can use this RequestParser to go through the Form Fields

    @jwt_required()
    def get(self, name):
        item = next(filter(lambda x: x["name"] == name, items), None)
        return {"item": item}, 200 if item else 404
        
    def post(self, name):
        if next(filter(lambda x: x["name"] == name, items), None):
            return {"message": "An item with name '{}' already exists".format(name)}, 400
        data = Item.parser.parse_args()
        item = {"name": name, "price":data["price"]}
        items.append(item)
        return item, 201

    def delete(self, name):
        global items # We are informing python that the items variable defined below is taken from line 12 above #*  items = []
        items = list(filter(lambda x: x['name'] != name, items)) # Overwriting the existing items [] excluding the item we want to delete
        return {"message": "Item Deleted"}
    
    def put(self, name): #* For both Posting and Updating an Item
        data = Item.parser.parse_args()
        item = next(filter(lambda x: x["name"] == name, items), None)
        if item is None:
            item = {"name": name, "price": data["price"]}
            items.append(item)
        else:
            item.update(data)
        return item


class ItemList(Resource):
    def get(self):
        return {"items":items}

api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')

app.run(port=8000, debug=True)