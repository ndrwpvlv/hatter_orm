class Field:
    def __init__(self):
        self.type = None

    def get_type(self):
        return self.type


class IntegerField(Field):
    def __init__(self):
        super(IntegerField, self).__init__()
        __name__ = 'Integer'
        self.type = __name__.upper()


class RealField(Field):
    def __init__(self):
        super(RealField, self).__init__()
        __name__ = 'Real'
        self.type = __name__.upper()


class TextField(Field):
    def __init__(self):
        super(TextField, self).__init__()
        __name__ = 'Text'
        self.type = __name__.upper()


class BlobField(Field):
    def __init__(self):
        super(BlobField, self).__init__()
        __name__ = 'Blob'
        self.type = __name__.upper()
