class Column:
    def __init__(self, field_type, **kwargs):
        self.constraints = tuple(
            ['type', 'not_null', 'default', 'primary_key', 'autoincrement', 'unique', 'foreign_key', ])
        self.constraints_values = tuple([
            field_type().get_type(),
            True if kwargs.get('not_null') else False,
            kwargs.get('default') or None,
            True if kwargs.get('primary_key') else False,
            True if kwargs.get('autoincrement') else False,
            True if kwargs.get('unique') else False,
            kwargs.get('foreign_key') or None,
        ])

    def keywords(self):
        return tuple([tuple([kw, self.keyword_format(kw, value)]) for kw, value in zip(
            self.constraints, self.constraints_values) if value])

    @staticmethod
    def keyword_format(kw, value):
        if kw == 'default':
            return 'DEFAULT {}'.format(value)
        elif kw in ['type', 'on_delete', 'on_update']:
            return value.upper()
        elif kw == 'foreign_key':
            fk = value if isinstance(value, str) else str(value)
            return '{}({})'.format(*fk.split('.'))
        return kw.upper().replace('_', ' ')
