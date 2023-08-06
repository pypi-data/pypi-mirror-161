from complex_json.complex_serializer import ComplexJsonSerializer
from models.validators.geoinfo_validator import PostalCode
from models.validators.common_validator import EmailValidator, PhoneValidator, StringValidator, NumberValidator

from models.abstract.dto import ModelDto

class GeoInfo(ComplexJsonSerializer, ModelDto):
    id = NumberValidator()
    postal_code = PostalCode()
    city = StringValidator(255)
    province = StringValidator(255)
    country = StringValidator(255)
    
    def __init__(self, postal_code, city, province, country):
        self.errors: list[ValueError] = []
        try:
            self.id = 0
        except ValueError as e:
            self.errors.append(e)
        try:
            self.postal_code = postal_code
        except ValueError as e:
            self.errors.append(e)
        try:
            self.city = city
        except ValueError as e:
            self.errors.append(e)
        try:
            self.province = province
        except ValueError as e:
            self.errors.append(e)
        try:
            self.country = country
        except ValueError as e:
            self.errors.append(e)
    
    def toJson(self):
        return {
            'postal_code': self.postal_code,
            'city': self.city,
            'province': self.province,
            'country': self.country
        }    

class Customer(ComplexJsonSerializer, ModelDto):
    id = NumberValidator()
    name = StringValidator(255)
    surname = StringValidator(255)
    email = EmailValidator()
    origin = StringValidator(255)
    # phone = PhoneValidator()
    phone = StringValidator(12)
    
    def __init__(self, name, surname, email, origin, phone, geo_info: GeoInfo):
        self.errors: list[ValueError] = []
        try:
            self.id = 0
        except ValueError as e:
            self.errors.append(e)
        try:
            self.name = name
        except ValueError as e:
            self.errors.append(e)
        try:
            self.surname = surname
        except ValueError as e:
            self.errors.append(e)
        try:
            self.email = email
        except ValueError as e:
            self.errors.append(e)
        try:
            self.origin = origin
        except ValueError as e:
            self.errors.append(e)
        try:
            self.phone = phone
        except ValueError as e:
            self.errors.append(e)
        self.geo_info = geo_info
    
    def toJson(self):
        return {
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'origin': self.origin,
            'phone': self.phone,
            'geo_info': self.geo_info.toJson()
        }