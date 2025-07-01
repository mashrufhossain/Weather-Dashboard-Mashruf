def wrap_text(text, width=60):
    import textwrap
    return "\n".join(textwrap.wrap(text, width))
