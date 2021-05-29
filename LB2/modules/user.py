from modules.entrypoint import * 
from modules.arg import *
from modules.classes import * 
from modules.customSerializer import Custom_Serializer


user = Person("Max", None)
person = Person("Mike", user)


custom_serializer = Custom_Serializer()


json = custom_serializer.object_to_json(person)



obj = custom_serializer.json_to_object(json)

print(obj)