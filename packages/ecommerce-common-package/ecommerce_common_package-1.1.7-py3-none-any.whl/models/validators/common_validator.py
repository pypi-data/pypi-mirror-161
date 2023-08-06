import re

class StringValidator:
    def __init__(self, max_length=None):
        self.max_length = max_length    
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = '_' + name
    def __get__(self, obj, objtype = None):
        value = getattr(obj, self.private_name)
        return value      
    def __set__(self, obj, value):
        if value is None:
            raise ValueError(f'{self.name} code cannot be null')
        elif len(value) > self.max_length:
            raise ValueError(f'{self.name} must be less than {self.max_length} characters long')
        else:
            setattr(obj, self.private_name, value)

class NumberValidator:
    def __init__(self, max_value=None):
        self.max_value = max_value
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = '_' + name
    def __get__(self, obj, objtype = None):
        value = getattr(obj, self.private_name)
        return value  
    def __set__(self, obj, value):
        if value is None:
            raise ValueError(f'{self.name} code cannot be null')
        elif self.max_value is not None and float(value) > self.max_value:
            raise ValueError(f'{self.name} must be less than {self.max_value}')
        else:
            setattr(obj, self.private_name, value)
            
class DateValidator:
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = '_' + name
    def __get__(self, obj, objtype = None):
        value = getattr(obj, self.private_name)
        return value
    def __set__(self, obj, value):
        regex = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
        if value is None:
            raise ValueError(f'{self.name} code cannot be null')
        elif not re.match(regex, value):
            raise ValueError(f'{self.name} must be valid')
        else:
            setattr(obj, self.private_name, value)
        
            
class EmailValidator:
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = '_' + name
    def __get__(self, obj, objtype = None):
        value = getattr(obj, self.private_name)
        return value
    def __set__(self, obj, value):
        regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
        if value is None:
            raise ValueError(f'{self.name} cannot be null')
        elif not re.match(regex, value):
            raise ValueError(f'{self.name} must be valid')
        elif value == '':
            raise ValueError(f'{self.name} cannot be empty')
        else:
            setattr(obj, self.private_name, value)
                           
class PhoneValidator:
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = '_' + name
    def __get__(self, obj, objtype = None):
        value = getattr(obj, self.private_name)
        return value
    def __set__(self, obj, value):
        regex = "^\+[1-9]{1}[0-9]{3,14}$"
        if value is None:
            raise ValueError(f'{self.name} cannot be null')
        elif not re.match(regex, value):
            raise ValueError(f'{self.name} must be valid')
        else:
            setattr(obj, self.private_name, value)