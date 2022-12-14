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
import os
import base64
from PIL import Image
from werkzeug.utils import secure_filename
from io import BytesIO

# allowed extensions for the images
allowed_exts = {'jpg', 'jpeg','png','JPG','JPEG','PNG'}

def check_allowed_file(filename):
    if filename.rsplit('.',1)[1] in allowed_exts:
        return True
    else:
        return False

# *** CONFIGURE FLASK APPLICATION ***
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('LOCAL_DB_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL', 'sqlite:///food-collection.db')
# "sqlite:///food-collection.db"
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
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    instructions = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    ingredients = db.relationship("Ingredient", backref="recipe")
    # setting these as nullable=true for now, because there exists recipes w/o type and image rn. may modify later.
    foodType = db.Column(db.String(80), nullable=True)
    image = db.Column(db.Text, nullable=True)
    # return a dictionary as a method in class Recipe
    def to_dict(self):
        # for each column in table, set key as name of column and value is value of column. 
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
            
class Ingredient(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.String(80), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"))
    # return a dictionary as a method in class Ingredient
    def to_dict(self):
        # for each column in table, set key as name of column and value is value of column. 
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

# ******* create  initial database. ran once. *********
# db.create_all()

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
            search = db.session.query(Food).filter_by(title=food).first()
            # if food already in database, dont add! 
            if search:
                print("already exists in database")
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
@app.route("/addRecipe", methods=["GET", "POST"])
def webAddRecipe():
    if request.method == "POST":
        # check if user submitted an image file.
        if 'recipeImage' not in request.files:
            print('no image attached ')
            return redirect(url_for('main'))

        file = request.files['recipeImage']
        if file == "":
            print('No file selected')
            return redirect(url_for('main'))

        if file and check_allowed_file(file.filename):
            filename = secure_filename(file.filename)
            img = Image.open(file.stream) 
            with BytesIO() as buf:
                img.save(buf, 'png')
                image_bytes = buf.getvalue()
            encoded_string = base64.b64encode(image_bytes).decode()

            
        newRecipe = Recipe(
            title = request.form.get("recipeTitle"),
            rating=request.form.get("rating"),
            instructions = request.form.get("instructions"),
            url = request.form.get("recipeURL"),
            foodType = request.form.get("foodType"),
            image = encoded_string
        )
        # loop through table of ingredients and get ingredients if theyre not empty    
        for i in range(20):
            ingredient = request.form.get("i"+ str(i+1))
            quantity = request.form.get("q"+str(i+1))
            if ingredient != "" or quantity != "":
                newIngredient = Ingredient(
                    recipe=newRecipe,
                    name = ingredient,
                    quantity = quantity,
                )
        
        db.session.add(newRecipe)
        db.session.commit()     

        return redirect(url_for('main'))
    return render_template("addNewRecipe.html")

# web app -> delete recipe
@app.route("/deleteRecipe")
def deleteRecipe():
    recipe_id = request.args.get('id')
    recipe_to_delete = Recipe.query.get(recipe_id)
    db.session.delete(recipe_to_delete)
    db.session.commit()        
    return redirect(url_for('main'))

# web app -> edit Recipe
@app.route("/editRecipe", methods=["GET", "POST"])
def editRecipe():

    if request.method == "POST":
        recipe_id = request.form['id']
        recipe_to_update = Recipe.query.get(recipe_id)
        rating = request.form.get("rating")

        if rating == "Rating":
            print("Please add a rating")
            return redirect(url_for('main'))
        else:
            recipe_to_update.title = request.form.get("recipeTitle")
            recipe_to_update.url = request.form.get("recipeURL")
            recipe_to_update.rating = rating
            recipe_to_update.instructions = request.form.get("instructions")
            db.session.commit()
        return redirect(url_for('main'))

    recipe_id = request.args.get('id')
    recipe_to_edit = Recipe.query.get(recipe_id) 
    return render_template("editRecipe.html", recipe = recipe_to_edit)

# web app -> edit ingredient
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


# API -> add new food. when user enters in food collection, it checks if it's unique before adding.
@app.route("/add", methods=['POST'])
def post_new_food():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json
        newFoodEntry = Food(title = json["title"], expiry=json["expiry"])
        db.session.add(newFoodEntry)
        db.session.commit()
        return json
        # return jsonify(response = {"Success": "Successfully added new food item"})
    else:
        return jsonify(error={"Forbidden": "Content-Type not supported"}), 403



# API -> search food
@app.route("/search")
def get_food_name():
    food_name = request.args.get("title")
    food = db.session.query(Food).filter_by(title=food_name).first()
    if food:
        return jsonify(food=food.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry food item not found in the database."}), 404

# API -> print all food
@app.route("/allfoods")
def get_all_foods():
    foods = db.session.query(Food).all()
    return jsonify(collection=[item.to_dict() for item in foods])

# API -> print all recipe
@app.route("/allrecipes")
def get_all_recips():
    recipes = db.session.query(Recipe).all()
    return jsonify(recipe=[recipe.to_dict() for recipe in recipes])

# API -> print all ingredient
@app.route("/allingredients")
def get_all_ingredients():
    ingredients = db.session.query(Ingredient).all()
    return jsonify(ingredient=[ingredient.to_dict() for ingredient in ingredients])


# API -> print all combined recipes and ingredients together
@app.route ("/allRecipesIngredients")
def get_all_recipes_ingredients():
    ingredients=db.session.query(Ingredient).all()
    recipes=db.session.query(Recipe).all()

    ingredients_dict = [ingredient.to_dict() for ingredient in ingredients]
 
    recipes_dict = [recipe.to_dict() for recipe in recipes]


    combined_list = []
    
    for recipe in recipes_dict:

        ingredient_list = []
        for ingredient in ingredients_dict:
           if ingredient["recipe_id"] == recipe["id"]:
                ingredient_list.append(ingredient)
        
        new_dict = {
            "ingredient" : ingredient_list
        }
        recipe.update(new_dict)
        combined_list.append(recipe)
        

    return jsonify(recipes = combined_list)

if __name__ == '__main__':
    app.run(debug=True)
