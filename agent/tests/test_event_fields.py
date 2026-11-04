import pytest

from argos_agent.runner.event_fields import request_events

pytestmark = pytest.mark.unit

GA4_URL = "https://analytics.google.com/g/collect?v=2&tid=G-1"
# A real GA4 item: two-letter fields, a custom k0/v0 pair, `~` between them.
REAL_ITEM = (
    "id4586649~nmgraphic-design-specialist~ln0~cano~c2score_null~c4is-yerinde"
    "~c5tam-zamanli~k0sort_score_flag~v0no~loistanbul"
)


def test_a_request_without_a_body_is_one_event_from_its_query() -> None:
    assert request_events(f"{GA4_URL}&en=page_view", None) == [{"v": "2", "tid": "G-1", "en": "page_view"}]


def test_each_body_line_is_one_event_merged_with_the_query() -> None:
    events = request_events(GA4_URL, "en=a&x=1\nen=b&x=2\n")

    assert events == [
        {"v": "2", "tid": "G-1", "en": "a", "x": "1"},
        {"v": "2", "tid": "G-1", "en": "b", "x": "2"},
    ]


def test_an_empty_body_is_the_query_alone() -> None:
    assert request_events(GA4_URL, "") == [{"v": "2", "tid": "G-1"}]


def test_a_body_line_value_replaces_the_query_value() -> None:
    event = request_events(f"{GA4_URL}&en=query&dr=a", "en=line")[0]

    assert (event["en"], event["dr"]) == ("line", "a")


def test_a_repeated_key_keeps_its_last_value() -> None:
    assert request_events("https://a.com/?x=1&x=2", None)[0]["x"] == "2"


def test_form_encoding_is_decoded() -> None:
    event = request_events("https://a.com/p", "ep.content_group=ana-sayfa&dl=https%3A%2F%2Fa.com%2F&t=a+b")[0]

    assert (event["ep.content_group"], event["dl"], event["t"]) == ("ana-sayfa", "https://a.com/", "a b")


def test_an_item_is_split_on_tilde_into_dot_fields_and_the_raw_key_is_dropped() -> None:
    event = request_events(f"{GA4_URL}&en=view_item_list", f"pr1={REAL_ITEM}&pr2=id7~lp2")[0]

    assert event == {
        "v": "2",
        "tid": "G-1",
        "en": "view_item_list",
        "pr1.id": "4586649",
        "pr1.nm": "graphic-design-specialist",
        "pr1.ln": "0",
        "pr1.ca": "no",
        "pr1.c2": "score_null",
        "pr1.c4": "is-yerinde",
        "pr1.c5": "tam-zamanli",
        "pr1.lo": "istanbul",
        "pr1.sort_score_flag": "no",
        "pr2.id": "7",
        "pr2.lp": "2",
    }


def test_a_field_with_an_empty_value_is_kept() -> None:
    assert request_events("https://a.com/?pr1=id1~va", None)[0] == {"pr1.id": "1", "pr1.va": ""}


def test_a_custom_name_without_its_value_is_dropped() -> None:
    assert request_events("https://a.com/?pr1=id1~k0flag~k1x~v1y", None)[0] == {"pr1.id": "1", "pr1.x": "y"}


def test_keys_that_only_look_like_items_are_left_alone() -> None:
    event = request_events("https://a.com/?pr=a~b&prx1=c~d&id=GTM-1", None)[0]

    assert event == {"pr": "a~b", "prx1": "c~d", "id": "GTM-1"}
