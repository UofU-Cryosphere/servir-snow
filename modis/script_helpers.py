import datetime

from lib import SourceFolder


def validate_types(ctx, _param, value):
    if not SourceFolder.valid_source_type(value):
        print('Invalid source data type\n' +
              'Possible options:\n' +
              ' * forcing\n' +
              ' * fraction')
        ctx.abort()
    else:
        return value


def parse_year(_ctx, _param, value):
    if value:
        return range(value, value + 1)
    else:
        return range(2000, datetime.date.today().year + 1)
