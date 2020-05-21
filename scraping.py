from bs4 import BeautifulSoup
import requests
from models import Ingredient, Energy, EatStep, Recipe, UserTest, AddressTest, UserAddress
from mysql_queries import insertRecipeList, insertTestList

def getSize( elements ):
    counter = 0
    for element in elements:
        counter += 1
    return counter

###
# Parsing Category page
# return list of detail url article
# ###
def getListDetailsUrl( source ):
    listOfUrls = []
    soup = BeautifulSoup(source, 'lxml')

    for article in soup.find_all('article', class_='item-bl'):
        articleDetailUrl = article.find('div', 'm-img desktop-img conima').find('a')['href']
        listOfUrls.append(articleDetailUrl)
    
    return listOfUrls
    # return listOfUrls[1 : 4]

###
# Parsing list of category
# ###
def parseCategories( soup ):
    categoryList = []

    for item in soup.find_all('div', class_='article-breadcrumbs'):

        p_elements = item.find_all('p')

        categories = p_elements[0].find_all('span')
        
        for categoryName in categories:
            text = categoryName.a.text.replace("\n", "").replace("\r", "").replace("  ", "")
            categoryList.append(text)

    return categoryList

###
# Parsing kitchen
# ###
def parseKitchen( soup ):
    div = soup.find('div', class_='article-breadcrumbs')

    p_elements = div.find_all('p')

    p_elements_size = getSize(p_elements)

    if p_elements_size > 1:
        return p_elements[1].text.replace("\n", "").replace("\r", "").replace("  ", "").split(':')[1]
    else:
        return None

###
# Parsing time cooking
# ###
def parseCookingTime( soup ):
    div = soup.find('div', class_='ingredients-bl')
    p_elements = div.find_all('p')
    p_elements_size = getSize(p_elements)

    if p_elements_size == 0:
        return None
    else:
        for item in p_elements:
            if "Время" in item.text:
                timeToCook = item.text.split(':')[1]
                return timeToCook

    return None

###
# Parsing count of portion
# ###
def parsePortionCount( soup ):
    div = soup.find('div', class_='ingredients-bl')
    p_elements = div.find_all('p')
    p_elements_size = getSize(p_elements)

    if p_elements_size == 0:
        return None
    else:
        for item in p_elements:
            if "порций" in item.text:
                timeToCook = item.text.split(':')[1]
                return timeToCook

    return None

###
# Parsing list of ingredients
# ###
def parseIngredients( soup ):
    ingredientList = []

    div = soup.find('div', class_='ingredients-bl')
    ul = div.find('ul')
    li_elements = ul.find_all('li')

    for li in li_elements:
        line = li.text.replace("\n", "").replace("\r", "").replace("  ", "")
        lineArray = line.split('—')

        name = ''
        description = ''
        value = ''

        if "(" in str(lineArray[0]):
            nameDescription = lineArray[0].split('(')
            name = nameDescription[0]
            description = nameDescription[1][:-1]
            
        else:
            name = lineArray[0]

        if getSize(lineArray) > 1:
            value = lineArray[1]

        model = Ingredient(str(name), str(description), str(value))

        ingredientList.append(model)
        
    return ingredientList

###
# Parsing eat energy
# ###
def eatEnergy( soup ): 
    modelList = []

    tr_list = soup.find('div', id='nae-value-bl').find('table').find_all('tr')

    index = 1
    for tr in tr_list:
        if index % 2 != 0:
            title = tr.text.replace("\n", "").replace("\r", "").replace("  ", "")
            model = Energy(title, '', '', '', '')
            modelList.append(model)
        index = index + 1

    index = 1
    indexModel = 0
    for tr in tr_list:
        if index % 2 == 0:
            td = tr.find_all('td')
            kcal = td[0].find('strong').text.replace("\n", "").replace("\r", "").replace("  ", "")
            squirrels = td[1].find('strong').text.replace("\n", "").replace("\r", "").replace("  ", "")
            fats = td[2].find('strong').text.replace("\n", "").replace("\r", "").replace("  ", "")
            carbohydrates = td[3].find('strong').text.replace("\n", "").replace("\r", "").replace("  ", "")
            
            modelList[indexModel].kcal = kcal
            modelList[indexModel].squirrels = squirrels
            modelList[indexModel].fats = fats
            modelList[indexModel].carbohydrates = carbohydrates

            indexModel = indexModel + 1
            
        index = index + 1
    return modelList

###
# Parsing recipe steps
# ###
def recipeSteps( soup ):
    listModel = []

    div_list = soup.find_all('div', class_='cooking-bl')

    for div in div_list:
        img = div.find('span', 'cook-img').find('a').find('img')['src']
        description = div.find('div').text

        model = EatStep(img, description)
        listModel.append(model)
    
    return listModel

