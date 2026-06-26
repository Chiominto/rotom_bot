from constants.aesthetics import Emojis
from utils.logs.debug_log import debug_log, enable_debug
from datetime import datetime
from zoneinfo import ZoneInfo

class HELD_ITEM_EMOJI:
    assaultvest = Emojis.assault_vest
    dragonscale = Emojis.DragonScale
    kingsrock = Emojis.KingsRock
    fairyfeather = Emojis.FairyFeather
    focusband = Emojis.FocusBand
    luckyegg = Emojis.LuckyEgg
    magnet = Emojis.Magnet
    hardstone = Emojis.hard_stone
    miracleseed = Emojis.MiracleSeed
    mysticwater = Emojis.MysticWater
    nevermeltice = Emojis.Nevermelt_Ice
    poisonbarb = Emojis.Poison_Barb
    razorfang = Emojis.RazorFang
    sharpbeak = Emojis.Sharp_Beak
    silkscarf = Emojis.Silk_Scarf
    silverpowder = Emojis.Silver_Powder
    softsand = Emojis.Soft_Sand
    spelltag = Emojis.Spell_Tag
    twistedspoon = Emojis.Twisted_Spoon
    electrizer = Emojis.Electirizer
    magmarizer = Emojis.Magmarizer
    blackglasses = Emojis.BlackGlasses
    charcoal = Emojis.Charcoal
    dragonfang = Emojis.DragonFang
    metalcoat = Emojis.MetalCoat
    razorclaw = Emojis.RazorClaw
    blackbelt = Emojis.BlackBelt
    duskball = Emojis.Duskball
    moonball = Emojis.Moonball


class HELD_ITEM_POKEMON:
    assaultvest = ["aggron", "shuckle"]
    blackbelt = ["makuhita", "hariyama", "throh", "sawk", "mankey"]
    blackglasses = ["poochyena", "mightyena", "sandile", "krokorok"]

    charcoal = ["numel", "camerupt", "vulpix", "ninetales", "torkoal"]

    dragonfang = [
        "horsea",
        "seadra",
        "kingdra",
        "dratini",
        "dragonair",
        "bagon",
        "shelgon",
        "druddigon",
    ]

    electrizer = ["electabuzz", "elekid"]

    magmarizer = ["magmar", "magby"]

    kingsrock = [
        "hawlucha",
        "makuhita",
        "hariyama",
        "poliwrath",
        "slowpoke",
        "slaking",
        "psyduck",
    ]

    dragonscale = ["seadra", "horsea", "dragonair", "dratini"]

    fairyfeather = ["ralts", "cleffa", "clefairy", "togepi"]

    focusband = ["machop", "machoke", "machamp"]

    luckyegg = ["blissey"]

    magnet = ["pikachu", "raichu", "magnemite", "magneton", "nosepass"]

    metalcoat = ["beldum", "metang", "bronzor", "bronzong", "skarmory", "magnemite"]

    hardstone = [
        "aron",
        "lairon",
        "aggron",
        "corsola",
        "geodude",
        "graveler",
        "golem",
        "onix",
        "steelix",
        "crustle",
        "dwebble",
        "roggenrola",
        "boldore",
    ]

    miracleseed = [
        "cherubi",
        "cherrim",
        "sunkernn",
        "sunflora",
        "formantis",
        "lurantis",
        "maractus",
    ]

    mysticwater = ["castform", "goldeen", "seaking", "dewpider", "araquanid", "lapras"]

    nevermeltice = [
        "seel",
        "dewgong",
        "snover",
        "abomasnow",
        "lapras",
        "cryogonal",
        "vanilite",
    ]

    poisonbarb = [
        "tentacool",
        "tentacruel",
        "skorupi",
        "drapion",
        "qwilfish",
        "weedle",
        "beedrill",
        "budew",
        "roselia",
        "ekans",
        "arbok",
        "cacnea",
        "cacturne",
        "vespiquen",
    ]

    razorclaw = ["hakamo-o", "jangmo-o", "sneasel"]

    razorfang = ["gligar", "bruxish"]

    sharpbeak = ["doduo", "dodrio", "spearow", "fearow"]

    silkscarf = ["trubbish", "garbodor", "zigzagoon", "linoone", "skitty", "delcatty"]

    silverpowder = ["butterfree", "venonat", "venomoth", "surskit", "masquerain"]

    softsand = [
        "diglett",
        "dugtrio",
        "nincada",
        "trapinch",
        "sandshrew",
        "sandslash",
        "trapinch",
        "stunfisk",
    ]

    spelltag = [
        "gastly",
        "haunter",
        "gengar",
        "duskull",
        "dusclops",
        "shuppet",
        "banette",
        "misdreavus",
        "sandygast",
        "yamask",
    ]

    twistedspoon = ["abra", "kadabra", "alakazam"]


