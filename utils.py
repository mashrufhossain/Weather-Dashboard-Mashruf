def title_case(s):

    '''
    Convert a string to title case, preserving all-uppercase words.

    Splits the input on whitespace, then for each word:
      - If it’s already all uppercase (e.g. an acronym like “NASA”), leave it unchanged.
      - Otherwise capitalize it (first letter uppercase, rest lowercase).
    Finally rejoins the words with single spaces.
    '''

    return ' '.join([w if w.isupper() else w.capitalize() for w in s.split()])