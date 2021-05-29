from modules.customSerializer import Custom_Serializer
import pickle
import toml
import yaml
import json





class TOML_Serializer(Custom_Serializer):

    def dump(self, obj, fp, tp):
        dict_obj = self.getDictionary(obj, tp)
        with open(fp, "w") as file:
            toml.dump(dict_obj, file)
            file.close()
        return 1

    def dumps(self, obj, tp):
        dict_obj = self.getDictionary(obj, tp)
        toml_obj = toml.dumps(dict_obj)
        return toml_obj


    def loads(self, s):
        dict_obj = toml.loads(s)
        entity = super().make_entity(dict_obj)
        return entity

    def load(self, fp):
        dict_obj = None
        with open(fp, "r") as file:
            dict_obj = toml.load(file)
            file.close()
        entity = super().make_entity(dict_obj)
        return entity








class YAML_Serializer(Custom_Serializer):
    
    def dump(self, obj, fp, tp):
        dict_obj = super().getDictionary(obj, tp)
        with open(fp, "w") as file:
            yaml.dump(dict_obj, file)
            file.close()
        return 1

    def dumps(self, obj, tp):
        dict_obj = super().getDictionary(obj, tp)
        yaml_obj = yaml.dump(dict_obj)
        return yaml_obj

    def loads(self, s):
        dict_obj = yaml.unsafe_load(s)
        entity = super().make_entity(dict_obj)
        return entity

    def load(self, fp):
        dict_obj = None
        with open(fp, "r") as file:
            dict_obj = yaml.load(file, Loader=yaml.FullLoader)
            file.close()
        entity = super().make_entity(dict_obj)
        return entity




class PICKLE_Serializer(Custom_Serializer):
    
    def dump(self, obj, fp, tp):
        dict_obj = super().getDictionary(obj, tp)
        with open(fp, "wb") as file:
            pickle.dump(dict_obj, file)
            file.close()
        return 1

    def dumps(self, obj, tp):
        dict_obj = super().getDictionary(obj, tp)
        pickle_obj = pickle.dumps(dict_obj)
        return pickle_obj

    def loads(self, s):
        dict_obj = pickle.loads(s)
        entity = super().make_entity(dict_obj)
        return entity

    def load(self, fp):
        dict_obj = None
        with open(fp, "rb") as file:
            dict_obj = pickle.load(file)
            file.close()
        entity = super().make_entity(dict_obj)
        return entity



class JSON_Serializer(Custom_Serializer):
    
    def dump(self, obj, fp, tp):
        dict_obj = super().getDictionary(obj, tp)
        with open(fp, "w") as file:
            json.dump(dict_obj, file)
            file.close()
        return 1

    def dumps(self, obj, tp):
        dict_obj = super().getDictionary(obj, tp)
        json_obj = json.dumps(dict_obj)
        return json_obj

    def loads(self, s):
        dict_obj = json.loads(s)
        entity = super().make_entity(dict_obj)
        return entity

    def load(self, fp):
        dict_obj = None
        with open(fp, "r", encoding='utf-8') as file:
            dict_obj = json.load(file)
            file.close()
        entity = super().make_entity(dict_obj)
        return entity
