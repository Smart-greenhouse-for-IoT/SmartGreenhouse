def searchDict(_dict, key_lst, key, value, index=False):
    # Search a device given name or ID
    found_dict = {}
    found_ind = None
    for ind, item in enumerate(_dict[key_lst]):
        if type(item[key]) is list:
            if value in item[key]:
                found_dict = item.copy()
                found_ind = ind
        else:
            if item[key] == value:
                found_dict = item.copy()
                found_ind = ind
    if index == True:
        return found_ind, found_dict
    else:
        return found_dict


def generateID(id_lst):
    if id_lst:
        new_id = id_lst[-1] + 1
        # Check if new id is already present
        while id_lst.count(new_id) > 0:
            new_id += 1
        return new_id
    else:
        return 1
