const request = require('request');
const cheerio = require('cheerio');
const iconvLite = require('iconv-lite');
const iconv = require('iconv'); 

const Insert = require('../database/insert')
const Select = require('../database/select')


//https://www.povarenok.ru/recipes/category/index/~pageNumber/
const categoriesNumber = [2, 6, 12, 15, 19, 23, 25, 30, 35, 228, 227, 55, 187, 247, 289, 308, 356];
const pageCount = 50;


var items = [];

exports.startScrapRecipe = () => {

    categoriesNumber.forEach((index) => {
        console.log('index = ' + index);

        for (let i = 1; i <= pageCount; i++) { 
            var uri = 'https://www.povarenok.ru/recipes/category/' + index + '/~' + i + '/';
            console.log("Parsing: " + uri);
            parseItemListPage(uri);
        }
    });

}


//parsing
function parseItemListPage(uri) {
    const jsonParam = {
        uri: uri,
        encoding: null
    }
    request(jsonParam, (error, response, html) => {
        if(!error && response.statusCode == 200) {
            const $ = cheerio.load(html);

            $('.item-bl').each((i, el) => {

                const itemUrl = $(el)
                                .find('div', '.m-img.desktop-img.conima')
                                .find('a')
                                .attr('href');

                parseRecipeItem(itemUrl);
                                
            });
        }
    });
}

function parseRecipeItem(itemUrl) {
    const jsonParam = {
        uri: itemUrl,
        encoding: null
    }

    request(jsonParam, (error, response, html) => {
        if(!error && response.statusCode == 200) {
            const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });

            const articleName = $('h1').text();

            const articleImageUrl = $('div.m-img')
                                    .find('img')
                                    .attr('src');

            const comment = $('div.article-text').find('p').text()

            const categoties = parseCategories(html)
            const kitchen = parseKitchen(html)
            const countOfPorcion = parseTimeAndPorcion(html, false);
            const cookTime = parseTimeAndPorcion(html, true);
            const ingridients = parseIngridients(html)

            const galeryImages = parseGaleryImages(html)

            const arrayTabelValue = parseTableValue(html);
            const cookSteps = parseCookSteps(html);
            const appointment = parseAppointment(html);
            const tags = parseTags(html, 1);
            const tastes = parseTags(html, 2)


            //Result scrapping

            writeToDatabase(articleName, 
                articleImageUrl, 
                categoties, 
                kitchen, 
                countOfPorcion, 
                cookTime, 
                arrayTabelValue, 
                ingridients, 
                cookSteps, 
                galeryImages, 
                tags, 
                tastes, 
                appointment)

            // console.log('articleName = ' + articleName);
            // console.log('articleImageUrl = ' + articleImageUrl)
            // console.log('categoties = ' + categoties)
            // console.log('kitchen = ' + kitchen)
            // console.log('Порций = ' + countOfPorcion)
            // console.log('Время приготовления = ' + cookTime)


            // console.log('\nTabel:')
            // arrayTabelValue.forEach((item) => {
            //     console.log('\n\n');
            //     console.log(item.title + '\n' + item.kcal + ' = ' + item.kcalValue + '\t' + item.squirrels + ' = ' + item.squirrelsValue + '\t' + item.fats + ' = ' + item.fatsValue + '\t' + item.carbohydrates + ' = ' + item.carbohydratesValue);
            //     console.log('\n\n');
            // });
            
            // console.log('\nIngridients:')
            // ingridients.forEach((model) => {
            //     console.log(model.title);

            //     for (var entry of model.ingridients.entries()) {
            //         var key = entry[0],
            //             value = entry[1];
            //         console.log(key + " = " + value);
            //     }
            //     console.log('\n');
            // });
            // console.log("ANDRII 1");

            // var i = 0;
            // console.log('\nCook step:')
            // for (var step of cookSteps.entries()) {
            //     i++;
            //     var key = step[0],
            //         value = step[1];
            //     console.log(i + '. ' + key);
            // }

            // console.log('\nGalery images:')
            // i = 0;
            // for (var url of galeryImages) {
            //     i++;
            //     console.log(i + '. url = ' + url);
            // }

            // console.log('\nТеги:', 'background: #222');
            // tags.forEach((item) => {
            //     console.log(item);
            // });

            // console.log('\nВкусы:', 'background: #222');
            // tastes.forEach((item) => {
            //     console.log(item);
            // });

            // console.log('\nНазначение:', 'background: #222');
            // for (var step of appointment.entries()) {
            //     i++;
            //     var key = step[0],
            //         value = step[1];
            //     console.log(i + '. ' + key + ' : ' + value);
            // }
            // console.log('\nload uri =' + itemUrl + ' is done!')
            // console.log('======================================================================\n\n\n\n')
        } else {
            console.log('error =' + error);
        }
    });
}

