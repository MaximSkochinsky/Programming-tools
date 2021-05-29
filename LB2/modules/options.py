

def inputValidation(obj, tp):
    if obj.__class__.__name__ == "function" and tp == "function":
        return True
    if obj.__class__.__name__ == "type" and tp == "class":
        return True
    if str(obj).__contains__("object")  and tp == "object":
        return True

    return False



def get_type(obj):
    if (obj.__class__.__name__ == "function"): 
        return "function"
    elif obj.__class__.__name__ == "type":
        return "class"
    elif str(obj).__contains__("object"):
        return "object"
    else: 
        raise Exception("Invalid entity!")

    return tp




