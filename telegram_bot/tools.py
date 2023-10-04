def searchDict(dict,key_lst, key, value, index=False):
        # Search a device given name or ID
        #TODO: possible to output different dictionaries associated to key
        found_dev = {}
        found_ind = None
        for ind, device in enumerate(dict[key_lst]):
            if device[key] == value:
                found_dev = device.copy()
                found_ind = ind
        if index == True:
            return found_ind,found_dev
        else:
             return found_dev

def generateID(id_lst):
    if id_lst:
        new_id = id_lst[-1] + 1
        # Check if new id is already present
        while id_lst.count(new_id) > 0:
               new_id += 1
        return new_id
    else:
         return 1