# -*- coding: utf-8 -*-
import scrapy
import csv
from src.recipe import Recipe, Nutrition


class RecipeSpider(scrapy.Spider):
    name = 'recipe'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = self.get_urls_from_data("../data/input/recipes.csv")['bbc']

    @staticmethod
    def get_urls_from_data(data_path: str):
        """
        Finds and returns a list of URLs from the recipes.csv dataset.
        :param data_path:
        :return:
        """
        bbc_urls = []
        all_recipes_urls = []
        with open(data_path) as csv_file:
            csv_reader = csv.reader(csv_file)
            for index, row in enumerate(csv_reader):
                if "www.bbcgoodfood.com" in row[0]:
                    bbc_urls.append(row[0])

        return {
            "bbc": bbc_urls,
            "all_recipes": all_recipes_urls
        }

    def parse(self, response):
        # Information from header includes title, author, cook time, difficulty, servings
        # and nutritional information
        header = response.xpath('//div[contains(@class, "recipe-header")]')
        recipe_title = header.xpath('h1[contains(@class, "recipe-header__title")]/text()')
        attrib = header.xpath('//div[contains(@class, "recipe-header__chef")]/span/a/text()')

        time = {
            "prep": {
                'hrs': header.xpath('//span[contains(@class, "recipe-details__cooking-time-prep")]/'
                                    'span[contains(@class, "hrs")]/text()').get(),
                'mins': header.xpath('//span[contains(@class, "recipe-details__cooking-time-prep")]/'
                             'span[contains(@class, "mins")]/text()').get(),
            },
            "cook": {
                'hrs': header.xpath('//span[contains(@class, "recipe-details__cooking-time-cook")]/'
                                    'span[contains(@class, "hrs")]/text()').get(),
                'mins': header.xpath('//span[contains(@class, "recipe-details__cooking-time-cook")]/'
                                     'span[contains(@class, "mins")]/text()').get(),
            }
        }

        difficulty = header.xpath('//section[contains(@class, "recipe-details__item--skill-level")]'
                                  '/span[contains(@class, "recipe-details__text")]/text()').get()
        servings = header.xpath('//section[contains(@class, "recipe-details__item--servings")]'
                                  '/span[contains(@class, "recipe-details__text")]/text()').get()
        # Here we gather available nutritional info and build the Nutrition object
        nutrition_list = header.xpath('//ul[contains(@class, "nutrition")]')
        kcal = nutrition_list.xpath('//span[contains(@itemprop, "calories")]/text()').get()
        fat = nutrition_list.xpath('//span[contains(@itemprop, "fatContent")]/text()').get()
        sat_fats = nutrition_list.xpath('//span[contains(@itemprop, "saturatedFatContent")]/text()').get()
        carbs = nutrition_list.xpath('//span[contains(@itemprop, "carbohydrateContent")]/text()').get()
        sugars = nutrition_list.xpath('//span[contains(@itemprop, "sugarContent")]/text()').get()
        fibre = nutrition_list.xpath('//span[contains(@itemprop, "fiberContent")]/text()').get()
        protein = nutrition_list.xpath('//span[contains(@itemprop, "proteinContent")]/text()').get()
        salt = nutrition_list.xpath('//span[contains(@itemprop, "sodiumContent")]/text()').get()
        nutrition_object = Nutrition(kcal, fat, sat_fats, carbs, sugars, fibre, protein, salt)

        # Information from the details section includes ingredients and method
        details = response.xpath('//div[contains(@class, "responsive-tabs")]')
        # The full text of the ingredients will be in the content attribute of the li tag
        ingredients = details.xpath('section[contains(@id, "recipe-ingredients")]//'
                                    'div[contains(@class, "ingredients-list__content")]/ul/li/@content')
        # TODO Check for final method step, sometimes the beeb offers a suggestion with a link to another recipe
        method = details.xpath('section[contains(@id, "recipe-method")]//'
                               'div[contains(@class, "method")]/ol/li/p/text()')

        recipe_object = Recipe(recipe_title.get(), attrib.get(), nutrition_object, ingredients.getall(),
                               method.getall(), time, difficulty, servings)

        # self, name, author, nutrition, ingredients, method
        return recipe_object.to_dict()
        pass
