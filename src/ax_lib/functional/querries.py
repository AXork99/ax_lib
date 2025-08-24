def querry_attr(obj, name):
    return lambda x: obj[x].get(name)
