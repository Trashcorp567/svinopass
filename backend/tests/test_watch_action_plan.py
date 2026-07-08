from app.services.watch_action_plan import format_action_plan_text


def test_action_plan_with_breaches_includes_steps():
    text = format_action_plan_text(breach_count=3)
    assert "Смените пароль" in text
    assert "/check" in text
    assert "/#pricing" in text or "svinopass.ru" in text
    assert "/watch" in text
    assert "удалить данные" in text.lower()


def test_action_plan_clean_email():
    text = format_action_plan_text(breach_count=0)
    assert "утечек не найдено" in text.lower()
    assert "/check" in text
    assert "/watch" in text


def test_action_plan_can_hide_watch_cta():
    text = format_action_plan_text(breach_count=2, include_watch_cta=False)
    assert "/watch" not in text
    assert "/check" in text
