import requests
from bs4 import BeautifulSoup


class getSearchResults():
    def __init__(self, searchName):
        self.searchName = searchName
        self.result = requests.get(f'https://www.bbc.co.uk/food/search?q={searchName}')
        self.page = self.result.text
        self.soup = BeautifulSoup(self.page, 'html.parser')
        self.menu_list = self.soup.find_all(
            'div', {'class': 'gel-layout__item gel-1/2 gel-1/4@xl'})
        self.title = []
        self.prep = []
        self.cook = []
        self.Serves = []
        self.links = []

    def returnTitles(self):
        for menu in self.menu_list:
            title = menu.find('h3', {'class': 'promo__title'}).get_text()
            self.title.append(title)
        return self.title

    def returnTitleDetails(self):
        for menu in self.menu_list:
            # Get to the info of the menu, which contains cooking_time, prep_time, and servings
            div = menu.find('div', {'class': "promo__recipe-info"})
            # Get cooking_time, if not found, unknown. Same for all below.
            if div.get_text().find("Cook") != -1:
                cook_index = div.get_text().find("Cook")
                cook_message = div.get_text()[cook_index:]
            else:
                cook_message = "Unknown"

            if div.get_text().find("Prep") != -1:
                prep_index = div.get_text().find("Prep")
                prep_message = div.get_text()[prep_index:cook_index]

            else:
                prep_message = "Unknown"

            if div.get_text().find("Serves") != -1:
                serve_index = div.get_text().find("Serve")
                serve_message = div.get_text()[:prep_index]
            else:
                serve_message = "Serves Unknown"

            self.prep.append(prep_message)
            self.cook.append(cook_message)
            self.Serves.append(serve_message)

        return self.prep, self.cook, self.Serves

    def returnLinks(self):
        for menu in self.menu_list:
            links1 = menu.find('a', {'class': 'promo'}, href=True)['href']   # Find the menu's link.
            links = "https://www.bbc.co.uk" + links1
            self.links.append(links)
        return self.links


class getRecipeDetails:
    def __init__(self, link):
        self.link = link
        self.ingredients = []
        self.procedure = []
        self.cookingTime = ""
        self.prepTime = ""
        self.servings = ""
        self.chef = ""

        self.result = requests.get(self.link)
        self.soup = BeautifulSoup(self.result.text,'html.parser')

    def returnIngredients(self):
        ingredients = self.soup.find_all('li', {'class': 'recipe-ingredients__list-item'})
        for item in ingredients:
            self.ingredients.append(item.get_text())
        return self.ingredients

    def returnProcedure(self):
        method = self.soup.find_all('p', {'class': 'recipe-method__list-item-text'})
        for steps in method:
            self.procedure.append(steps.get_text())
        return self.procedure

    def returnCookingTime(self):
        cooking_time = self.soup.find('p', {'class': 'recipe-metadata__cook-time'})
        try:
            self.cookingTime = cooking_time.get_text()
        except:
            self.cookingTime = "Unknown"
        return self.cookingTime

    def returnPrepTime(self):
        prep_time = self.soup.find('p',{'class': "recipe-metadata__prep-time"})
        try:
            self.prepTime = prep_time.get_text()
        except:
            self.prepTime = "Unknown"
        return self.prepTime

    def returnServings(self):
        serves = self.soup.find('p',{'class':'recipe-metadata__serving'})
        try:
            self.servings = serves.get_text()
        except:
            self.servings = "Unknown"
        return self.servings

    def returnChef(self):
        try:
            self.chef = self.soup.find('a', {'class':'chef__link'}).get_text()
        except:
            self.chef = "Anonymous"
        return self.chef


