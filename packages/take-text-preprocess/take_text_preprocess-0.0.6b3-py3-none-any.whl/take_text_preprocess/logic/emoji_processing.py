import emoji
import re

from .remove_non_ascii_symbols import remove_non_ascii_symbol_characters


def process_emoji(sentence: str, processing_parameters: list) -> str:
    """Remove non-ascii character but keeps emojis

    The skin tone emoji is removed from the sentence

    :param sentence: Text to be processed.
    :type sentence: `str`

    :param processing_parameters: Preprocessing options to be applied.
    :type processing_parameters: list

    :return: Processed text without non-ascii and with emoji
    :rtype: `str`
    """
    sentence = emoji.demojize(sentence)

    sentence = remove_skin_tone(sentence)

    sentence = remove_non_ascii_symbol_characters(sentence,
                                                  processing_parameters)

    return emoji.emojize(sentence)


def remove_skin_tone(sentence: str) -> str:
    """Remove skin tone emoji  from a sentence

    :param sentence: Text to be processed
    :type sentence: str

    :return: Sentence without skin tone emoji
    :rtype: str
    """
    pattern = r'\s:[A-Za-z]+_skin_tone:'
    return re.sub(pattern, '', sentence)
