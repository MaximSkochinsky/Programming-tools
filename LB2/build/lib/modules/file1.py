from modules.entrypoint import *
from modules.serializers import *
from modules.customSerializer import *
from modules.file3 import *



def func(x, y, z):
    return x + y + z


def f(x, y):
    global s
    return x + y + s


lambd = lambda x, y: x + y



def return_string():
    toml_serializer = create_serializer('toml')
    yaml_serializer = create_serializer('yaml')

    string_toml = toml_serializer.dump(f, '../docs/input.toml', 'function')
    print(string_toml)
    string_yaml = yaml_serializer.dumps(lambd, '../docs/input.toml', "function")

    return (string_toml, string_yaml)
    



if __name__ == "__main__":
    return_string()
