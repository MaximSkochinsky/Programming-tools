from modules.options import *
from modules.classes import *
import inspect
import types
from types import FunctionType


class Custom_Serializer:

    def object_to_json(self, obj):
        if str(obj).__contains__("object"):
            struct = {'__type__': 'object', '__class__': obj.__class__.__name__}
            for attr in obj.__dir__():  
                if not attr.startswith('__'):
                    attr_value = getattr(obj, attr)
                    if callable(attr_value):
                        if len(inspect.getfullargspec(attr_value).args) > 1:
                            struct[attr] = self.function_to_json(attr_value)  
                    elif str(attr_value).__contains__("object"):
                        struct[attr] = self.object_to_json(attr_value)
                    else:
                        struct[attr] = attr_value
            return struct        
        raise Exception("Only object")



    def class_to_json(self, cl):
        if cl.__class__.__name__ == "type":
            struct = {'__type__': 'class', '__class__': cl}
            for attr in dir(cl):   
                if not attr.startswith('__'):
                    attr_value = getattr(cl, attr) 
                    if "<class 'type'>"  in str(attr_value.__class__): 
                        struct[attr] = self.class_to_json(attr_value)
                    elif "<class '__main__." in str(attr_value.__class__): 
                        struct[attr] = self.object_to_json(attr_value)     
                    elif callable(attr_value):
                        if len(inspect.getfullargspec(attr_value).args) > 1:
                            struct[attr] = self.function_to_json(attr_value)                   
                    else:
                        struct[attr] = attr_value
            return struct



    def function_to_json(self, funct):
        struct = {'__type__': 'function'}
        args = []
        if str(funct).__contains__('lambda'):
            s = str(inspect.getsource(funct)[inspect.getsource(funct).find("lambda"):])
            struct['code'] = s
            return struct
        elif funct.__name__.startswith('__') :
            struct['name'] = funct.__name__
            args = inspect.getfullargspec(funct).args
            struct['args'] = args 
            return struct    
        else:   
            globs = {}
            name = funct.__name__
            func_code = inspect.getsource(funct)
            if func_code.__contains__('global'):
                subs = func_code.split('global')
                for i in range(1, len(subs)):
                    glob_key = subs[i].lstrip().split("\n")[0]
                    globs.update(dict([(glob_key, funct.__globals__[glob_key])]))

            struct['name'] = name
            struct['globals'] = globs
            struct['code'] = func_code
            return struct



    def json_to_function(self, json):
            
            if (json.get('name')):
                func = json["globals"]
                s_func = json["code"].split("\n")
                if s_func[0].count("    ") == 1:
                    s_func[0] = s_func[0].lstrip() + "\n"
                    for i in range(1, len(s_func) - 1):
                        tabs = int(s_func[i].count("    ") - 1)
                        s_func[i] = "    " * tabs + s_func[i].lstrip() + "\n"
                    exec("".join(s_func), func)
                else:    
                    exec(json["code"], func)
                return func[json['name']]
            else:
                json['code'] = json['code'].strip()
                foo_code = compile(json['code'],'file2.py',"exec")
                return FunctionType(foo_code.co_consts[0], globals(), 'lambda')

        


    def json_to_object(self, json):
        class_name = globals()[json['__class__']]
        init_args = inspect.getfullargspec(class_name).args
        args = {}
        for arg in init_args:
            if arg in json:
                args[arg] = json[arg]
        obj = class_name(**args) 
        for attr in obj.__dir__():
            if isinstance(getattr(obj, attr), dict) and not attr.startswith('__'):
                object_attr  = self.json_to_object(getattr(obj, attr))
                setattr(obj, attr, object_attr)            
            elif not attr.startswith('__') and attr not in args:
                object_attr = getattr(obj, attr)
                if not callable(object_attr):
                    setattr(obj, attr, json[attr])
        return obj




    def json_to_class(self, json):
        vars = {}
        argsN = []
        for attr in json:
            if not isinstance(json[attr], dict) and not attr.startswith('__'):
                vars[attr] = json[attr];
            elif isinstance(json[attr], dict) and not attr.startswith('__'):
                if json[attr]['__type__'] == 'function':
                    vars[attr] = self.json_to_function(json[attr]) 
                
        return type("User", (object, ), vars)  





    def make_dictionary(self, obj, obj_type):
        if obj_type == "class":
            return self.class_to_json(obj)
        elif obj_type == "function":
            return self.function_to_json(obj)
        elif obj_type == "object":
            return self.object_to_json(obj)


        raise Exception("Invalid type!!!") 

        

    def make_entity(self, dictionary):
        if dictionary["__type__"] == 'function':
            return self.json_to_function(dictionary)
        elif dictionary['__type__'] == 'object':
            return self.json_to_object(dictionary)
        elif dictionary['__type__'] == 'class':
            return self.json_to_class(dictionary)
        
        raise Exception("Invalid type!!!")


    
    def getDictionary(self, obj, tp):
        check = (False, True)[inputValidation(obj, tp)]
        if not check: raise Exception("Incorrect input!")
        dict_obj = self.make_dictionary(obj, tp)
        return dict_obj



