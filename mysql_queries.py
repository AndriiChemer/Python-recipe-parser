import mysql.connector
from mysql.connector import Error
import time

current_milli_time = lambda: int(round(time.time() * 1000))

def connectMySQL():
    try:
        connection = mysql.connector.connect(host='127.0.0.1', database='recipe',user='andrii', password='31lanafe')
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
        return connection

def closeConnection(connection):
    if(connection.is_connected()):
        connection.close()
        print("MySQL connection is closed")
    

# GENERAL METHODS
def generalInsert(connection, sql_get, params):
    id = None
    try:
        cursor = connection.cursor()
        cursor.execute(sql_get, params)
        connection.commit()
        id = cursor.lastrowid
    except Error as e:
        print("Error while insert category to MySQL", e)
    finally: 
        if (connection.is_connected()):
            cursor.close()
        return id

def generalGetID(connection, sql, params):
    id = None
    try:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        record = cursor.fetchone()
        id = record[0]

    except Error as e:
        print("Error while insert subcategory to MySQL", e)
    finally: 
        if (connection.is_connected()):
            cursor.close()
        return id



# MAIN INSERT METHOD
def insertRecipeList(listRecipeModel):
    connection = connectMySQL()

    for recipeModel in listRecipeModel:

        id_category = insertCategory(connection, recipeModel.categoriesModel)
        id_subcategory = insertSubcategory(connection, recipeModel.categoriesModel, id_category)
        id_recipe_category = insertRecipeCategory(connection, recipeModel.categoriesModel, id_subcategory)
        id_kitchen = insertKitchen(connection, recipeModel.kitchenName)
        id_recipe = insertRecipe(connection, recipeModel.name, recipeModel.image_url, recipeModel.comment, recipeModel.portion_count, recipeModel.cook_time, id_kitchen, id_category, id_subcategory, id_recipe_category)
        pass

    #Past sql database code
    closeConnection(connection)



# STEP 1 (CATEGORY OPERATION)
query_insert_category = "INSERT INTO category (name) VALUES (%s);"
def insertCategory(connection, categories):
    try:
        categoryName = categories[0]
        id_category = getCategoryID(connection, categoryName)

        if id_category is None:
            id_category = generalInsert(connection, query_insert_category, [(categoryName)])
    
    except Error as e:
        print("Error while insert subcategory to MySQL", e)
    finally:
        return id_category

query_select_category_id = "SELECT id FROM category WHERE name = %s;" 
def getCategoryID(connection, categoryName):
    return generalGetID(connection, query_select_category_id, (categoryName, ))



# STEP 2 (SUBCATEGORY OPERATION)
query_insert_subcategory = "INSERT INTO subcategory (name, id_category) VALUES (%s, %s);"
def insertSubcategory(connection, categories, id_category):
    try:
        subcategoryName = categories[1]
        id_subcategory = getSubcategoryID(connection, subcategoryName)

        if id_subcategory is None:
            id_subcategory = generalInsert(connection, query_insert_subcategory, [(subcategoryName, id_category)])

    except Error as e:
        print("Error while insert subcategory to MySQL", e)
    finally:
        return id_subcategory

query_select_subcategory_id = "SELECT id FROM subcategory WHERE name = %s;" 
def getSubcategoryID(connection, subcategoryName):
    return generalGetID(connection, query_select_subcategory_id, (subcategoryName, ))



# STEP 3 (RECIPE_CATEGORY OPERATION)
query_insert_recipe_category = "INSERT INTO recipe_category (name, id_subcategory, is_appoint) VALUES (%s, %s, %s);"
def insertRecipeCategory(connection, categories, id_subcategory):
    try:
        recipeCategoryName = categories[2]
        id_recipe_category = getRecipeCategoryID(connection, recipeCategoryName)

        if id_recipe_category is None:
            id_recipe_category = generalInsert(connection, query_insert_recipe_category, [(recipeCategoryName, id_subcategory, True)])

    except Error as e:
        print("Error while insert subcategory to MySQL", e)
    finally: 
        return id_recipe_category

query_select_recipe_category_id = "SELECT id FROM recipe_category WHERE name = %s;" 
def getRecipeCategoryID(connection, recipeCategoryName):
    return generalGetID(connection, query_select_recipe_category_id, (recipeCategoryName, ))



# STEP 4 (KITCHEN OPERATION)
query_insert_kitchen = "INSERT INTO kitchen (name) VALUES (%s);"
def insertKitchen(connection, kitchenName):
    id_kitchen = getKitchenID(connection, kitchenName)

    if id_kitchen is None:
        return generalInsert(connection, query_insert_kitchen, [(kitchenName)])
    else:
        return id_kitchen
    
query_select_kitchen_id = "SELECT id FROM kitchen WHERE name = %s;" 
def getKitchenID(connection, kitchenName):
    return generalGetID(connection, query_select_kitchen_id, (kitchenName, ))



# STEP 5 (RECIPE OPERATION)
query_insert_recipe = """
    INSERT INTO recipe (name, image_url, 
                comment, created_at, portion_count, 
                cook_time, is_active, id_kitchen, 
                id_category, id_subcategory, id_recipe_category) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s); 
"""
def insertRecipe(connection, name, image_url, comment, portion_count, cook_time, id_kitchen, id_category, id_subcategory, id_recipe_category):
    created_at = current_milli_time()
    return generalInsert(connection, query_insert_recipe, [(name, image_url, comment, created_at, portion_count, cook_time, True, id_kitchen, id_category, id_subcategory, id_recipe_category)])



