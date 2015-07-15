from flask import Flask, request
from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal_with
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dev.db"
db = SQLAlchemy(app)
api = Api(app)


value = db.Table('house_value',
    db.Column('value_id', db.Integer, db.ForeignKey('value.value_id')),
    db.Column('house_id', db.Integer, db.ForeignKey('house.house_id'))
)

character_in_film = db.Table('character_in_film',
    db.Column('character_id', db.Integer, db.ForeignKey('character.character_id')),
    db.Column('film_id', db.Integer, db.ForeignKey('film.film_id')),
    db.Column('type', db.Enum('A','M'))
)

character_in_book = db.Table('character_in_book',
    db.Column('character_id', db.Integer, db.ForeignKey('character.character_id')),
    db.Column('book_id', db.Integer, db.ForeignKey('book.book_id')),
    db.Column('type', db.Enum('A','M'))
)

class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    cover_artist_name = db.Column(db.String(255), unique=False)
    publisher = db.Column(db.String(255), unique=False)
    release_date = db.Column(db.String(255), unique=False)
    pages = db.Column(db.String(255), unique=False)
    followed_by_id = db.Column(db.Integer, db.ForeignKey('book.book_id'))
    preceeded_by_id = db.Column(db.Integer, db.ForeignKey('book.book_id'))
    
    #relationships - TODO, fix issued with foreign key. Using the correct one seems to mix up the followed_by and preceeded_by objects
    #Manually swapping the foreign keys below overrides this and outputs correctly (but shouldnt be right!)
    followed_by = db.relationship("Book", foreign_keys=[preceeded_by_id])
    preceeded_by = db.relationship("Book", foreign_keys=[followed_by_id])

    book_pf_fields = {
        'book_id': fields.Integer,
        'name': fields.String,
        'uri': fields.Url('bookresource', absolute=True)
    }

    book_resource_fields = {
        'book_id': fields.Integer,
        'name': fields.String,
        'cover_artist_name': fields.String,
        'publisher': fields.String,
        'release_date': fields.String,
        'pages': fields.String,
        'followed_by': fields.Nested(book_pf_fields),
        'preceeded_by': fields.Nested(book_pf_fields),
        'uri': fields.Url('bookresource', absolute=True)
    } 

    def __init__(self, book_id, name, cover_artist_name, publisher, release_date, pages, preceeded_by_id, followed_by_id):
        self.book_id = book_id
        self.name = name
        self.cover_artist_name = cover_artist_name
        self.publisher = publisher
        self.release_date = release_date
        self.pages = pages
        self.preceeded_by_id = preceeded_by_id
        self.followed_by_id = followed_by_id

class Film(db.Model):
    film_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)
    director = db.Column(db.String(100), unique=False)
    producer = db.Column(db.String(100), unique=False)
    writer = db.Column(db.String(100), unique=False)
    distributor = db.Column(db.String(100), unique=False)
    release_date = db.Column(db.String(100), unique=False)
    rating = db.Column(db.String(100), unique=False)
    running_time = db.Column(db.String(100), unique=False)
    budget = db.Column(db.String(100), unique=False)
    revenue = db.Column(db.String(100), unique=False)
    preceeded_by_id = db.Column(db.Integer, db.ForeignKey('film.film_id'))
    followed_by_id = db.Column(db.Integer, db.ForeignKey('film.film_id'))
    
    #Relationships
    preceeded_by = db.relationship("Film", foreign_keys=[followed_by_id])
    followed_by = db.relationship("Film", foreign_keys=[preceeded_by_id])

    film_pf_fields = {
        'film_id': fields.Integer,
        'name': fields.String,
        'uri': fields.Url('filmresource', absolute=True)
    }

    film_resource_fields = {
        'film_id': fields.Integer,
        'name': fields.String,
        'director': fields.String,
        'producer': fields.String,
        'writer': fields.String,
        'distributor': fields.String,
        'release_date': fields.String,
        'rating': fields.String,
        'running_time': fields.String,
        'budget': fields.String,
        'revenue': fields.String,
        'preceeded_by': fields.Nested(film_pf_fields),
        'followed_by': fields.Nested(film_pf_fields),
        'uri': fields.Url('filmresource', absolute=True)
    }

    def __init__(self, film_id, name, director, producer, writer, distributor, release_date, rating, running_time, budget, revenue, preceeded_by_id, followed_by_id):
        self.film_id = film_id
        self.name = name
        self.director = director
        self.producer = producer
        self.writer = writer
        self.distributor = distributor
        self.release_date = release_date
        self.rating = rating
        self.running_time = running_time
        self.budget = budget
        self.revenue = revenue
        self.preceeded_by_id = preceeded_by_id
        self.followed_by_id = followed_by_id

