from app.services.backup_codes import BACKUP_CODE_COUNT, BACKUP_CODE_LENGTH, generate_backup_codes


def test_generate_backup_codes_count_and_length():
    codes = generate_backup_codes()
    assert len(codes) == BACKUP_CODE_COUNT
    assert all(len(code) == BACKUP_CODE_LENGTH for code in codes)
    assert len(set(codes)) == BACKUP_CODE_COUNT


def test_generate_backup_codes_alphabet():
    codes = generate_backup_codes(count=5, length=10)
    allowed = set("23456789ABCDEFGHJKLMNPQRSTUVWXYZ")
    for code in codes:
        assert code[:2] in {"SV", "KH", "BK", "HL", "OK", "MD", "SN", "BR", "PG", "HW"}
        assert all(c in allowed for c in code[2:])
