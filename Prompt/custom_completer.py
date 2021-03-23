'''
Original: https://github.com/prompt-toolkit/python-prompt-toolkit

Many thanks to the contributors!
'''

from typing import Callable, Iterable, List, Mapping, Optional, Pattern, Union, Any, Dict, Set

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import AnyFormattedText

__all__ = [
    "ImpvWordCompleter",
]

class ImpvWordCompleter(Completer):
    """
    Simple autocompletion on a list of words.

    :param words: List of words or callable that returns a list of words.
    :param ignore_case: If True, case-insensitive completion.
    :param meta_dict: Optional dict mapping words to their meta-text. (This
        should map strings to strings or formatted text.)
    :param WORD: When True, use WORD characters.
    :param sentence: When True, don't complete by comparing the word before the
        cursor, but by comparing all the text before the cursor. In this case,
        the list of words is just a list of strings, where each string can
        contain spaces. (Can not be used together with the WORD option.)
    :param match_middle: When True, match not only the start, but also in the
                        middle of the word.
    :param pattern: Optional compiled regex for finding the word before
        the cursor to complete. When given, use this regex pattern instead of
        default one (see document._FIND_WORD_RE)
    """

    def __init__(
        self,
        words: Union[List[str], Callable[[], List[str]]],
        ignore_case: bool = False,
        display_dict: Optional[Mapping[str, AnyFormattedText]] = None,
        meta_dict: Optional[Mapping[str, AnyFormattedText]] = None,
        WORD: bool = False,
        sentence: bool = False,
        match_middle: bool = False,
        pattern: Optional[Pattern[str]] = None,
    ) -> None:

        assert not (WORD and sentence)

        self.words = words
        self.ignore_case = ignore_case
        self.display_dict = display_dict or {}
        self.meta_dict = meta_dict or {}
        self.WORD = WORD
        self.sentence = sentence
        self.match_middle = match_middle
        self.pattern = pattern

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        # Get list of words.
        words = self.words
        if callable(words):
            words = words()

        # Get word/text before cursor.
        if self.sentence:
            word_before_cursor = document.get_word_before_cursor(
                WORD=self.WORD, pattern=self.pattern
            )
        else:
            word_before_cursor = document.text_before_cursor

        # word_before_cursor = document.text_before_cursor

        if self.ignore_case:
            word_before_cursor = word_before_cursor.lower()

        def word_matches(word: str) -> bool:
            """ True when the word before the cursor matches. """
            if self.ignore_case:
                word = word.lower()

            if self.match_middle:
                return word_before_cursor in word
            else:
                return word.startswith(word_before_cursor)

        for a in words:
            if word_matches(a):
                display = self.display_dict.get(a, a)
                display_meta = self.meta_dict.get(a, "")
                yield Completion(
                    a,
                    -len(word_before_cursor),
                    display=display,
                    display_meta=display_meta,
                )

# NestedDict = Mapping[str, Union['NestedDict', Set[str], None, Completer]]
NestedDict = Mapping[str, Union[Any, Set[str], None, Completer]]

"""
Nestedcompleter for completion of hierarchical data structures.
"""

class MyNestedCompleter(Completer):
    """
    Completer which wraps around several other completers, and calls any the
    one that corresponds with the first word of the input.

    By combining multiple `NestedCompleter` instances, we can achieve multiple
    hierarchical levels of autocompletion. This is useful when `WordCompleter`
    is not sufficient.

    If you need multiple levels, check out the `from_nested_dict` classmethod.
    """

    def __init__(
        self, options: Dict[str, Optional[Completer]], ignore_case: bool = True
    ) -> None:

        self.options = options
        self.ignore_case = ignore_case

    def __repr__(self) -> str:
        return "NestedCompleter(%r, ignore_case=%r)" % (self.options, self.ignore_case)

    @classmethod
    def from_nested_dict(cls, data: NestedDict) -> "NestedCompleter":
        """
        Create a `NestedCompleter`, starting from a nested dictionary data
        structure, like this:

        .. code::

            data = {
                'show': {
                    'version': None,
                    'interfaces': None,
                    'clock': None,
                    'ip': {'interface': {'brief'}}
                },
                'exit': None
                'enable': None
            }

        The value should be `None` if there is no further completion at some
        point. If all values in the dictionary are None, it is also possible to
        use a set instead.

        Values in this data structure can be a completers as well.
        """
        options: Dict[str, Optional[Completer]] = {}
        for key, value in data.items():
            if isinstance(value, Completer):
                options[key] = value
            elif isinstance(value, dict):
                options[key] = cls.from_nested_dict(value)
            elif isinstance(value, set):
                options[key] = cls.from_nested_dict({item: None for item in value})
            else:
                assert value is None
                options[key] = None

        return cls(options)

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        # Split document.
        text = document.text_before_cursor.lstrip()
        stripped_len = len(document.text_before_cursor) - len(text)

        # If there is a space, check for the first term, and use a
        # subcompleter.
        if " " in text:
            first_term = text.split()[0]
            completer = self.options.get(first_term)

            # If we have a sub completer, use this for the completions.
            if completer is not None:
                remaining_text = text[len(first_term) :].lstrip()
                move_cursor = len(text) - len(remaining_text) + stripped_len

                new_document = Document(
                    remaining_text,
                    cursor_position=document.cursor_position - move_cursor,
                )

                for c in completer.get_completions(new_document, complete_event):
                    yield c

        # No space in the input: behave exactly like `WordCompleter`.
        else:
            completer = ImpvWordCompleter(
                list(self.options.keys()), ignore_case=self.ignore_case, match_middle=False, pattern=False, WORD=False
            )
            for c in completer.get_completions(document, complete_event):
                yield c
    
    pass