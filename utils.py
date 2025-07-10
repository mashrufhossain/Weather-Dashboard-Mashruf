def title_case(s):
    return ' '.join([w if w.isupper() else w.capitalize() for w in s.split()])