function parseTimeAndPorcion(html, isCookTime) {
    var timeCook = null;
    var porcion = null;
    const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });

    $('div.ingredients-bl').find('p').each((i, el) => {
        var text = $(el).text();

        if(text.includes('Время')) {
            timeCook = text;
        }

        if(text.includes('Количество')) {
            porcion = text;
        }
    });

    if(isCookTime) {
        return timeCook;
    } else {
        return porcion;
    }
}

function parseAppointment(html) {
    var map = new Map();

    const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });
    const tags = $('div.tab-content').find('p')[0];
    $(tags).find('span').each((i, item) => {
        const tag = $(item).find('a');
        if(tag.length > 1) {
            const subCategory = $(tag[0]).text();
            const recipeCategory = $(tag[1]).text();

            map.set(recipeCategory, subCategory);
        } else {
            const recipeCategory = $(tag).text();
            map.set(recipeCategory, null);
        }

    });

    return map;
}

function parseTags(html, index) {
    var arraysTags = [];
    const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });
    const tags = $('div.tab-content').find('p')[index];
    $(tags).find('span').each((i, item) => {
        const tag = $(item).find('a').text();
        arraysTags.push(tag);
    });

    return arraysTags;
}

function parseCookSteps(html) {
    var map = new Map();

    const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });
    $('div.cooking-bl').each((i, div) => {
        const image = $(div).find('span.cook-img').find('a').attr('href');
        const text = $(div).find('div').find('p').text();

        map.set(image, text);
    });


    return map;
}

function parseTableTitles(html) {
    var titles = [];
    var readyDish = new Map();

    const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });
    
    $('div#nae-value-bl').find('table').find('tr').each((i, el) => {
        const td = $(el).find('td');
        if(td.length < 2) {
            titles.push($(td).find('strong').text());
        }
    });
}

function parseTableValue1(html) {
    // var readyDishTitle = '';

    var titles = [];
    var readyDish = new Map();

    var objectList = [];
    // var portions = new Map();
    // var onOneHungredDish = new Map();
    const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });
    console.log('tr size = ' + $('div#nae-value-bl').find('table').find('tr').length);

    
    $('div#nae-value-bl').find('table').find('tr').each((i, el) => {
        console.log('index = ' + i);
        const td = $(el).find('td');
        
        if(td.length > 1) {

            td.each((index, element) => {
                
                var value = $(element).find('strong').text();
                var name = $(element).text().replace(value, '');

                var newValue = '';
                value.split('  ').forEach((item) => {
                    if(item.length > 1) {
                        newValue += item
                    }
                });

                var newName = '';
                name.split('  ').forEach((item) => {
                    if(item.length > 1) {
                        newName += item
                    }
                });


                readyDish.set(newName, value)
            });


        } else {
            titles.push($(td).find('strong').text());
        }
    });
}

