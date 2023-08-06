from collections import defaultdict
import sys


class ServiceBase:
    def __init__(self):
        self.functions = defaultdict(dict)

    def get(self, _name):
        def wrapper(f):
            return self.action("get", _name)(f)
        return wrapper

    def put(self, _name):
        def wrapper(f):
            return self.action("put", _name)(f)
        return wrapper
    
    def exploit(self, _name):
        def wrapper(f):
            return self.action("exploit", _name)(f)
        return wrapper

    def ping(self, f):
        return self.action("ping")(f)

    def action(self, action, _name="default"):
        def decorator(f):
            self.functions[action][_name] = f
        return decorator

    def parce_args(self):
        action = sys.argv[1]
        if len(sys.argv) == 3:
            return self.functions[action]["default"](sys.argv[2])
        elif len(sys.argv) == 4:
            return self.functions[action][sys.argv[3]](sys.argv[2])
        elif len(sys.argv) == 5:
            return self.functions[action][sys.argv[3]](sys.argv[2], sys.argv[4])

    def run(self):
        result = self.parce_args()
        if not result:
            print(0, end="\n")
        else:
            print(result, end="\n")