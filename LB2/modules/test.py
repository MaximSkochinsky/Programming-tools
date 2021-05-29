import unittest
from modules.entrypoint import *
from modules.arg import *
from modules.serializers import *
from modules.fabric import create_serializer
from modules.file1 import *





class TestSerializers(unittest.TestCase):
     
    def setUp(self):


        self.make_files = make_files
        self.custom_serializer = Custom_Serializer()
        self.user = user
        self.func = func
        self.lambd = lambda x, y, z: x * y + z
        self.yaml_serializer = create_serializer("yaml")
        self.toml_serializer = create_serializer("toml")
        self.json_serializer = create_serializer("json")
        self.pickle_serializer = create_serializer("pickle")


        self.class_json = self.custom_serializer.class_to_json(User)
        self.object_json = self.custom_serializer.object_to_json(user)

        self.json_func = self.custom_serializer.function_to_json(func)
        self.json_glob_func = self.custom_serializer.function_to_json(f)



        (self.pair_pickle_serializer, self.pair_toml_serializer) = create_serializers('pickle', 'toml')
        (self.pair_json_serializer, self.pair_yaml_serializer) = create_serializers('json', 'yaml')


        self.pickle_lambda_str = self.pickle_serializer.dumps(self.lambd, "function")
        self.yaml_lambda_str = self.yaml_serializer.dumps(self.lambd, "function")
        self.toml_lambda_str = self.toml_serializer.dumps(self.lambd, "function")
        self.json_lambda_str = self.json_serializer.dumps(self.lambd, "function")

        self.pickle_str = self.pickle_serializer.dumps(user, "object")
        self.json_str = self.json_serializer.dumps(user, "object")
        self.toml_str = self.toml_serializer.dumps(user, "object")
        self.yaml_str = self.yaml_serializer.dumps(user, "object")

        self.class_pickle_str = self.pickle_serializer.dumps(User, "class")
        self.class_toml_str = self.toml_serializer.dumps(User, "class")
        self.class_yaml_str = self.yaml_serializer.dumps(User, "class")




    def test_custom_class_loads(self):
        self.assertEqual(self.custom_serializer.json_to_class(self.class_json).name, "Jonh Smith")

    def test_custom_object_loads(self):
        self.assertEqual(self.custom_serializer.json_to_object(self.object_json).func(1, 2), 3)

    def test_custom_function_loads(self):
        self.assertEqual(self.custom_serializer.json_to_function(self.json_func)(1, 2, 3), 6)

    def test_custom_global_function_loads(self):
        self.assertEqual(self.custom_serializer.json_to_function(self.json_glob_func)(1, 2), 8)

    



    def test_yaml_load(self):
        self.assertEqual(self.yaml_serializer.load("docs/input.yaml").__class__, user.__class__)

    def test_json_load(self):
        self.assertEqual(self.json_serializer.load("docs/input.json").__class__, user.__class__)

    def test_pickle_load(self):
        self.assertEqual(self.pickle_serializer.load("docs/input.pickle").__class__, user.__class__)

    def test_toml_load(self):
        self.assertEqual(self.toml_serializer.load("docs/input.toml").__class__, user.__class__)



    def test_pickle_dumps(self):
        self.assertEqual(self.pickle_serializer.dumps(user, "object"), self.pickle_str)

    def test_json_dumps(self):
        self.assertEqual(self.json_serializer.dumps(user, "object"), self.json_str)

    def test_toml_dumps(self):
        self.assertEqual(self.toml_serializer.dumps(user, "object"), self.toml_str)

    def test_yaml_dumps(self):
        self.assertEqual(self.yaml_serializer.dumps(user, "object"), self.yaml_str)





    def test_pickle_loads(self):
        self.assertEqual(self.pickle_serializer.loads(self.pickle_str).__class__, user.__class__)

    def test_json_loads(self):
        self.assertEqual(self.json_serializer.loads(self.json_str).__class__, user.__class__)

    def test_toml_loads(self):
        self.assertEqual(self.toml_serializer.loads(self.toml_str).__class__, user.__class__)

    def test_toml_loads(self):
        self.assertEqual(self.yaml_serializer.loads(self.yaml_str).__class__, user.__class__)





    def test_pickle_dumps_function(self):
        self.assertEqual(self.pickle_serializer.dumps(self.lambd, "function"), self.pickle_lambda_str)

    def test_json_dumps_function(self):
        self.assertEqual(self.json_serializer.dumps(self.lambd, "function"), self.json_lambda_str)

    def test_toml_dumps_function(self):
        self.assertEqual(self.toml_serializer.dumps(self.lambd, "function"), self.toml_lambda_str)

    def test_yaml_dumps_function(self):
        self.assertEqual(self.yaml_serializer.dumps(self.lambd, "function"), self.yaml_lambda_str)




    def test_pickle_loads_function(self):
        self.assertEqual(self.pickle_serializer.loads(self.pickle_lambda_str)(2, 2, 2), 6)

    def test_json_loads_function(self):
        self.assertEqual(self.json_serializer.loads(self.json_lambda_str)(2, 3, 4), 10)

    def test_toml_loads_function(self):
        self.assertEqual(self.toml_serializer.loads(self.toml_lambda_str)(1, 3, 2), 5)

    def test_yaml_loads_function(self):
        self.assertEqual(self.yaml_serializer.loads(self.yaml_lambda_str)(1, 2, 3), 5)





    def test_pickle_loads_class(self):
        self.assertEqual(self.pickle_serializer.loads(self.class_pickle_str).name, "Jonh Smith")

    def test_yaml_loads_class(self):
        self.assertEqual(self.yaml_serializer.loads(self.class_yaml_str).name, "Jonh Smith")

    def test_toml_loads_class(self):
        self.assertEqual(self.toml_serializer.loads(self.class_toml_str).name, "Jonh Smith")



    def test_make_files(self):
        self.assertEqual(self.make_files(user, "object"), 1)

    






if __name__ == "__main__":
    unittest.main()
