import typing


def to_snake_case(value: typing.Any) -> str:
    """Convert the camelCase or PascalCase value into a snake_case value."""
    if value is None or value == "":
        return ""

    cleaned = str(value).replace("-", "_").strip()
    characters = [cleaned[0].lower()]
    for last_index, character in enumerate(cleaned[1:]):
        last_character = cleaned[last_index]
        was_lowercase = last_character.lower() == last_character
        is_lowercase = character.lower() == character
        if last_character == "_":
            characters.append(character.lower())
        elif was_lowercase and not is_lowercase:
            characters.append(f"_{character.lower()}")
        else:
            characters.append(character.lower())
    return "".join(characters).strip("_")
