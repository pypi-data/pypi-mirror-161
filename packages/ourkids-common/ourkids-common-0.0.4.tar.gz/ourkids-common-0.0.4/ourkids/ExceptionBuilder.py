from .exceptionBody import ExceptionBody
from .NotFoundException import NotFoundException

class ExceptionBuilder:
    
    @staticmethod
    def build(exception: BaseException) -> ExceptionBody:
        exceptionBody = ExceptionBody(
            cause = exception.__cause__,
            context = exception.__context__,
            traceback = exception.__traceback__,
            clazz = exception.__class__
        )
        
        return exceptionBody