import secrets
import string
import re
from typing import Tuple

def _clean_pool(s: str) -> list:
    """s dan tafsiliy belgi havzasi: bo'shliqlarni underscore ga aylantirmasdan saqlaydi."""
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
    """
    s(matn) asosida tasodifiy login yaratadi.
    - Login uzunligi length_min..length_max orasida bo'ladi.
    - Agar s juda qisqa bo'lsa, s takrorlanib ishlatiladi.
    - Login har doim harf bilan boshlashga harakat qilinadi (agar s bu imkoniyatni bermasa, 'u' qo'shiladi).
    """
    if not isinstance(s, str):
        raise TypeError("s must be a str")
    pool = _clean_pool(s)
    if not pool:
        # agar s bo'sh bo'lsa — defaultga tushamiz
        pool = list(string.ascii_lowercase + string.digits)

    length = secrets.choice(range(length_min, length_max + 1))

    # poolni yetarli qilish uchun kerak bo'lsa takrorlaymiz
    while len(pool) < length:
        pool += pool

    # tanlash
    chars = [secrets.choice(pool) for _ in range(length)]
    # bo'shliqlarni '_' ga almashtiramiz va boshqa noqulay belgilarni olib tashlash:
    username = ''.join(ch if not ch.isspace() else '_' for ch in chars)

    # login birinchi belgi harf bo'lishi kerak — buni ta'minlaymiz
    if not username[0].isalpha():
        # s ichidan harf topishga harakat qilamiz
        letters = [c for c in pool if c.isalpha()]
        if letters:
            username = secrets.choice(letters) + username[1:]
        else:
            username = 'u' + username[1:]  # fallback

    # loginni lowercase qilamiz, odatda username kichik harflarga olinadi
    return re.sub(r'[^A-Za-z0-9_.-]', '_', username).lower()


def make_password(s: str, length_min: int = 8, length_max: int = 10) -> str:
    """
    s(matn) asosida tasodifiy parol yaratadi.
    - Parol uzunligi length_min..length_max orasida bo'ladi.
    - Parol asosan s dan olinadi; agar s ichida raqam yoki simvol mavjud bo'lmasa,
      xavfsizlik uchun kichik sonli raqam/simvol qo'shadi.
    - Natija katta-kichik harf, raqam va simvol kombinatsiyasini ta'minlashga harakat qiladi.
    """
    if not isinstance(s, str):
        raise TypeError("s must be a str")
    pool = _clean_pool(s)
    # default pool agar s juda bo'sh bo'lsa
    if not pool:
        pool = list(string.ascii_letters + string.digits + "!@#$%^&*()")

    length = secrets.choice(range(length_min, length_max + 1))

    # Takrorlash orqali yetarlicha element hosil qilamiz
    while len(pool) < length:
        pool += pool

    # Boshlang'ich tanlov - asosan s dan
    chosen = [secrets.choice(pool) for _ in range(length)]

    # Kategoriya tekshiruvlari
    has_lower = any(c.islower() for c in chosen)
    has_upper = any(c.isupper() for c in chosen)
    has_digit = any(c.isdigit() for c in chosen)
    has_symbol = any((not c.isalnum()) for c in chosen)

    # Agar biror tur yetishmasa, s ichidan izlaymiz; topilmasa umumiy belgidan olamiz
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
            # mavjud kichik harfni katta qilish orqali ham ishlatamiz (shu bilan ham "s" ishlatilgan hisoblanadi)
            idx = secrets.randbelow(len(chosen))
            chosen[idx] = chosen[idx].upper() if chosen[idx].isalpha() else secrets.choice(string.ascii_uppercase)

    if not has_digit:
        from_s = [c for c in pool if c.isdigit()]
        if from_s:
            chosen[secrets.randbelow(len(chosen))] = secrets.choice(from_s)
        else:
            # agar s ichida raqam yo'q bo'lsa, 1 ta raqam qo'shamiz (xavfsizlik uchun)
            chosen[secrets.randbelow(len(chosen))] = secrets.choice(string.digits)

    if not has_symbol:
        from_s = [c for c in pool if not c.isalnum()]
        if from_s:
            chosen[secrets.randbelow(len(chosen))] = secrets.choice(from_s)
        else:
            # s ichida symbol yo'q bo'lsa, bitta umumiy symbol qo'shamiz
            chosen[secrets.randbelow(len(chosen))] = secrets.choice("!@#$%&*?-_")

   
    secrets.SystemRandom().shuffle(chosen)
    password = ''.join(chosen)
    return password




