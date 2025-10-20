class XYBException(Exception):
    pre: str = ''
    code: int = 00
    def __init__(self, message: str):
        super().__init__(message)
        self.message = f'{self.pre}{self.code}: {message}'