function parseTableValue(html) {
    var arrays = [];

    const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });
    
    var el = $('div#nae-value-bl').find('table').find('tr');

    var objectReadyDish = new Object();
    objectReadyDish.title = $(el[0]).find('td').find('strong').text();
    var mapReadyDish = parseRovValue($(el[1]));

    var step = 0;
    for (var entry of mapReadyDish.entries()) {
        var key = entry[0],
            value = entry[1];

        if(step == 0) {
            objectReadyDish.kcal = key;
            objectReadyDish.kcalValue = value;
        } else if(step == 1) {
            objectReadyDish.squirrels = key;
            objectReadyDish.squirrelsValue = value;
        } else if(step == 2) {
            objectReadyDish.fats = key;
            objectReadyDish.fatsValue = value;
        } else {
            objectReadyDish.carbohydrates = key;
            objectReadyDish.carbohydratesValue = value;
        }
        step++;
    }



    var objectPortions = new Object();
    objectPortions.title = $(el[2]).find('td').find('strong').text();
    var mapPortions = parseRovValue($(el[3]));

    step = 0;
    for (var entry of mapPortions.entries()) {
        var key = entry[0],
            value = entry[1];

        if(step == 0) {
            objectPortions.kcal = key;
            objectPortions.kcalValue = value;
        } else if(step == 1) {
            objectPortions.squirrels = key;
            objectPortions.squirrelsValue = value;
        } else if(step == 2) {
            objectPortions.fats = key;
            objectPortions.fatsValue = value;
        } else {
            objectPortions.carbohydrates = key;
            objectPortions.carbohydratesValue = value;
        }
        step++;
    }

    var objectOneHundredDish= new Object();
    objectOneHundredDish.title = $(el[4]).find('td').find('strong').text();
    var mapOneHundredDish = parseRovValue($(el[5]));

    step = 0;
    for (var entry of mapOneHundredDish.entries()) {
        var key = entry[0],
            value = entry[1];

        if(step == 0) {
            objectOneHundredDish.kcal = key;
            objectOneHundredDish.kcalValue = value;
        } else if(step == 1) {
            objectOneHundredDish.squirrels = key;
            objectOneHundredDish.squirrelsValue = value;
        } else if(step == 2) {
            objectOneHundredDish.fats = key;
            objectOneHundredDish.fatsValue = value;
        } else {
            objectOneHundredDish.carbohydrates = key;
            objectOneHundredDish.carbohydratesValue = value;
        }
        step++;
    }


    arrays.push(objectReadyDish);
    arrays.push(objectPortions);
    arrays.push(objectOneHundredDish);

    return arrays;
}

function parseRovValue(html) {
    var map = new Map();

    const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });

    const td = $(html).find('td');

    if(td.length > 1) {

        td.each((index, element) => {
            
            var value = $(element).find('strong').text();
            var name = $(element).text().replace(value, '');

            var newValue = '';
            value.split('  ').forEach((item) => {
                if(item.length > 1) {
                    newValue += item
                }
            });

            var newName = '';
            name.split('  ').forEach((item) => {
                if(item.length > 1) {
                    newName += item
                }
            });

            map.set(newName, value)
        });
    }

    return map;
}

//TODO think about model
function parseIngridients1(html) {
    var ingridientsArray = [];

    const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });

    const ulLength = $('div.ingredients-bl').find('ul').length;

    if($('div.ingredients-bl').find('p').length == 0) {
        var object = new Object();
        object.title = "Ингредиенты для";
        ingridientsArray.push(object);
    } else {
        $('div.ingredients-bl').find('p').each((i, p) => {
            var object = new Object();
            object.title = $(p).find('strong').text();
            ingridientsArray.push(object);
        });
    }

    if(ulLength < ingridientsArray.length) {
        ingridientsArray.pop();
        ingridientsArray[0].title = "Ингредиенты для"

    } else if(ingridientsArray.length == 1) {
        ingridientsArray[0].title = "Ингредиенты для"
    }

    $('div.ingredients-bl').find('ul').each((i, ul) => {

        var object = ingridientsArray[i]
        var ingridients = new Map();

        $(ul).find('li').each((i1, li) => {

            var ingredient = $(li).find('span').find('a');
            if(ingredient.length > 1) {
                ingredient = $(ingredient[0]).find('span').text()
            } else {
                ingredient = $(ingredient).find('span').text()
            }


            var value = ''

            const spanCount = $(li).find('span').find('span').length;
            if(spanCount > 2) {
                const temp = $(li).find('span').find('span');
                value = $(temp[2]).text();
            } else if(spanCount > 1) {
                const temp = $(li).find('span').find('span');
                value = $(temp[1]).text();
            } else {
                value = $(li).find('span').find('span').text();
            }

            if(ingredient === value) {
                ingridients.set(ingredient, null); 
            } else {
                ingridients.set(ingredient, value); 
            }

        });

        object.ingridients = ingridients;
        ingridientsArray[i] = object;

    });

    return ingridientsArray;
}

