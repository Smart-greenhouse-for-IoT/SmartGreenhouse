def searchDict(dict,key_lst, key, value):
        # Search a device given name or ID
        #TODO: possible to output different dictionaries associated to key
        found_dev = {}
        for device in dict[key_lst]:
            if device[key] == value:
                found_dev = device.copy()
        return found_dev