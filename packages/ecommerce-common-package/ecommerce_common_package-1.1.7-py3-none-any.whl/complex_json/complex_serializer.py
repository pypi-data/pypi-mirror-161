from abc import abstractmethod


class ComplexJsonSerializer:
    """
    Estendere da questa classe è necessario per l'utilizzo del complex Encoder presente nella libreria
    """
    @abstractmethod
    def toJson(self):
        pass
    