held_item_list = [
    "assaultvest",
    "blackbelt",
    "blackglasses",
    "charcoal",
    "dragonfang",
    "electrizer",
    "magmarizer",
    "kingsrock",
    "dragonscale",
    "fairyfeather",
    "focusband",
    "luckyegg",
    "magnet",
    "hardstone",
    "metalcoat",
    "miracleseed",
    "mysticwater",
    "nevermeltice",
    "poisonbarb",
    "razorclaw",
    "razorfang",
    "sharpbeak",
    "silkscarf",
    "silverpowder",
    "softsand",
    "spelltag",
    "twistedspoon",
]


HELD_ITEMS_DICT = {}
for item in held_item_list:
    HELD_ITEMS_DICT[item] = {
        "pokemon": getattr(HELD_ITEM_POKEMON, item),
        "emoji": getattr(HELD_ITEM_EMOJI, item),
    }

MULTI_HELD_ITEM_POKEMON = {
    "aggron": ["assaultvest", "hardstone"],
    "makuhita": ["blackbelt", "kingsrock"],
    "hariyama": ["blackbelt", "kingsrock"],
    "seadra": ["dragonfang", "dragonscale"],  # duplicate in your dataset, can merge
    "horsea": ["dragonfang", "dragonscale"],
    "dratini": ["dragonfang", "dragonscale"],
    "dragonair": ["dragonfang", "dragonscale"],
    "lapras": ["mysticwater", "nevermeltice"],
    "magnemite": ["magnet", "metalcoat"],
}

# Battle Items
battle_items = [
    "assaultvest",
    "focusband",
    "kingsrock",
    "luckyegg",
]

# Type Boosters
type_boosters = [
    "magnet",
    "metalcoat",
    "charcoal",
    "dragonfang",
    "blackbelt",
    "blackglasses",
    "fairyfeather",
    "hardstone",
    "miracleseed",
    "mysticwater",
    "nevermeltice",
    "poisonbarb",
    "sharpbeak",
    "silkscarf",
    "silverpowder",
    "softsand",
    "spelltag",
    "twistedspoon",
]

# Evolution / Special Items
evolution_items = [
    "electrizer",
    "magmarizer",
    "dragonscale",
    "razorclaw",
    "razorfang",
]

# Balls
balls = [
    "duskball",
    "moonball",
]

# ─────────────────────────────
#  💎 Pretty names for items
# ─────────────────────────────
PRETTY_ITEM_NAMES = {
    "assaultvest": "Assault Vest",
    "blackbelt": "Black Belt",
    "blackglasses": "Black Glasses",
    "charcoal": "Charcoal",
    "dragonfang": "Dragon Fang",
    "electrizer": "Electrizer",
    "magmarizer": "Magmarizer",
    "kingsrock": "King's Rock",
    "dragonscale": "Dragon Scale",
    "fairyfeather": "Fairy Feather",
    "focusband": "Focus Band",
    "luckyegg": "Lucky Egg",
    "magnet": "Magnet",
    "hardstone": "Hard Stone",
    "metalcoat": "Metal Coat",
    "miracleseed": "Miracle Seed",
    "mysticwater": "Mystic Water",
    "nevermeltice": "Nevermeltice",
    "poisonbarb": "Poison Barb",
    "razorclaw": "Razor Claw",
    "razorfang": "Razor Fang",
    "sharpbeak": "Sharp Beak",
    "silkscarf": "Silk Scarf",
    "silverpowder": "Silver Powder",
    "softsand": "Soft Sand",
    "spelltag": "Spell Tag",
    "twistedspoon": "Twisted Spoon",
}


