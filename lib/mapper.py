""""
All Alma 'pickup-library' entries must resolve to one of these GFA 'delivery-stop' codes:
[ 'AN', 'ED', 'HA', 'OR', 'RO', 'SC' ]
"""

ALMA_PICKUP_TO_GFA_DELIVERY = {
    'ANNEX': 'AN',
    'ANNEX READING ROOM': 'AN',
    'Elec. Delivery (Annex Articles)': 'ED',
    'Electronic Delivery': 'ED',
    'HAY': 'HA',
    'Hay at Rock Reading Room': 'HA',
    'John Hay Library': 'HA',
    'Library Coll Annex': 'AN',
    'ORWIG': 'OR',
    'Orwig Music Library': 'OR',
    'ROCK': 'RO',
    'Rockefeller Library': 'RO',
    'SCI': 'SC',
    'Sciences Library': 'SC'
    }



"""
All Alma 'libraryCode' entries must resolve to one of these GFA 'location' codes:
[ 'ED', 'QH', 'QS' ]
"""

ALMA_LIBRARY_CODE_TO_GFA_LOCATION = {
    'ANNEX': 'QS',
    'ANNEX_HAY': 'QH',
    'Electronic Delivery': 'ED',
    'ORWIG': 'QS',
    'ROCK': 'QS',
    'SCI': 'QS'
}
