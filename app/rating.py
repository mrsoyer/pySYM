def rate_location(location):
    marseille = [zip_code for zip_code in range(13001, 13017)]

    address = location.split()

    for element in address:
        if len(element) == 5 and element.isdigit():
            element = int(element)
            if element in marseille:
                return 5
            elif element == 13090 or element == 13100:
                return 4
            elif str(element)[:2] == "13":
                return 3
            else:
                return 1
        else:
            return 0
    
def rate_title(title):
    pass