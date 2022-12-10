class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.db_object = self.__get_object()


    def __get_object(self):
        f = open(f'database/{self.db_name}.db', 'r')
        object = eval(f.read())
        f.close()
        return object


    def save(self):
        with open(f'database/{self.db_name}.db', 'w') as f:
            f.write(str(self.db_object))

