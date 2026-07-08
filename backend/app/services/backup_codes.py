import secrets

from app.services.uniqueness import claim_credential

BACKUP_CODE_COUNT = 10
BACKUP_CODE_LENGTH = 10
BACKUP_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
BACKUP_PREFIXES = (
    "SV",
    "KH",
    "BK",
    "HL",
    "OK",
    "MD",
    "SN",
    "BR",
    "PG",
    "HW",
)


def generate_backup_codes(
    count: int = BACKUP_CODE_COUNT,
    length: int = BACKUP_CODE_LENGTH,
) -> list[str]:
    if length < 4:
        raise ValueError("Backup code length too short for themed prefix")

    rng = secrets.SystemRandom()
    codes: list[str] = []
    seen: set[str] = set()
    attempts = 0
    max_attempts = count * 64

    while len(codes) < count and attempts < max_attempts:
        attempts += 1
        prefix = rng.choice(BACKUP_PREFIXES)
        body_len = length - len(prefix)
        code = prefix + "".join(rng.choice(BACKUP_ALPHABET) for _ in range(body_len))
        if code in seen:
            continue
        if not claim_credential(code):
            continue
        seen.add(code)
        codes.append(code)

    if len(codes) < count:
        raise RuntimeError("Could not generate unique backup codes")

    return codes
