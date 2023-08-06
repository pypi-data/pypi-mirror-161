HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
}

# Make sure have all this variables in UPPERCASE
GRAPHICS_CARDS = [
    "RTX 3090 TI",
    "RTX 3090",
    "RTX 3080 TI",
    "RTX 3080",
    "RTX 3070 TI",
    "RTX 3070",
    "RTX 3060 TI",
    "RTX 3060",
    "RTX 2080 SUPER",
    "RTX 2080",
    "RTX 2070 SUPER",
    "RTX 2070",
    "RTX 2060 SUPER",
    "RTX 2060",
    "GTX 1660 SUPER",
    "GTX 1660",
    "GTX 1660 TI",
    "GTX 1650",
    "GTX 1650 TI",
    "GTX 1650"
]

MANUFACTURERS = [
    "NVIDIA",
    "ASUS",
    "ACER",
    "AORUS",
    "EVGA",
    "GAINWARD",
    "GIGABYTE",
    "HP",
    "INNO3D",
    "LENOVO",
    "MSI",
    "PALIT",
    "PNY",
    "ZOTAC"
]

ATTRIBUTES = [
    "displayName",
    "totalCount",
    "productID",
    "imageURL",
    "productTitle",
    "digitialRiverID",
    "productSKU",
    "productUPC",
    "productUPCOriginal",
    "productPrice",
    "productAvailable",
    "productRating",
    "customerReviewCount",
    "isFounderEdition",
    "isFeaturedProduct",
    "certified",
    "manufacturer",
    "locale",
    "isFeaturedProdcutFoundInSecondSearch",
    "category",
    "gpu",
    "purchaseOption",
    "prdStatus",
    "minShipDays",
    "maxShipDays",
    "shipInfo",
    "isOffer",
    "offerText",
    "productInfo",
    "compareProductInfo"
]


def remove_by_index(str, index) -> str:
    if index < 0 or index >= len(str):
        raise Exception("Index out of bounds")
    if index == len(str):
        return str[:-1]
    elif index == 0:
        return str[1:]
    else:
        return str[:index] + str[index+1:]


def remove_final_commas(str) -> str:
    new_str = str
    counter = 0
    while(',' in new_str[counter:]):
        sliced_str = new_str[counter:]
        index_pos = sliced_str.index(',')
        counter += index_pos
        if counter + 1 < len(new_str):
            if sliced_str[index_pos + 1] == "&":
                new_str = remove_by_index(new_str, counter)
            counter += 1
        else:
            new_str = remove_by_index(new_str, counter)
            break

    return new_str


def sublist(list1, list2):
    set([item.upper() for item in list1]) <= set(list2)