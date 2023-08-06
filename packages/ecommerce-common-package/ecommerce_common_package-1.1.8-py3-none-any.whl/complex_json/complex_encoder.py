import json

from .complex_serializer import ComplexJsonSerializer

class ComplexEncoder(json.JSONEncoder):
    
    """
    Classe che permette di convertire un oggetto in una stringa JSON, data la funzione toJson() implementata correttamente
    
    """
    
    def default(self, obj):
        if issubclass(type(obj), ComplexJsonSerializer):
            return obj.toJson()
        else:
            return json.JSONEncoder.default(self, obj)