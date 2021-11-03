""""
All Alma 'pickup-library' entries must resolve to one of these GFA 'delivery-stop' codes:
[ 'AN', 'ED', 'HA', 'OR', 'RO', 'SC' ]
"""

ALMA_PICKUP_TO_GFA_DELIVERY = {
    'ANNEX READING ROOM': 'AN',
    'ANNEX': 'AN',
    'DIGITAL_REQUEST_HAY': 'EH',        # this is an 'interpreted' alma-pickup-library
    'DIGITAL_REQUEST_NONHAY': 'ED',     # this is an 'interpreted' alma-pickup-library
    'Elec. Delivery (Annex Articles)': 'ED',
    'Electronic Delivery': 'ED',
    'Hay at Rock Reading Room': 'HA',
    'HAY': 'HA',
    'John Hay Library': 'HA',
    'Library Coll Annex': 'AN',
    'Orwig Music Library': 'OR',
    'ORWIG': 'OR',
    'PERSONAL_DELIVERY': 'RO',          # 2021-Aug-23 -- until I hear otherwise
    'ROCK': 'RO',
    'Rockefeller Library': 'RO',
    'SCI': 'SC',
    'Sciences Library': 'SC'
    }

# ALMA_PICKUP_TO_GFA_DELIVERY = {
#     'ANNEX': 'AN',
#     'ANNEX READING ROOM': 'AN',
#     'DIGITAL_REQUEST': 'ED',        # 2021-Aug-26 -- this is an 'interpreted' alma-pickup-library
#     'Elec. Delivery (Annex Articles)': 'ED',
#     'Electronic Delivery': 'ED',
#     'HAY': 'HA',
#     'Hay at Rock Reading Room': 'HA',
#     'John Hay Library': 'HA',
#     'Library Coll Annex': 'AN',
#     'ORWIG': 'OR',
#     'Orwig Music Library': 'OR',
#     'PERSONAL_DELIVERY': 'RO',      # 2021-Aug-23 -- until I hear otherwise
#     'ROCK': 'RO',
#     'Rockefeller Library': 'RO',
#     'SCI': 'SC',
#     'Sciences Library': 'SC'
#     }


"""
All Alma 'libraryCode' entries must resolve to one of these GFA 'location' codes:
[ 'QH', 'QS' ]
"""

ALMA_LIBRARY_CODE_TO_GFA_LOCATION = {
    'ANNEX': 'QS',
    'ANNEX_HAY': 'QH',
    # 'Electronic Delivery': 'ED',
    'HAY': 'QH',
    'ORWIG': 'QS',
    'ROCK': 'QS',
    'SCI': 'QS'
}
