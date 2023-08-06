from collections import defaultdict

META_TYPE_KEY = {
    'int': [
        'rows',
        'columns',
        'layers',
        'mrows',
        'mcolumns',
        'mrowres',
        'mcolumnres',
        'sections',
        'channels',
        'Zscan',
        'startnum',
    ],
    'float': ['xres', 'yres', 'zres', 'sectionres'],
}


class MosaicDict(defaultdict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_factory = list

    def update(self, item):
        key, val = list(item.items())[0]
        if not key or not val:
            pass
        elif key in META_TYPE_KEY['int']:
            self[key] = int(val)
        elif key in META_TYPE_KEY['float']:
            self[key] = float(val)
        elif 'XPos' in key:
            self['XPos'].append(int(val))
        elif 'YPos' in key:
            self['YPos'].append(int(val))
        else:
            self[key] = val