function parseGaleryImages(html) {
    var images = [];

    const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });

    $('img.bbimg').each((i, img) => {
        var url = $(img).attr('src')
        images.push(url)
    });

    return images;
}


function parseIngridients(html) {
    var ingridientsArray = [];

    const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });

    const ulLength = $('div.ingredients-bl').find('ul').length;

    if($('div.ingredients-bl').find('p').length == 0) {
        var object = new Object();
        object.title = "Ингредиенты для";
        ingridientsArray.push(object);
    } else {
        $('div.ingredients-bl').find('p').each((i, p) => {
            var object = new Object();

            var title = $(p).find('strong').text()

            if(!title.includes("Время") && !title.includes("Количество")) {
                object.title = title;
                ingridientsArray.push(object);
            }
        });
    }

    if(ulLength > ingridientsArray.length) {
        var object = new Object();
        object.title = "Ингредиенты для"
        ingridientsArray.push(object)

    } 
    // else if(ingridientsArray.length == 1) {
    //     ingridientsArray[0].title = "Ингредиенты для"
    // }

    $('div.ingredients-bl').find('ul').each((i, ul) => {

        var object = ingridientsArray[i]
        var ingridients = new Map();

        $(ul).find('li').each((i1, li) => {

            var ingredient = $(li).find('span').find('a');
            if(ingredient.length > 1) {
                ingredient = $(ingredient[0]).find('span').text()
            } else {
                ingredient = $(ingredient).find('span').text()
            }


            var value = ''

            const spanCount = $(li).find('span').find('span').length;
            if(spanCount > 2) {
                const temp = $(li).find('span').find('span');
                value = $(temp[2]).text();
            } else if(spanCount > 1) {
                const temp = $(li).find('span').find('span');
                value = $(temp[1]).text();
            } else {
                value = $(li).find('span').find('span').text();
            }

            if(ingredient === value) {
                ingridients.set(ingredient, ''); 
            } else {
                ingridients.set(ingredient, value); 
            }

        });

        object.ingridients = ingridients;
        ingridientsArray[i] = object;

    });

    return ingridientsArray;
}

function parseKitchen(html) {
    var kitchen = null;
    const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });
    $('div.article-breadcrumbs').each((i, el) => {

        const items = $(el).find('p');
        if(items.length > 1) {
            kitchen = $(items[1]).find('span').find('a').text()
        }
    });

    return kitchen;
}

function parseCategories(html) {
    var categories = [];

    const $ = cheerio.load(readRussianChars(html), { decodeEntities: true });
    $('div.article-breadcrumbs').each((i, el) => {

        const items = $(el).find('p');

        if(items.length > 1) {
            const category = $(items[0]).find('span').find('a').each((i, el) => {
                categories.push($(el).text())
            });

        } else {
            const category = $(items).find('span').find('a').each((i, el) => {
                categories.push($(el).text())
            });
        }


    });

    return categories;
}

function readRussianChars(html) {
    return iconvLite.encode(iconvLite.decode(html, 'windows-1251'), 'utf8').toString()
}