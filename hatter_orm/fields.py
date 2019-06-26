class Field:
    def __init__(self):
        self.name = None

    def get_type(self):
        return self.name.upper()


class IntegerField(Field):
    def __init__(self):
        super(IntegerField, self).__init__()
        self.name = 'Integer'


class RealField(Field):
    def __init__(self):
        super(RealField, self).__init__()
        self.name = 'Real'


class TextField(Field):
    def __init__(self):
        super(TextField, self).__init__()
        self.name = 'Text'


class BlobField(Field):
    def __init__(self):
        super(BlobField, self).__init__()
        self.name = 'Blob'
