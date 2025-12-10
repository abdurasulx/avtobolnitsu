import secrets
import string
import re
from typing import Tuple

def _clean_pool(s: str) -> list:
    if not s:
        return []
    return list(s)

def to_latin(text: str) -> str:
 
    translit = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'x', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'X', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }

    return ''.join(translit.get(ch, ch) for ch in text)

def make_login(s: str, length_min: int = 6, length_max: int = 12) -> str:

    if not isinstance(s, str):
        raise TypeError("s must be a str")
    pool = _clean_pool(s)
    if not pool:
    
        pool = list(string.ascii_lowercase + string.digits)

    length = secrets.choice(range(length_min, length_max + 1))

  
    while len(pool) < length:
        pool += pool

  
    chars = [secrets.choice(pool) for _ in range(length)]
    username = ''.join(ch if not ch.isspace() else '_' for ch in chars)

    if not username[0].isalpha():
        letters = [c for c in pool if c.isalpha()]
        if letters:
            username = secrets.choice(letters) + username[1:]
        else:
            username = 'u' + username[1:] 

    return re.sub(r'[^A-Za-z0-9_.-]', '_', username).lower()


def make_password(s: str, length_min: int = 8, length_max: int = 10) -> str:
   
    if not isinstance(s, str):
        raise TypeError("s must be a str")
    pool = _clean_pool(s)
    if not pool:
        pool = list(string.ascii_letters + string.digits + "!@#$%^&*()")

    length = secrets.choice(range(length_min, length_max + 1))

    while len(pool) < length:
        pool += pool

    chosen = [secrets.choice(pool) for _ in range(length)]

    has_lower = any(c.islower() for c in chosen)
    has_upper = any(c.isupper() for c in chosen)
    has_digit = any(c.isdigit() for c in chosen)
    has_symbol = any((not c.isalnum()) for c in chosen)

    if not has_lower:
        from_s = [c for c in pool if c.islower()]
        if from_s:
            chosen[secrets.randbelow(len(chosen))] = secrets.choice(from_s)
        else:
            chosen[secrets.randbelow(len(chosen))] = secrets.choice(string.ascii_lowercase)

    if not has_upper:
        from_s = [c for c in pool if c.isupper()]
        if from_s:
            chosen[secrets.randbelow(len(chosen))] = secrets.choice(from_s)
        else:
            idx = secrets.randbelow(len(chosen))
            chosen[idx] = chosen[idx].upper() if chosen[idx].isalpha() else secrets.choice(string.ascii_uppercase)

    if not has_digit:
        from_s = [c for c in pool if c.isdigit()]
        if from_s:
            chosen[secrets.randbelow(len(chosen))] = secrets.choice(from_s)
        else:
            chosen[secrets.randbelow(len(chosen))] = secrets.choice(string.digits)

    if not has_symbol:
        from_s = [c for c in pool if not c.isalnum()]
        if from_s:
            chosen[secrets.randbelow(len(chosen))] = secrets.choice(from_s)
        else:
            chosen[secrets.randbelow(len(chosen))] = secrets.choice("!@#$%&*?-_")

   
    secrets.SystemRandom().shuffle(chosen)
    password = ''.join(chosen)
    return password




