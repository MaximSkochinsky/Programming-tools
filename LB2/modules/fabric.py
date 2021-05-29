from modules.serializers import *



def create_serializer(form):
    if (form == "json"):
        return JSON_Serializer()
    if (form == "yaml"):
        return YAML_Serializer()
    if (form == "pickle"):
        return PICKLE_Serializer()
    if (form == "toml"):
        return TOML_Serializer()




def create_serializers(input_format, output_format):

    if (input_format == "json"):
        deserializer = create_serializer("json")
    elif (input_format == "pickle"):
        deserializer = create_serializer("pickle")
    elif (input_format == "toml"):
        deserializer = create_serializer("toml")
    elif (input_format == "yaml"):
        deserializer = create_serializer("yaml")
    else: raise Exception("Invalid format!!!")


    if (output_format == "json"):
        serializer = create_serializer("json")
    elif (output_format == "pickle"):
        serializer = create_serializer("pickle")
    elif (output_format == "toml"):
        serializer = create_serializer("toml")
    elif (output_format == "yaml"):
        serializer = create_serializer("yaml")
    else: 
        raise Exception("Invalid format!!!")


    return (serializer, deserializer)
