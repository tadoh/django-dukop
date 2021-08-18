from dukop.apps.calendar.templatetags.calendar_tags import url_alias


def test_url_alias():
    assert url_alias("https://hej.com/test") == "hej.com"
    assert url_alias("https://hej.com") == "hej.com"
    assert url_alias("http://hej.com") == "hej.com"
    assert url_alias("http://hej.com/lala/lala/?91892") == "hej.com"