# STEP 6 (Energy value OPERATION)
query_insert_energy = "INSERT INTO energy (name, kcal_value, squirrels_value, grease_value, carbohydrates_value) VALUES (%s, %s, %s, %s, %s);"
query_insert_recipe_energy = "INSERT INTO recipe_energy (id_recipe, id_energy) VALUES (%s, %s);"
def insertEnergyValue(connection, energyArray, id_recipe):
    for energyModel in energyArray:
        id_energy = generalInsert(connection, query_insert_energy, [(energyModel.title, energyModel.kcal, energyModel.squirrels, energyModel.fats, energyModel.carbohydrates)])
        
        if id_energy is not None:
            generalInsert(connection, query_insert_recipe_energy, [(id_recipe, id_energy)])



# STEP 7 (Ingredients OPERATION)
query_insert_ingredients = "INSERT INTO ingredient (name, value, description) VALUES (%s, %s, %s);"
query_insert_recipe_ingredients = "INSERT INTO recipe_ingredient (id_recipe, id_ingredient) VALUES (%s, %s);"
def insertIngredients(connection, ingredientArray, id_recipe):
    for ingredientModel in ingredientArray:
        id_ingredient = generalInsert(connection, query_insert_ingredients, [(ingredientModel.name, ingredientModel.value, ingredientModel.description)])
        
        if id_ingredient is not None:
            generalInsert(connection, query_insert_recipe_ingredients, [(id_recipe, id_ingredient)])



# STEP 8 (Cook Steps OPERATION)
query_insert_cook_step = "INSERT INTO cook_step (step, description, image_url) VALUES (%s, %s, %s);"
query_insert_recipe_cook_step = "INSERT INTO recipe_cook_step (id_recipe, id_cook_step) VALUES (%s, %s);"
def insertCookStep(connection, cookStepArray, id_recipe):
    step = 1
    for cookStep in cookStepArray:
        id_cook_step = generalInsert(connection, query_insert_cook_step, [(step, cookStep.description, cookStep.imgUrl)])
        
        if id_cook_step is not None:
            generalInsert(connection, query_insert_recipe_cook_step, [(id_recipe, id_cook_step)])
        step = step + 1



# STEP 9 (TASTES OPERATION)
query_insert_tastes = "INSERT INTO tastes (name) VALUES (%s);"
query_insert_recipe_tastes = "INSERT INTO recipe_tastes (id_recipe, id_tastes) VALUES (%s, %s);"
def insertTastes(connection, tasteList, id_recipe):
    for taste in tasteList:
        id_taste = getTasteID(connection, taste)
        if id_taste is None:
            id_taste = generalInsert(connection, query_insert_tastes, [(taste)])
        
        if id_taste is not None:
            generalInsert(connection, query_insert_recipe_tastes, [(id_recipe, id_taste)])

query_select_tastes_id = "SELECT id FROM tastes WHERE name = %s;" 
def getTasteID(connection, taste):
    return generalGetID(connection, query_select_tastes_id, (taste, ))


# STEP 10 (TAGS OPERATION)
query_insert_tag = "INSERT INTO tag (name) VALUES (%s);"
query_insert_recipe_tag = "INSERT INTO recipe_tag (id_recipe, id_tag) VALUES (%s, %s);"
def insertTags(connection, tagList, id_recipe):
    for tag in tagList:
        id_tag = getTagID(connection, tag)

        if id_tag is None:
            id_tag = generalInsert(connection, query_insert_tag, [(tag)])
        
        if id_tag is not None:
            generalInsert(connection, query_insert_recipe_tag, [(id_recipe, id_tag)])

query_select_tag_id = "SELECT id FROM tag WHERE name = %s;" 
def getTagID(connection, tag):
    return generalGetID(connection, query_select_tag_id, (tag,))

# SELECT scrypt


query_insert_user_test = "INSERT INTO test_user (name) VALUES (%s);"
query_insert_addrtess_test = "INSERT INTO test_address (address) VALUES (%s);"
query_insert_user_address_test = "INSERT INTO test_user_address (id_test_user, id_test_address) VALUES (%s, %s);"
query_select_user_test = "SELECT id FROM test_user WHERE name = %s;"

#INSERT
def insertTestList(testList):
    connection = connectMySQL()

    for model in testList:
        id_user_test = insertUserTest(connection, model.user)
        print("User id: ", id_user_test)
        # id_address_test = insertAddressTest(connection, model.address)
        # print("Address id: ", id_address_test)
        # record = insertUserAddress(connection, id_user_test, id_address_test)
        # print("======================================")
        # print(record)
        # print()
        pass

    closeConnection(connection)
    
# TEST_USER OPERATION
def insertUserTest(connection, user):
    id_user = getTestUserId(connection, user.name)

    if id_user is None:
        return generalInsert(connection, query_insert_user_test, [(user.name)])
    else:
        return id_user

def getTestUserId(connection, name):
    return generalGetID(connection, query_select_user_test, (name, ))
     
# TEST_ADDRESS OPERATION
def insertAddressTest(connection, address):
    id_address = None
    try:
        cursor = connection.cursor()
        cursor.execute(query_insert_addrtess_test, [(address.address)])
        connection.commit()
        id_address = cursor.lastrowid
        print("Address id: ", id_address)
    except Error as e:
        connection.rollback()
        print("Error while insert AddressTest to MySQL", e)
    finally: 
        if (connection.is_connected()):
            cursor.close()
            print("MySQL cursor is closed")
        return id_address
    pass

# TEST_USER_ADDRESS OPERATION
def insertUserAddress(connection, id_user_test, id_address_test):
    record = None
    try:
        cursor = connection.cursor()
        cursor.execute(query_insert_user_address_test, (id_user_test, id_address_test))
        connection.commit()
        record = cursor.rowcount
        print("You're connected to database: ", record)
    except Error as e:
        connection.rollback()
        print("Error while insert UserAddressTest to MySQL", e)
    finally: 
        return record

# connectMySQL()