import inspect
import json
from types import FunctionType


class User:
    def __init__(self, arg1, arg2, comp):
        self.arg1 = arg1
        self.arg2 = arg2
        self.comp = comp

    name = 'John Smith'
    address = 'New York'
    
    class Player:
        score = 1
        
    
    

    def some_method(self, some_arg, some_arg_2):
        # pass if has arg
        return self.name
    

class Computer:
    def __init__(self, model, num, proc):
        self.model = model
        self.num = num
        self.proc = proc
        self.mas = [1, 2, 3, 4]
        
class Processor:
    def __init__(self, model):
        self.model = model
        
        
   
    


def object_to_json(obj):
    if "<class '__main__." in str(obj.__class__):
        struct = {'__type__': 'object', '__class__': obj.__class__.__name__}
        for attr in obj.__dir__():
            if attr == "__init__":
                attr_value = getattr(obj, attr)
                struct[attr] = function_to_json(attr_value)  
            if not attr.startswith('__'):
                attr_value = getattr(obj, attr)
                if callable(attr_value):
                    if len(inspect.getfullargspec(attr_value).args) > 1:
                        struct[attr] = function_to_json(attr_value)  
                elif "<class '__main__." in str(attr_value.__class__): 
                    struct[attr] = object_to_json(attr_value)
                else:
                    struct[attr] = attr_value
        return struct 
    elif obj.__class__.__name__ == "type":
        struct = {'__type__': 'class', '__class__': obj}
        for attr in dir(obj):
            if attr == "__init__":
                attr_value = getattr(obj, attr)
                struct[attr] = function_to_json(attr_value)            
            if not attr.startswith('__'):
                attr_value = getattr(obj, attr) 
                if "<class 'type'>"  in str(attr_value.__class__): 
                    struct[attr] = object_to_json(attr_value)
                elif callable(attr_value):
                    if len(inspect.getfullargspec(attr_value).args) > 1:
                        struct[attr] = function_to_json(attr_value)                   
                else:
                    struct[attr] = attr_value
        return struct       
    raise Exception("Only object")







def function_to_json(func):
    struct = {'__type__': 'function'}
    struct['name'] = func.__name__
    args = []
    if func.__name__.startswith('__'):
        args = inspect.getfullargspec(func).args
        struct['args'] = args  
        struct['return'] = inspect.getsourcelines(func)     
    else:   
        for arg in func.__code__.co_varnames: 
            if arg == "class_name":
                break
            args.append(arg)
        struct['args'] = args     
        struct['code'] = inspect.getsource(func)
    return struct



def json_to_func(json):
    if json['__type__'] != 'function': return
    foo_code = compile(inspect.getsource(func), "<string>", "exec")
    foo_func = FunctionType(foo_code.co_consts[0], globals(), "foo")
    return foo_func

    


def json_to_object(json):
    class_name = globals()[json['__class__']]
    init_args = inspect.getfullargspec(class_name).args
    args = {}
    for arg in init_args:
        if arg in json:
            args[arg] = json[arg]
    obj = class_name(**args) 
    for attr in obj.__dir__():
        if isinstance(getattr(obj, attr), dict) and not attr.startswith('__'):
            object_attr  = json_to_object(getattr(obj, attr))
            setattr(obj, attr, object_attr)            
        elif not attr.startswith('__') and attr not in args:
            object_attr = getattr(obj, attr)
            if not callable(object_attr):
                setattr(obj, attr, json[attr])
    return obj


    


processor = Processor("Intel Core i5")
computer = Computer("Dell", 10, processor)
user = User(5, 10, computer)
user.address = 'Minsk'


def func(n, m):
    return n * m


jsonN = function_to_json(func)
print(jsonN)


function = json_to_func(jsonN)

print(function(4, 2))