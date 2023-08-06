"""
Data for use within the package

**ASSUMPTIONS**
    See init, no further assumptions to note

**LIMITATIONS**
    See init, no further limitations to note
"""
# -----------------------------------------------

FORMAT_PARTS = {'Y': 4, 'y': 2, 'm': 2, 'd': 2}

# -----------------------------------------------
# Disabling line too long, as these are just months of the year
#   and preferable to have each list on a single line

# pylint: disable=line-too-long

MONTH_NAMES = {
    'DE1': ['JAN', 'FEB', 'MRZ', 'APR', 'MAI', 'JUN', 'JUL', 'AUG', 'SEP', 'OKT', 'NOV', 'DEZ'],
    'DE2': ['JANUAR', 'FEBRUAR', 'MARZ', 'APRIL', 'MAI', 'JUNI', 'JULI', 'AUGUST', 'SEPTEMBER', 'OKTOBER', 'NOVEMBER', 'DEZEMBER'],
    'EN1': ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
    'EN2': ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER'],
    'ES1': ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'],
    'ES2': ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'],
    'FR1': ['JANV', 'FEVR', 'MARS', 'AVR', 'MAI', 'JUIN', 'JUIL', 'AOUT', 'SEPT', 'OCT', 'NOV', 'DEC'],
    'FR2': ['JANVIER', 'FEVRIER', 'MARS', 'AVRIL', 'MAI', 'JUIN', 'JUILLET', 'AOUT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DECEMBRE']
}

# -----------------------------------------------

SPLITS = {
    4: (
        ((2, 2), ('year', 'month')),
        ((1, 2), ('month', 'year'))
    ),
    '6Y2': (
        ((2, 2, 2), ('year', 'month', 'day')),
        ((2, 2, 2), ('month', 'year', 'day')),
        ((2, 2, 2), ('day', 'month', 'year'))
    ),
    6: (
        ((4, 2), ('year', 'month')),
        ((2, 4), ('month', 'year'))
    ),
    8: (
        ((4, 2, 2), ('year', 'month', 'day')),
        ((4, 2, 2), ('year', 'day', 'month')),
        ((2, 2, 4), ('month', 'day', 'year')),
        ((2, 2, 4), ('day', 'month', 'year')),
        # Assuming nobody would place the year in the middle.
    )
}

# -----------------------------------------------
# End.
