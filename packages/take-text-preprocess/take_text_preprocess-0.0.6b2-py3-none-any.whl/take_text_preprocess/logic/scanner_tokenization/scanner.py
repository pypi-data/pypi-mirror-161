import typing as tp
import string

import emoji


class Scanner:
    """
    Class for scanning text and finding tokenizing numbers and codes.
    
    Methods:
    -------
        * get_tokens: reads a string and returns a list of tokens and a list of token types.
    """
    def __init__(self):
        """ Initializes the class with character groups. """
        # Attributes
        self.fragment: str  # reference to text fragment received by '__initialize_fragment()'
        self.token: str  # text of token returned by '__next_token()'
        self.token_id: str  # type of token returned
    
        # Protected
        self._letters = set(string.ascii_letters)
        self._letters = self._letters.union(set("ÁÀÂÃáàâãÉÈÊéàêÍÌíìÓÒÔÕóòôõÚÙúùÇç_"))
        self._digit = set("0123456789")
        self._ordinal = set("ºª")
        self._delimiter = set(" \r\n\t\'\"!#%&*()=+{[}]<><;?|@$")
        self._blank = set(" \r\n\t")  # also in self._delimiter
        self._numeric_part = set(":/-.,")  # not in delimiter
    
        self._length: int = 0  # length of text fragment
        self._pos: int = 0  # next character position on the text fragment
        self._current_character = " "  # current character being processed

    def get_tokens(self, input_text: str) -> tp.Tuple[tp.List[str]]:
        """ Reads a string and returns a list of tokens and a list of token types
        
        :param input_text: Text to be scanned.
        :type input_text: `str`
        :return: A tuple containing a list of the tokens and a list of the token types.
        :rtype: `tp.Tuple[tp.List[str]]`
        """
        self.__initialize_fragment(input_text)
        tokens = []
        token_ids = []

        while self.token_id != 'EOT':
            self.__next_token()
            tokens.append(self.token)
            token_ids.append(self.token_id)
        return tokens, token_ids
                        
    def __initialize_fragment(self, fragment: str) -> None:
        """ Initializes the text fragment being scanned.
        
        :param fragment: Text currently being scanned.
        :type fragment: `str`
        """
        self.fragment = fragment
        self.token = ""
        self.token_id = 'INVALID'
        
        self._length = len(self.fragment)
        self._pos = 0
        self._current_character = " "

    def __next_token(self) -> None:
        """ Moves scanner to the next token in the scanned text. """
        self.token = ""
        self.token_id = 'INVALID'
    
        self.__ignore_blanks()
    
        if self._current_character == "\0":
            self.token_id = 'EOT'
            return
    
        if self._current_character in self._letters:
            return self.__get_word()
    
        if self._current_character in self._delimiter.union(self._numeric_part):
            self.token_id = 'DELIMITER'
            self.token = self.token + self._current_character
            self.__get_next_char()
            return
    
        if self._current_character in self._digit:
            return self.__get_number()

        if emoji.is_emoji(self._current_character):
            self.token += self._current_character
            self.__get_next_char()
            return

    
        self.__get_next_char()
        return

    def __ignore_blanks(self) -> None:
        """ Ignores black characters in scanned text. """
        while self._current_character in self._blank:
            self.__get_next_char()
    
    def __get_next_char(self) -> None:
        """ Moves current character to the next one on the scanned text. """
        if self._pos >= self._length:
            self._current_character = "\0"
            return
        self._current_character = self.fragment[self._pos]
        self._pos += 1
    
    def __get_word(self) -> None:
        """ Matches words on scanned text. """
        self.token_id = 'WORD'
        while self._current_character in self._letters:
            self.token = self.token + self._current_character
            self.__get_next_char()
        if self._current_character in self._digit:
            self.__replace_to_code()

    def __get_number(self) -> None:
        """ Matches numbers on scanned text. """
        self.token_id = 'NUMBER'
        while self._current_character in self._digit.union(self._numeric_part):
            self.token = self.token + self._current_character
            self.__get_next_char()
        if self._current_character in self._letters:
            self.__replace_to_code()

    def __replace_to_code(self) -> None:
        """ Matches codes on scanned text. """
        while self._current_character not in self._blank and self._current_character != '\0':
            self.__set_token('CODE')
            self.__get_next_char()

    def __set_token(self, token_type) -> None:
        """ Set current token and token type. """
        self.token_id = token_type
        self.token = self.token + self._current_character
