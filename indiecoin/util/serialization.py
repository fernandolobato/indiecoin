

def remove_dict_prefix(dictionary, prefix):
    """ Recieves a dictionary in which all objects share a common
        key prefix that must be removed
    """
    data = {}

    for key, val in dictionary.iteritems():
        data[key.replace(prefix, '')] = val

    return data
