
# créations des niveaux pour Brick Shooter
# chaque niveau est une grille de 10x10 grid
# 'X' représente une cellule vide.
# '0'-'7' represente l'index dans BLOCK_COLORS.


LEVEL_DATA = [
    # Level 1 - Le classique
    [
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXX01XXXX",
        "XXXX10XXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
    ],
    # Level 2 - La croix
    [
        "XXXXXXXXXX",
        "XXXX0XXXXX",
        "XXXX1XXXXX",
        "XX01210XXX",
        "XXXX1XXXXX",
        "XXXX0XXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
    ],
    # Level 3 - Le rond
    [
        "XXXXXXXXXX",
        "XXX010XXXX",
        "XX1XXX1XXX",
        "XX0XXX0XXX",
        "XX1XXX2XXX",
        "XXX201XXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
    ],
    # Level 4 - Le Fromage
    [
        "XXXXXXXXXX",
        "XX010101XX",
        "XX101010XX",
        "XX010101XX",
        "XX121212XX",
        "XX212121XX",
        "XX121212XX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
    ],
    # Level 5 - Les Diamants Jumeaux
    [
        "XXXXXXXXXX",
        "XXXX0XXXXX",
        "XXX010XXXX",
        "XXXX0XXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXX2XXXXX",
        "XXX212XXXX",
        "XXXX2XXXXX",
        "XXXXXXXXXX",
    ],
    # Level 6 - Les deux iles
    [
        "XXXXXXXXXX",
        "XX01XXXXXX",
        "XX10XXXXXX",
        "XXXXXX23XX",
        "XXXXXX32XX",
        "XXXXXXXXXX",
        "XX32XXXXXX",
        "XX23XXXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
    ],
    # Level 7 - The Hourglass
    [
        "XXXXXXXXXX",
        "XX012321XX",
        "XXX1321XXX",
        "XXXX21XXXX",
        "XXXX32XXXX",
        "XXX2032XXX",
        "XX123102XX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
    ],
    # Level 8 - Scattered Gems
    [
        "XXXXXXXXXX",
        "XX0XX1XX2X",
        "XX1XX2XX0X",
        "XXXXXXXXXX",
        "XX2XX0XX1X",
        "XX0XX1XX2X",
        "XXXXXXXXXX",
        "XX1XX2XX0X",
        "XX2XX0XX1X",
        "XXXXXXXXXX",
    ],
    # Level 9 - The Walled Garden
    [
        "XXXXXXXXXX",
        "XX012301XX",
        "XX4XXXX4XX",
        "XX0X12X0XX",
        "XX1X34X1XX",
        "XX2X01X2XX",
        "XX3XXXX3XX",
        "XX012301XX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
    ],
    # Level 10 - Spiral Chaos
    [
        "XXXXXXXXXX",
        "XX012345XX",
        "XXXXXXXXXX",
        "XX5XXXX0XX",
        "XX4X21X1XX",
        "XX3X02X2XX",
        "XX2XXXX3XX",
        "XX105434XX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
    ]
]
