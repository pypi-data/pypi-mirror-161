from limeutils import oxford_comma


class ValidationError(Exception):
    def __init__(self, message='', choices: list = None):
        if choices:
            choices = choices and oxford_comma(choices) or ''
            self.message = message or f'Arguments can only be: {choices}.'
        else:
            self.message = message or 'Arguments must use the correct value or selection of values.'
        super().__init__(self.message)
        
    def __str__(self):
        return self.message


class RedisError(Exception):
    pass