def parceTags( soup, str ):
    tagsList = []

    p_elements = soup.find('div', class_='article-tags').find('div', class_="tabs-wrap").find('div', class_='tab-content').find_all('p')

    for p in p_elements:
        # print(p.text)
        if str in p.text:
            for span in p.find_all("span"):
                tagsList.append(span.text)
            break

    return tagsList 

###
# Parsing detail page
# ###
def parseDetailUrl( detailUrl ):
    source = requests.get(detailUrl).text
    soup = BeautifulSoup(source, 'lxml')

    #Title
    titleModel = soup.find('h1').text
    #Main image
    imgUrlModel = soup.find('div', class_='m-img').img['src']
    #Users comment
    commentModel = soup.find('div' ,class_='article-text').p.text
    #Categories
    categoriesModel = parseCategories(soup)
    #Kitchen
    kitchen = parseKitchen(soup)
    #Cook time
    cookTimeModel = parseCookingTime(soup)
    #Count of portions
    portionCountModel = parsePortionCount(soup)
    #List of ingredients
    ingredients = parseIngredients(soup)
    #Parse table energy of eat
    energyEat = eatEnergy(soup)
    #Parse table energy of eat
    eatSteps = recipeSteps(soup)
    #Parse list tags
    tags = parceTags(soup, "Теги")
    #Parce tastes list
    tastes = parceTags(soup, "Вкусы")

    # showLogDetails(titleModel, imgUrlModel, commentModel, categoriesModel, kitchen, cookTimeModel, portionCountModel, ingredients, energyEat, eatSteps, tags, tastes)
    model = Recipe(titleModel, imgUrlModel, commentModel, categoriesModel, kitchen, cookTimeModel, portionCountModel, ingredients, energyEat, eatSteps, tags, tastes)

    return model

###
# Show log model
# ###
def showLogDetails(titleModel, imgUrlModel, commentModel, categoriesModel, kitchen, cookTimeModel, portionCountModel, ingredients, energyEat, eatSteps, tags, tastes):
    print()
    print()
    print("===============================================================")
    print("Title:")
    print(titleModel)
    print("Img url:")
    print(imgUrlModel)
    print("Comment:")
    print(commentModel[0 : 10])
    print("Categories:")
    print(categoriesModel)
    print("Kitchen:")
    print(kitchen)
    print("Cook time:")
    print(cookTimeModel)
    print("Portion count:")
    print(portionCountModel)
    print("Ingredients:")
    print(ingredients)
    print("Energy of eat:")
    print(energyEat)
    print("Eat steps:")
    print(eatSteps)
    print("Теги:")
    print(tags)
    print("Вкусы:")
    print(tastes)
    print("===============================================================")

# categoriesNumber = [2, 6, 12, 15, 19, 23, 25, 30, 35, 228, 227, 55, 187, 247, 289, 308, 356]
# pageCount = 50
# categoriesNumber = [2]
# pageCount = 1

# #Main function
# for categoryIndex in categoriesNumber:
#     for pageCountIndex in range(pageCount):
#         index = 1 + pageCountIndex
#         url = 'https://www.povarenok.ru/recipes/category/' + str(categoryIndex) + '/~' + str(index) + '/'
#         source = requests.get(url).text

#         # Getting detail url list from category 
#         listDetailsUrl = getListDetailsUrl(source)
#         # Parse detail
#         for detailUrl in listDetailsUrl:
#             parseDetailUrl( detailUrl )


def startParse():
    # categoriesNumber = [2, 6, 12, 15, 19, 23, 25, 30, 35, 228, 227, 55, 187, 247, 289, 308, 356]
    # pageCount = 50
    categoriesNumber = [2, 6, 12]
    pageCount = 2
    listRecipeModel = []

    for categoryIndex in categoriesNumber:
        print("categoryIndex = " + str(categoryIndex))
        for pageCountIndex in range(pageCount):
            print("pageCountIndex = " + str(pageCountIndex))
            index = 1 + pageCountIndex
            url = 'https://www.povarenok.ru/recipes/category/' + str(categoryIndex) + '/~' + str(index) + '/'
            source = requests.get(url).text

            # Getting detail url list from category 
            listDetailsUrl = getListDetailsUrl(source)
            # Parse detail
            for detailUrl in listDetailsUrl:
                recipeModel = parseDetailUrl( detailUrl )
                listRecipeModel.append(recipeModel)

    print(listRecipeModel)
    # insertRecipeList(listRecipeModel)

        
# startParse()

def insertList():
    listModels = []

    user1 = UserTest("Andre123412")
    address1 = AddressTest("Addre123432")
    userAddress1 = UserAddress(user1, address1)
    listModels.append(userAddress1)

    # user2 = UserTest("Andre2234")
    # address2 = AddressTest("Addre2234")
    # userAddress2 = UserAddress(user2, address2)
    # listModels.append(userAddress2)

    # user3 = UserTest("Andre3234")
    # address3 = AddressTest("Addre3234")
    # userAddress3 = UserAddress(user3, address3)
    # listModels.append(userAddress3)

    insertTestList(listModels)
    

insertList()