class Spell(db.Model):
    spell_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)
    incantation = db.Column(db.String(100), unique=False)
    type = db.Column(db.String(100), unique=False)
    light = db.Column(db.String(100), unique=False)
    effect = db.Column(db.String(999), unique=False)

    spell_resource_fields = {
        'spell_id': fields.Integer,
        'name': fields.String,
        'incantation': fields.String,
        'type': fields.String,
        'light': fields.String,
        'effect': fields.String,
        'uri': fields.Url('spellresource', absolute=True)
    }

    def __init__(self, spell_id, name, incantation, type, light, effect):
        self.spell_id = spell_id
        self.name = name
        self.incantation = incantation
        self.type = type
        self.light = light
        self.effect = effect

class Character(db.Model):
    character_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)
    species = db.Column(db.String(100), unique=False)
    gender = db.Column(db.String(100), unique=False)
    hair_colour = db.Column(db.String(100), unique=False)
    eye_colour = db.Column(db.String(100), unique=False)
    wand = db.Column(db.String(100), unique=False)
    patronus = db.Column(db.String(100), unique=False)
    animagus = db.Column(db.String(100), unique=False)
    hogwarts_house_id = db.Column(db.Integer, db.ForeignKey('house.house_id'))

    #Relationships
    films = db.relationship('Film', secondary=character_in_film, backref=db.backref('films', lazy='dynamic'))
    books = db.relationship('Book', secondary=character_in_book, backref=db.backref('books', lazy='dynamic'))
    hogwarts_house = db.relationship('House', foreign_keys=[hogwarts_house_id])

    character_house_resource_fields = {
        'house_id': fields.Integer,
        'name': fields.String,
        'url': fields.Url('houseresource', absolute=True)
    }

    character_book_resource_fields = {
        'book_id': fields.Integer,
        'name': fields.String,
        'url': fields.Url('bookresource', absolute=True)
    }

    character_film_resource_fields = {
        'film_id': fields.Integer,
        'name': fields.String,
        'url': fields.Url('filmresource', absolute=True)
    }

    character_resource_fields = {
        'character_id': fields.Integer,
        'name': fields.String,
        'species': fields.String,
        'gender': fields.String,
        'hair_colour': fields.String,
        'eye_colour': fields.String,
        'wand': fields.String,
        'patronus': fields.String,
        'animagus': fields.String,
        'hogwarts_house': fields.Nested(character_house_resource_fields, allow_null=True),
        'books': fields.Nested(character_book_resource_fields),
        'films': fields.Nested(character_film_resource_fields),
        'url': fields.Url('characterresource', absolute=True)

    }

    def __init__(self, character_id, name, species, gender, hair_colour, eye_colour, wand, patronus, animagus, hogwarts_house_id):
        self.character_id = character_id
        self.name = name
        self.species = species
        self.gender = gender
        self.hair_colour = hair_colour
        self.eye_colour = eye_colour
        self.wand = wand
        self.patronus = patronus
        self.animagus = animagus
        self.hogwarts_house_id = hogwarts_house_id

class House(db.Model):
    house_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)
    colours = db.Column(db.String(100), unique=False)
    animal = db.Column(db.String(100), unique=False)
    element = db.Column(db.String(100), unique=False)
    common_room = db.Column(db.String(100), unique=False)
    head_of_house_id = db.Column(db.Integer, db.ForeignKey('character.character_id', use_alter=True, name='hogwarts_house'))
    founder_id = db.Column(db.Integer, db.ForeignKey('character.character_id', use_alter=True, name='hogwarts_house'))
    ghost_id = db.Column(db.Integer, db.ForeignKey('character.character_id', use_alter=True, name='hogwarts_house'))

    #Relationships
    values = db.relationship('Value', secondary=value, backref=db.backref('houses', lazy='dynamic'))
    head_of_house = db.relationship("Character", foreign_keys=[head_of_house_id])
    founder = db.relationship("Character", foreign_keys=[founder_id])
    ghost = db.relationship("Character", foreign_keys=[ghost_id])

    character_resource_fields = {
        'character_id': fields.Integer,
        'name': fields.String,
        'url': fields.Url('characterresource', absolute=True)
    }

    house_values_resource_fields = {
        'value_id': fields.Integer,
        'name': fields.String,
        'url': fields.Url('valueresource', absolute=True)
    }

    house_resource_fields = {
        'house_id': fields.Integer,
        'name': fields.String,
        'colours': fields.String,
        'animal': fields.String,
        'element': fields.String,
        'common_room': fields.String,
        'head_of_house': fields.Nested(character_resource_fields),
        'founder': fields.Nested(character_resource_fields),
        'ghost': fields.Nested(character_resource_fields),
        'values': fields.Nested(house_values_resource_fields),
        'url': fields.Url('houseresource', absolute=True)
    }

    def __init__(self, house_id, name, colours, animal, element, common_room, head_of_house_id, founder_id, ghost_id):
        self.house_id = house_id
        self.name = name
        self.colours = colours
        self.animal = animal
        self.element = element
        self.common_room = common_room
        self.head_of_house_id = head_of_house_id
        self.founder_id = founder_id
        self.ghost_id = ghost_id

