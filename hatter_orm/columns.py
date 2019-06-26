class Column:
    def __init__(self, field_type, **kwargs):
        self.constraints = tuple(['type', 'not_null', 'default', 'primary_key', 'autoincrement', 'unique', 'foreign_key', ])
        self.constraints_values = (
            field_type().get_type(),
            kwargs.get('not_null', False),
            kwargs.get('default'),
            kwargs.get('primary_key', False),
            kwargs.get('autoincrement', False),
            kwargs.get('unique', False),
            kwargs.get('foreign_key'),
        )

    def keywords(self):
        return tuple((kw, self.keyword_format(kw, value)) for kw, value in zip(self.constraints, self.constraints_values) if value)

    @staticmethod
    def keyword_format(kw: str, value: any) -> str:
        if kw == 'default':
            return 'DEFAULT {}'.format(value)
        elif kw in ['type', 'on_delete', 'on_update']:
            return value.upper()
        elif kw == 'foreign_key':
            fk = value if isinstance(value, str) else str(value)
            return '{}({})'.format(*fk.split('.'))
        return kw.upper().replace('_', ' ')
