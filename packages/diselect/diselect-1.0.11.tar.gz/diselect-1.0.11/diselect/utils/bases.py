class ParameterBase:

    def __init__(self, *args, **kwargs):
        pass

    def as_kwargs(self):
        return self.__dict__
        

    

