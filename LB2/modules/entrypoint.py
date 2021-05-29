from modules.arg import *
from modules.classes import *
from modules.fabric import *
from modules.options import *



def make_files(obj, tp):
    
    TOMLSerializer = TOML_Serializer()
    TOMLSerializer.dump(obj, "docs/input.toml", tp) 
      
    PICKLESerializer = PICKLE_Serializer()
    PICKLESerializer.dump(obj, "docs/input.pickle", tp) 

    JSONSerializer = JSON_Serializer()
    JSONSerializer.dump(obj, "docs/input.json", tp) 

    YAMLSerializer = YAML_Serializer()
    YAMLSerializer.dump(obj, "docs/input.yaml", tp) 

    return 1




def main():
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    if(len(sys.argv) < 9 and not sys.argv.__contains__("-c")): print("No enough arguments")
    elif (args.config and len(sys.argv) > 9):
        raise Exception('Choose only one option: config file or manual input')
    check_validation(args.ifr, args.ofr, args.ifl, args.ofl)


    if (args.config):
        config = read_config(str(args.config))
        check_validation(config['ifr'], config['ofr'], config['ifl'], config['ofl'])

        (serializer, deserializer) = create_serializers(config['ifr'], config['ofr'])
        obj = deserializer.load(config['ifl'])
        tp = get_type(obj)
        serializer.dump(obj, config['ofl'], tp)
    else:
        (serializer, deserializer) = create_serializers(args.ifr, args.ofr)

        obj = deserializer.load(args.ifl)
        tp = get_type(obj)
        serializer.dump(obj, args.ofl, tp)




if __name__ == '__main__':
    main()




