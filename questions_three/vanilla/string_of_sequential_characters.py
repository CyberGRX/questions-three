from string import ascii_letters, digits


LETTERS_AND_NUMBERS = ascii_letters + digits


def string_of_sequential_characters(*, character_count):
    if type(character_count) is int and character_count > 0:
        loop_count = 0
        string = ""
        for n in range(character_count):
            if loop_count == len(LETTERS_AND_NUMBERS):
                loop_count = 0
            string += LETTERS_AND_NUMBERS[loop_count]
            loop_count += 1
        return string
    raise TypeError('character_count must be of Type int and greater than 0')