def pretty_item_name(item: str) -> str:
    """Return the properly formatted item name."""
    return PRETTY_ITEM_NAMES.get(item.lower(), item.title())


def is_midnight_est():
    """
    Returns True if the current time in America/New_York is between 12:00 AM and 12:59 AM.
    """
    nyc = ZoneInfo("America/New_York")
    now_nyc = datetime.now(nyc)
    return now_nyc.hour == 0


def is_nighttime_est():
    nyc = ZoneInfo("America/New_York")
    now_nyc = datetime.now(nyc)
    return now_nyc.hour >= 18 or now_nyc.hour < 7


# ─────────────────────────────
#  💎 Held Item Message
# ─────────────────────────────
def held_item_message(pokemon_name: str) -> str | None:
    """
    Generate a compact message for a Pokemon with held items.

    user_sub example:
        {
            "all_held_items": True,
            "subscribed_items": {"hardstone", "assaultvest", ...},
            "moonball": True,
            "duskball": True
        }
    """
    debug_log(f"held_item_message called for {pokemon_name}")

    nyc = ZoneInfo("America/New_York")
    now_nyc = datetime.now(nyc)
    debug_log(f"Current time in EST: {now_nyc.strftime('%Y-%m-%d %H:%M:%S')} ")

    held_item_phrase = f"{Emojis.held_item} item! "

    items_for_pokemon = [
        item
        for item, data in HELD_ITEMS_DICT.items()
        if pokemon_name.lower() in data["pokemon"]
    ]
    proper_pokemon_name = pokemon_name.title()

    # Special balls to show
    special_balls = []
    if is_midnight_est():
        debug_log(f"Midnight EST detected for {proper_pokemon_name}")
        special_balls.append(f"{Emojis.moonball} **__Moonball__**")
        debug_log(f"Added Moonball for {proper_pokemon_name}")
        special_balls.append(f"{Emojis.duskball} **__Duskball__**")
        debug_log(f"Added Duskball for {proper_pokemon_name}")
    elif is_nighttime_est():
        debug_log(f"Nighttime EST detected for {proper_pokemon_name}")
        special_balls.append(f"{Emojis.duskball} **__Duskball__**")
        debug_log(f"Added Duskball for {proper_pokemon_name}")
    else:
        debug_log(f"No special balls added for {proper_pokemon_name}")

    # No held items
    if not items_for_pokemon:
        debug_log(f"No held items for {proper_pokemon_name}")
        if special_balls:
            balls_str = " ".join(special_balls)
            debug_log(f"Special balls for {proper_pokemon_name}: {balls_str}")
            return f"{proper_pokemon_name} is holding an {held_item_phrase} (Special Item Chance: {balls_str})"
        else:
            debug_log(f"No special balls for {proper_pokemon_name}")
            return f"{proper_pokemon_name} is holding an {held_item_phrase}"

    # Held items
    items_to_show = []
    for item in items_for_pokemon:
        emoji = HELD_ITEMS_DICT[item]["emoji"]
        items_to_show.append(f"{emoji} **__{pretty_item_name(item)}__**")
    items_to_show.extend(special_balls)

    if not items_to_show:
        debug_log(f"No subscribed held items for {proper_pokemon_name}")
        return None

    if len(items_to_show) == 1:
        debug_log(f"One held item for {proper_pokemon_name}: {items_to_show[0]}")
        return f"{proper_pokemon_name} is holding an {held_item_phrase} (Special Item Chance: {items_to_show[0]})"
    else:
        items_str = " or ".join(items_to_show)
        debug_log(f"Multiple held items for {proper_pokemon_name}: {items_str}")
        return f"{proper_pokemon_name} is holding an {held_item_phrase} (Special Item Chance: {items_str})"
