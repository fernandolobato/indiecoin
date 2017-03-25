
def remove_dict_prefix(dictionary, prefix):
    """
    """
    data = {}

    for key,val in dictionary.iteritems():
        data[key.replace(prefix, '')] = val

    return data