class Value(db.Model):
    value_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)

    value_resource_fields = {
        'value_id': fields.Integer,
        'name': fields.String,
        'url': fields.Url('valueresource', absolute=True)
    }

    def __init__(self, value_id, name):
        self.value_id = value_id
        seld.name = name

class Request(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(20))
    requests = db.Column(db.Integer)
    last_request = db.Column(db.DateTime)
    first_request = db.Column(db.DateTime)

    def __init__(self, request_id, ip_address, requests, last_request, first_request):
        self.request_id = None
        self.ip_address = ip_address
        self.requests = requests
        self.last_request = last_request
        self.first_request = first_request

db.create_all()

def updateRateLimiting():
    requester = Request.query.filter_by(ip_address=request.remote_addr).first()

    now = datetime.now()
    dayago = now - timedelta(days=1)


    if requester is None:
        requester = Request('', request.remote_addr, 1, datetime.now(), datetime.now())
    else:
        if requester.first_request < dayago:
            requester.requests = 0
            requester.last_request = now
            requester.first_request = now

        else:
            requester.requests += 1
            requester.last_request = now
 
    db.session.add(requester)
    db.session.commit()




#Books
class BookResource(Resource):
    @marshal_with(Book.book_resource_fields, envelope='book')
    def get(self, book_id):
        return Book.query.get_or_404(book_id)

class BooksResource(Resource):
    @marshal_with(Book.book_resource_fields, envelope='books')
    def get(self):
        return Book.query.all()

api.add_resource(BooksResource, '/books')
api.add_resource(BookResource, '/books/<int:book_id>')

#Films
class FilmResource(Resource):
    @marshal_with(Film.film_resource_fields, envelope='film')
    def get(self, film_id):
        return Film.query.get_or_404(film_id)

class FilmsResource(Resource):
    @marshal_with(Film.film_resource_fields, envelope='films')
    def get(self):
        return Film.query.all()

api.add_resource(FilmsResource, '/films')
api.add_resource(FilmResource, '/films/<int:film_id>')

#Spells
class SpellResource(Resource):
    @marshal_with(Spell.spell_resource_fields, envelope="spell")
    def get(self, spell_id):
        return Spell.query.get_or_404(spell_id)

class SpellsResource(Resource):
    @marshal_with(Spell.spell_resource_fields, envelope="spells")
    def get(self):
        return Spell.query.all()

api.add_resource(SpellsResource, '/spells')
api.add_resource(SpellResource, '/spells/<int:spell_id>')

class CharacterResource(Resource):
    @marshal_with(Character.character_resource_fields, envelope="character")
    def get(self, character_id):
        return Character.query.get_or_404(character_id)

class CharactersResource(Resource):
    @marshal_with(Character.character_resource_fields, envelope="characters")
    def get(self):
        return Character.query.all()

api.add_resource(CharactersResource, '/characters')
api.add_resource(CharacterResource, '/characters/<int:character_id>')

class HouseResource(Resource):
    @marshal_with(House.house_resource_fields, envelope="house")
    def get(self, house_id):
        return House.query.get_or_404(house_id)

class HousesResource(Resource):
    @marshal_with(House.house_resource_fields, envelope="houses")
    def get(self):
        return House.query.all()

api.add_resource(HousesResource, '/houses')
api.add_resource(HouseResource, '/houses/<int:house_id>')

class ValueResource(Resource):
    @marshal_with(Value.value_resource_fields, envelope="value")
    def get(self, value_id):
        return Value.query.get_or_404(value_id)

class ValuesResource(Resource):
    @marshal_with(Value.value_resource_fields, envelope="values")
    def get(self):
        return Value.query.all()

api.add_resource(ValuesResource, '/values')
api.add_resource(ValueResource, '/values/<int:value_id>')

if __name__ == '__main__':
    #print list(app.url_map.iter_rules())
    app.run(debug=True)