def strip_0x(s: str):
    return s[2:] if s and s.startswith("0x") else s
