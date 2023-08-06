import re

class PostalCode:
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = '_' + name
    def __get__(self, obj, objtype = None):
        value = getattr(obj, self.private_name)
        return value
    def __set__(self, obj, value):
        regex = "^[0-9]*$"
        if value is None:
            raise ValueError('Postal code cannot be null')
        elif not re.match(regex, value):
            raise ValueError('Postal code must be valid')
        elif len(value) > 10:
            raise ValueError("Postal code must be less than 10 characters long")
        else:
            setattr(obj, self.private_name, value)