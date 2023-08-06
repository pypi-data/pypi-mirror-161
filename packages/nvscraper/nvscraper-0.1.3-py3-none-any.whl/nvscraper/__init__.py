import requests
from .nvutilities import *


class NvidiaDict(dict):

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)

    def available_filters(self) -> list:
        return ATTRIBUTES

    def filter_by(self, **filters):
        filtered_dict = self
        temp_dict = NvidiaDict()
        for filter, value in filters.items():
            if (filter.lower() not in [attr.lower() for attr in self.__]):
                raise Exception(
                    "Filter can't be applied, doesn't exist that attribute.")
            for key, info in super().items():
                if filtered_dict[key][filter] == value:
                    temp_dict[key] = info
            filtered_dict = temp_dict
            temp_dict.clear()
        return filtered_dict

    def get_specific_keys(self, *keys):
        filtered_dict = NvidiaDict()
        for item in self.keys():
            filtered_dict[item] = NvidiaDict()
            for key in keys:
                if key not in ATTRIBUTES:
                    raise Exception(f'{key} is not valid')
                else:
                    filtered_dict[item][key] = self[item][key]
        return filtered_dict


class NvidiaScraper:

    def _update_data(self, products, attr) -> None:
        if products["featuredProduct"] != None:
            for atribbutes in products["featuredProduct"]:
                self.__data[products["featuredProduct"]["productTitle"]] = {
                    attribute: products["featuredProduct"][attribute] if attribute in atribbutes else None for attribute in ATTRIBUTES
                }

        for product in products["productDetails"]:
            self.__data[product["productTitle"]] = {
                attribute: product[attribute] if attribute in product else None for attribute in ATTRIBUTES
            }

    def _check_price_range(self, price_range) -> tuple:
        min, max = price_range
        if min <= max and not (min < 0 or max < 0):
            return price_range
        else:
            raise Exception("Price range out of bounds.")

    def _check_graphics_cards(self, graphics_cards) -> list:
        for graphic_card in graphics_cards:
            if graphic_card.upper() not in GRAPHICS_CARDS:
                raise Exception("One or more graphic cards are not available.")
        return graphics_cards

    def _check_manufacturers(self, manufacturers) -> list:
        for manufacturer in manufacturers:
            if manufacturer.upper() not in MANUFACTURERS:
                raise Exception("One or more manufacturers are not available.")
        return manufacturers

    def _price_range_to_str(self) -> str:
        return str(self.__price_range[0]) + ',' + str(self.__price_range[1])

    def _search_query(self, page) -> str:
        query_options = f'page={page}&limit=9&locale={self.__locale}&category=GPU&price={self._price_range_to_str()}'
        formatted_graphic_cards = "gpu=" + \
            ''.join([graphic_card + "," for graphic_card in self.__graphics_cards])
        formatted_manufacturers = "manufacturer=" + \
            ''.join(manufacturer + ',' for manufacturer in self.__manufacturers)
        if formatted_graphic_cards != "gpu=":
            query_options += '&' + formatted_graphic_cards
        if formatted_manufacturers != "manufacturer=":
            query_options += '&' + formatted_manufacturers

        return remove_final_commas(query_options).replace(' ', '%20')

    # CONSTRUCTORS

    def __init__(self, graphics_cards=list(), manufacturers=list(), price_range=(0, 10000), locale="es-es") -> None:
        self.__URL = "https://api.nvidia.partners/edge/product/search?"
        self.__locale = locale
        self.__graphics_cards = self._check_graphics_cards(graphics_cards)
        self.__manufacturers = self._check_manufacturers(manufacturers)
        self.__price_range = self._check_price_range(price_range)
        self.__data = NvidiaDict()

    # GETTERS

    def get_graphics_cards(self) -> list:
        return self.__graphics_cards

    def get_manufacturers(self) -> list:
        return self.__manufacturers

    def get_price_range(self) -> tuple:
        return self.__price_range

    def get_data(self) -> NvidiaDict:
        return self.__data

    def get_locale(self) -> str:
        return self.__locale

    ## ADD | REMOVE
    def add_graphic_card(self, graphic_card) -> None:
        if graphic_card.upper() in GRAPHICS_CARDS and graphic_card.upper() not in self.__graphics_cards:
            self.__graphics_cards.append(graphic_card.upper())

    def remove_graphic_card(self, graphic_card) -> None:
        if graphic_card.upper() in GRAPHICS_CARDS and graphic_card.upper() in self.__graphics_cards:
            self.__graphics_cards.remove(graphic_card.upper())

    def add_manufacturer(self, manufacturer) -> None:
        if manufacturer.upper() in MANUFACTURERS and manufacturer.upper() not in self.__manufacturers:
            self.__graphics_cards.append(manufacturer.upper())

    def remove_manufacturer(self, manufacturer) -> None:
        if manufacturer.upper() in MANUFACTURERS and manufacturer.upper() in self.__manufacturers:
            self.__graphics_cards.remove(manufacturer.upper())

    def refresh_data(self) -> None:
        counter_page = 1
        self.__data.clear()
        while(True):
            filtered_url = self.__URL + self._search_query(counter_page)
            request_json = requests.get(
                url=filtered_url, headers=HEADERS, timeout=5).json()
            self._update_data(request_json["searchedProducts"], ATTRIBUTES)

            if request_json["searchedProducts"]["totalProducts"] <= 1:
                break
            else:
                counter_page += 1
