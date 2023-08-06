
class ExceptionBody:
    def __init__(self, cause = None, 
                       traceback = None, 
                       context = None, 
                       clazz = None, 
                       name = None) -> None:
        self.cause = cause
        self.traceback = traceback
        self.context = context
        self.clazz = clazz
