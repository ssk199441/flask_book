from flask import Flask, request
from flask_restful import Api, Resource
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from marshmallow import Schema, fields
from flask_apispec import FlaskApiSpec, MethodResource, marshal_with, doc, use_kwargs
from models import db, BookModel


APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config.update({
    'APISPEC_SPEC': APISpec(
        title='Awesome Project',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})

API = Api(APP)
db.init_app(APP)
DOCS = FlaskApiSpec(APP)


@APP.before_first_request
def create_table():
    '''Takes in a number n, returns the square of n'''
    db.create_all()


class AwesomeResponseSchema(Schema):
    '''Takes in a number n, returns the square of n'''

    message = fields.Str(default='Success')


class AwesomeRequestSchema(Schema):
    '''Takes in a number n, returns the square of n'''
    api_type = fields.String(required=True, description="API type of awesome API")


class BooksView(MethodResource, Resource):
    '''
    parser = reqparse.RequestParser()
    parser.add_argument('name',
        type=str,
        required=True,
        help = "Can't leave blank"
    )
    parser.add_argument('price',
        type=float,
        required=True,
        help = "Can't leave blank"
    )
    parser.add_argument('author',
        type=str,
        required=True,
        help = "Can't leave blank"
    )'''
    def getBooks(self):
        """getBooks"""
        print("Intentionally wriritng ")
        return

    @doc(description='My First GET Awesome API.', tags=['Awesome'])
    @marshal_with(AwesomeResponseSchema)  # marshalling
    def get(self):
        """Get Books"""
        books = BookModel.query.all()
        return {'Books': list(x.json() for x in books)}

    @doc(description='My First GET Awesome API.', tags=['Awesome'])
    @use_kwargs(AwesomeRequestSchema, location=('json'))
    @marshal_with(AwesomeResponseSchema)  # marshalling
    def post(self):
        """Post Books"""
        data = request.get_json()
        # data = BooksView.parser.parse_args()
        print("New book got added", data['name'])
        new_book = BookModel(data['name'], data['price'], data['author'])
        db.session.add(new_book)
        db.session.commit()
        return new_book.json(), 201


class BookView(Resource):
    '''
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help = "Can't leave blank"
        )
    parser.add_argument('author',
        type=str,
        required=True,
        help = "Can't leave blank"
        )'''

    @marshal_with(AwesomeResponseSchema)
    def get(self, name):
        '''Takes in a number n, returns the square of n'''
        book = BookModel.query.filter_by(name=name).first()
        if book:
            # if book found return it
            return book.json()
        return {'message': 'book not found'}, 404

    @marshal_with(AwesomeResponseSchema)
    def put(self, name):
        '''Takes in a number n, returns the square of n'''
        data = request.get_json()
        # data = BookView.parser.parse_args()

        book = BookModel.query.filter_by(name=name).first()

        if book:
            # Get data from price and author
            book.price = data["price"]
            book.author = data["author"]
        else:
            # Store in bookModel
            book = BookModel(name=name, **data)

        db.session.add(book)
        db.session.commit()

        return book.json()

    @marshal_with(AwesomeResponseSchema)
    def delete(self, name):
        '''Takes in a number n, returns the square of n'''
        book = BookModel.query.filter_by(name=name).first()

        if book:
            # if book is found, Store
            db.session.delete(book)
            db.session.commit()
            assert book, "deleted book"
            return {'message': 'Deleted'}
        else:
            # return error
            return {'message': 'book not found'}, 404


API.add_resource(BooksView, '/books')
API.add_resource(BookView, '/book/<string:name>')
DOCS.register(BooksView)

APP.debug = True
if __name__ == '__main__':
    APP.run(host='localhost', port=5000)
