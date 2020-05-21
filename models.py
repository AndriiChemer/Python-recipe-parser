class Ingredient:

    # Initializer / Instance Attributes
    def __init__(self, name, description, value):
        self.name = name
        self.description = description
        self.value = value

    def __repr__(self):
        return str(self.__dict__)


class Energy:

    def __init__(self, title, kcal, squirrels, fats, carbohydrates): 
        self.title = title
        self.kcal = kcal
        self.squirrels = squirrels
        self.fats = fats
        self.carbohydrates = carbohydrates
    
    def __repr__(self):
        return str(self.__dict__)

class EatStep:

    def __init__(self, imgUrl, description): 
        self.imgUrl = imgUrl
        self.description = description

    def __repr__(self):
        return str(self.__dict__)

class Recipe:

    def __init__(self, titleModel, imgUrlModel, commentModel, categoriesModel, kitchen, cookTimeModel, portionCountModel, ingredients, energyEat, eatSteps, tags, tastes):
        self.titleModel = titleModel
        self.imgUrlModel = imgUrlModel
        self.commentModel = commentModel
        self.categoriesModel = categoriesModel
        self.kitchen = kitchen
        self.cookTimeModel = cookTimeModel
        self.portionCountModel = portionCountModel
        self.ingredients = ingredients
        self.energyEat = energyEat
        self.eatSteps = eatSteps
        self.tags = tags
        self.tastes = tastes

class UserTest:
    def __init__(self, name): 
        self.name = name

class AddressTest:
    def __init__(self, address): 
        self.address = address

class UserAddress:
    def __init__(self, user, address): 
        self.user = user
        self.address = address