"""Utils utilized in Turing Machine Implementation"""

translation = {
    "Hungry DJs": "0",
    "Green Gold": "1",
    "Two": "2",
    "Three": "3",
    "Four": "4",
    "Five": "5",
    "Six": "6",
    "Seven": "7",
    "Eight": "8",
    "Nine": "9",
    "No. 22": "22",
    "Submarine Dance": "42",
    "Blank Space": "#",
}


def track_name_to_symbol(track):
    """Converts track name to string symbol according to translation table."""

    if track["name"] in translation:
        track["name"] = translation[track["name"]]
