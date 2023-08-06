from complex_json.complex_serializer import ComplexJsonSerializer
from models.validators.common_validator import StringValidator, NumberValidator


from models.abstract.dto import ModelDto

class Category(ComplexJsonSerializer, ModelDto):
    
    id = 0
    name = StringValidator(255)
    description = StringValidator(255)
    origin = StringValidator(255)
    
    def __init__(self, name, description, origin, child_categories: list['Category']):
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
            self.description = description
        except ValueError as e:
            self.errors.append(e)
        try:
            self.origin = origin
        except ValueError as e:
            self.errors.append(e)
        self.products: list[Product] = []
        self.child_categories = child_categories
        
    def toJson(self):
        # return dict(name=self.name, description=self.description, origin=self.origin, child_categories=[x.toJson() for x in self.child_categories])
        return dict(
            name=self.name,
            description=self.description,
            origin=self.origin,
            child_categories=list(self._recursiveJson(self.child_categories)),
            products = [x.toJson() for x in self.products]
        )

        
    def _recursiveJson(self, child_categories):
        for category in child_categories:
            yield category.toJson()
            yield from self._recursiveJson(category.child_categories)
           
    

class Product(ComplexJsonSerializer, ModelDto):    
    
    id = NumberValidator(max_value=None)
    name = StringValidator(255)
    sku = StringValidator(255)
    description = StringValidator(255)
    price = NumberValidator(max_value=None)
    product_code = StringValidator(255)
    origin = StringValidator(255)
    VATCode = NumberValidator(max_value=None)
    marginality = NumberValidator()
    reload = NumberValidator()
    
    def __init__(self, product_code, name, sku, description, price, origin, VATCode, marginality, reload):
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
            self.sku = sku
        except ValueError as e:
            self.errors.append(e)
        try:
            self.description = description
        except ValueError as e:
            self.errors.append(e)
        try:
            self.price = price
        except ValueError as e:
            self.errors.append(e)
        try:
            self.product_code = product_code
        except ValueError as e:
            self.errors.append(e)
        try:
            self.origin = origin
        except ValueError as e:
            self.errors.append(e)
        try:
            self.VATCode = VATCode
        except ValueError as e:
            self.errors.append(e)
        try:
            self.marginality = marginality
        except ValueError as e:
            self.errors.append(e)
        try:
            self.reload = reload
        except ValueError as e:
            self.errors.append(e)
        
    def toJson(self):
        return dict(name=self.name, sku=self.sku, description=self.description, price=self.price, product_code=self.product_code, origin=self.origin, VATCode=self.VATCode, marginality=self.marginality, reload=self.reload)