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

from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import column

# *** CONFIGURE FLASK APPLICATION ***
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///food-collection.db'
#Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# *** DATABASE TABLES ***
class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    expiry = db.Column(db.Integer, nullable=False)

    # return a dictionary as a method in class Food
    def to_dict(self):
        # for each column in table, set key as name of column and value is value of column. 
        return {column.title: getattr(self, column.title) for column in self.__table__.columns}

class Recipe(db.Model):
    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    instructions = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    ingredients = db.relationship("Ingredient", backref="recipe")

    # return a dictionary as a method in class Recipe
    def to_dict(self):
        # for each column in table, set key as name of column and value is value of column. 
        return {column.title: getattr(self, column.title) for column in self.__table__.columns}

class Ingredient(db.Model):
    __tablename__ = "ingredient"
    id =  db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.String(80), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"))


# ******* create  initial database. ran once. *********
# db.create_all()

# bananabread = Recipe(
#     title = "Banana Bread",
#     instructions = "1.Preheat oven to 350.\n"
#                    "2.Whisk flour, backing soda, salt, and cinnamon together in a large bowl.\n"
#                    "3.Beat butter and brown sugar together on high speed until smooth and creamy. Add eggs one at a time. Beat in yogurt, mashed bananas, and vanilla extract. Fold in dry ingredients\n"
#                    "4.Place batter in buttered pan and bake for 60-65 minutes. Cover bread with foil after 30 minutes. Done when toothpick comes out clean\n"
#                    "5.Can be stored at room temperature for 2 days or the refrigerator for 1 week.",
#     url = "https://sallysbakingaddiction.com/best-banana-bread-recipe/",
#     rating = 8,
# )
# #
# ingredient = Ingredient(
#     recipe_id = 1,
#     name = "Bananas",
#     quantity = "2 cups",
# )

# db.session.add(ingredient)
# db.session.commit()

# web app - main page 
@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        food = request.form.get("food_name")
        expiry = request.form.get("expiry_day")
        print(food)
        print(expiry)

        if  food == None or expiry == None or food == "":
            print("You had a missing field. Please fill in all fields to add new item.")
            pass
        else:
            newFoodEntry = Food(
                title = food,
                expiry = expiry,
            )
            db.session.add(newFoodEntry)
            db.session.commit()

    foods = db.session.query(Food).all()
    recipes = db.session.query(Recipe).all()
    return render_template("index.html", foods = foods, recipes = recipes)

# web app -> delete food item in database
@app.route("/deleteFood")
def deleteFood():
    food_id = request.args.get('id')
    food_to_delete = Food.query.get(food_id)
    db.session.delete(food_to_delete)
    db.session.commit()
    return redirect(url_for('main'))

# web app -> edit existing item
@app.route("/editFood", methods=["GET", "POST"])
def editFood():
    if request.method == "POST":
        food_id=request.form["id"]
        food_to_update = Food.query.get(food_id)
        food = request.form.get("food_name")
        expiry = request.form.get("expiry_day")
        # update record
        if  food == None or expiry == None or food == "":
            print("You had a missing field. Please fill in all fields to add new item.")
            pass
        else:
            food_to_update.title = food
            food_to_update.expiry = expiry
            db.session.commit()
            return redirect(url_for('main'))
    
    food_id = request.args.get('id')
    food_to_display = Food.query.get(food_id)
    return render_template("editFood.html", food = food_to_display)


# web app -> add new recipe 
@app.route("/addRecipe", methods=["GET"])
def webAddRecipe():
    return render_template("addNewRecipe.html")

# web app -> edit existing recipe ingredient
@app.route("/editIngredient", methods=["GET", "POST"])
def editIngredient():
    if request.method == "POST":
        ingredient_id=request.form["id"]
        ingredient_to_update = Ingredient.query.get(ingredient_id)
        ingredient = request.form.get("ingredient")
        quantity = request.form.get("quantity")
        # update record
        if  ingredient == None or quantity == None or ingredient== "" or quantity == "":
            print("You had a missing field. Please fill in all fields to add new item.")
            pass
        else:
            ingredient_to_update.name = ingredient
            ingredient_to_update.quantity = quantity
            db.session.commit()
            return redirect(url_for('main'))
    
    ingredient_id = request.args.get('id')
    ingredient_display = Ingredient.query.get(ingredient_id)
    return render_template("editIngredient.html", ingredient= ingredient_display)

# web app -> delete ingredient
@app.route("/deleteIngredient")
def deleteIngredient():
    ingredient_id = request.args.get('id')
    ingredient_to_delete = Ingredient.query.get(ingredient_id)
    db.session.delete(ingredient_to_delete)
    db.session.commit()
    return redirect(url_for('main'))

# web app -> add ingredient
@app.route("/addIngredient", methods=["GET","POST"])
def addIngredient():
    if request.method == "POST":
        ingredient_to_add = Ingredient(
            name = request.form.get("ingredient"),
            quantity = request.form.get("quantity"),
            recipe_id = request.form["id"]
        )

        db.session.add(ingredient_to_add)
        db.session.commit()
        return redirect(url_for('main'))
    

    recipe_id = request.args.get('id')
    recipe_to_display=Recipe.query.get(recipe_id)
    return render_template("addIngredient.html", recipe=recipe_to_display)

# web app -> add new food
@app.route("/addFood", methods=["GET"])
def webAddFood():
    return render_template("addNewFood.html")


# create record API
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



# search for food via API
@app.route("/search")
def get_food_name():
    food_name = request.args.get("title")
    food = db.session.query(Food).filter_by(title=food_name).first()
    if food:
        return jsonify(food=food.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry food item not found in the database."}), 404

# print everything out onto database API
@app.route("/all")
def get_all_food():
    foods = db.session.query(Food).all()
    print(foods)
    return jsonify(food=[item.to_dict() for item in foods])


if __name__ == '__main__':
    app.run(debug=True)
