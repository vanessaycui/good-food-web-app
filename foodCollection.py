# import sqlite3

# #connect to a new database. if database doesnt exist, a new database will be created
# db = sqlite3.connect("food-collection.db")

# #create a cursor to control database
# cursor = db.cursor()

# #tell cursor to execute an action as SQL (structured query language)
# # after creating table, commented it out because we dont want to recreate it everytime we run it. 
# # cursor.execute("CREATE TABLE collection(id INTEGER PRIMARY KEY, title varchar(250) not null unique, expiry INTEGER NOT NULL)")

# cursor.execute("INSERT INTO collection VALUES(1,'banana', '10')")
# db.commit()

# ******************************


# use SQLAlchemy

from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy

import json
from sqlalchemy import column

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///food-collection.db'
#Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# create tables
class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    expiry = db.Column(db.Integer, nullable=False)

    # return a dictionary as a method in class Food
    def to_dict(self):
        # for each column in table, set key as name of column and value is value of column. 
        return {column.title: getattr(self, column.title) for column in self.__table__.columns}

class Recipe(db.Model):
    __tablename__="recipe"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    instructions = db.Column(db.String(500), unique=True, nullable=False)
    url = db.Column(db.String(80), unique=True, nullable=False)
    ingredient = db.relationship("Ingredient", backref="recipe")


class Ingredient(db.Model):
    __tablename__="ingredient"
    id =  db.Column(db.Integer, primary_key=True)
    recipeid = db.Column(db.Integer, db.ForeignKey("recipe.id"))


    # return a dictionary as a method in class Recipe
    def to_dict(self):
        # for each column in table, set key as name of column and value is value of column.
        return {column.title: getattr(self, column.title) for column in self.__table__.columns}

# # create  initial database. ran once.
# db.create_all()

@app.route("/", methods=["GET", "POST"])
def main():
    foods = db.session.query(Food).all()

    return render_template("index.html", foods = foods)

# create record
@app.route("/add")
def post_new_food():

    api_key = request.args.get("api_key")
    if api_key == "TopSecretAPIKey":

        newFoodEntry = Food(
            title = request.args.get("title"),
            expiry = request.args.get("expiry"),
        )

        db.session.add(newFoodEntry)
        db.session.commit()
        return jsonify(response = {"Success": "Successfully added new food item"})
    else: 
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403



# search for food
@app.route("/search")
def get_food_name():
    food_name = request.args.get("title")
    food = db.session.query(Food).filter_by(title=food_name).first()
    if food:
        return jsonify(food=food.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry food item not found in the database."}), 404

# print everything out onto database.
@app.route("/all")
def get_all_food():
    foods = db.session.query(Food).all()
    print(foods)
    return jsonify(food=[item.to_dict() for item in foods])


if __name__ == '__main__':
    app.run(debug=True)
