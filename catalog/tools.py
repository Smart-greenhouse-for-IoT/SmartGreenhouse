def searchDict(dict,key_lst, key, value):
        # Search a device given name or ID
        #TODO: possible to output different dictionaries associated to key
        found_dev = {}
        for device in dict[key_lst]:
            if device[key] == value:
                found_dev = device.copy()
        return found_dev

def generateID(id_lst):
    new_id = id_lst[-1] + 1
    # Check if new id is already present
    while id_lst.count(new_id) > 0:
           new_id += 1
    return new_id