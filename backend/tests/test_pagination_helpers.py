"""Unit tests for app/routers/_common.py — LIKE escaping and pagination links."""

import pytest

from app.routers._common import (
    LIKE_ESCAPE_CHAR,
    build_pagination_links,
    escape_like,
)
from tests.conftest import make_request

TURKISH = "Ürün Ğğ İıŞş"


@pytest.mark.unit
class TestEscapeLike:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("", ""),
            ("plain", "plain"),
            ("100%", "100\\%"),
            ("%leading", "\\%leading"),
            ("snake_case", "snake\\_case"),
            ("_", "\\_"),
            ("%", "\\%"),
            ("\\", "\\\\"),
            ("back\\slash", "back\\\\slash"),
            ("%_", "\\%\\_"),
            ("50%_off", "50\\%\\_off"),
            # Backslash is escaped first, so a literal "\%" becomes "\\\%".
            ("\\%", "\\\\\\%"),
            ("%_\\", "\\%\\_\\\\"),
            (TURKISH, TURKISH),
            ("emoji 📱 %", "emoji 📱 \\%"),
            ("   ", "   "),
            ("\t\n", "\t\n"),
        ],
    )
    def test_escapes_wildcards_only(self, value: str, expected: str) -> None:
        # Act
        result = escape_like(value)

        # Assert
        assert result == expected

    def test_escape_character_is_a_single_backslash(self) -> None:
        # Assert — the routers pass this to ilike(escape=...)
        assert LIKE_ESCAPE_CHAR == "\\"
        assert len(LIKE_ESCAPE_CHAR) == 1

    def test_leaves_the_input_untouched(self) -> None:
        # Arrange
        value = "100%_off"

        # Act
        escape_like(value)

        # Assert — strings are immutable, but guard against a future rewrite
        assert value == "100%_off"

    def test_handles_a_very_long_string(self) -> None:
        # Arrange
        value = "%" * 10_000

        # Act
        result = escape_like(value)

        # Assert
        assert result == "\\%" * 10_000
        assert len(result) == 20_000

    def test_is_not_idempotent(self) -> None:
        # Assert — escaping twice double-escapes; callers must escape once
        assert escape_like(escape_like("100%")) == "100\\\\\\%"


@pytest.mark.unit
class TestBuildPaginationLinks:
    def test_first_page_of_many(self) -> None:
        # Arrange
        request = make_request("http://testserver/api/v1/devices?page=1&size=2")

        # Act
        links = build_pagination_links(request, page=1, size=2, total_pages=3)

        # Assert
        assert links.self == "http://testserver/api/v1/devices?page=1&size=2"
        assert links.first == "http://testserver/api/v1/devices?page=1&size=2"
        assert links.last == "http://testserver/api/v1/devices?page=3&size=2"
        assert links.next == "http://testserver/api/v1/devices?page=2&size=2"
        assert links.prev is None

    def test_middle_page_has_both_neighbours(self) -> None:
        # Arrange
        request = make_request("http://testserver/api/v1/devices?page=2&size=2")

        # Act
        links = build_pagination_links(request, page=2, size=2, total_pages=3)

        # Assert
        assert links.next == "http://testserver/api/v1/devices?page=3&size=2"
        assert links.prev == "http://testserver/api/v1/devices?page=1&size=2"

    def test_last_page_has_no_next(self) -> None:
        # Arrange
        request = make_request("http://testserver/api/v1/devices?page=3&size=2")

        # Act
        links = build_pagination_links(request, page=3, size=2, total_pages=3)

        # Assert
        assert links.next is None
        assert links.prev == "http://testserver/api/v1/devices?page=2&size=2"

    def test_single_page(self) -> None:
        # Arrange
        request = make_request("http://testserver/api/v1/devices")

        # Act
        links = build_pagination_links(request, page=1, size=20, total_pages=1)

        # Assert
        assert links.next is None
        assert links.prev is None
        assert links.self == links.first == links.last

    def test_empty_result_set_clamps_last_page_to_one(self) -> None:
        # Arrange
        request = make_request("http://testserver/api/v1/devices")

        # Act — total_pages is 0 when nothing matched
        links = build_pagination_links(request, page=1, size=20, total_pages=0)

        # Assert
        assert links.last == "http://testserver/api/v1/devices?page=1&size=20"
        assert links.next is None

    def test_page_beyond_the_last_page(self) -> None:
        # Arrange
        request = make_request("http://testserver/api/v1/devices?page=999")

        # Act
        links = build_pagination_links(request, page=999, size=20, total_pages=2)

        # Assert
        assert links.self.endswith("page=999&size=20")
        assert links.next is None
        assert links.prev == "http://testserver/api/v1/devices?page=998&size=20"

    def test_preserves_filter_and_sort_params(self) -> None:
        # Arrange
        request = make_request(
            "http://testserver/api/v1/devices"
            "?name=Alpha&status=true&sort_by=name&sort_order=asc&page=2&size=5"
        )

        # Act
        links = build_pagination_links(request, page=2, size=5, total_pages=4)

        # Assert — page/size are replaced, everything else survives
        for link in (links.self, links.first, links.last, links.next, links.prev):
            assert "name=Alpha" in link
            assert "status=true" in link
            assert "sort_by=name" in link
            assert "sort_order=asc" in link
            assert link.count("page=") == 1
            assert link.count("size=") == 1

    def test_drops_the_incoming_page_and_size(self) -> None:
        # Arrange
        request = make_request("http://testserver/api/v1/devices?page=7&size=3")

        # Act
        links = build_pagination_links(request, page=1, size=20, total_pages=1)

        # Assert
        assert "page=7" not in links.self
        assert "size=3" not in links.self
        assert links.self.endswith("page=1&size=20")

    def test_query_string_is_dropped_from_the_base_url(self) -> None:
        # Arrange
        request = make_request("http://testserver/api/v1/scenarios?name=x")

        # Act
        links = build_pagination_links(request, page=1, size=20, total_pages=1)

        # Assert
        assert links.self.startswith("http://testserver/api/v1/scenarios?")
        assert links.self.count("?") == 1

    @pytest.mark.parametrize("size", [1, 20, 100])
    def test_size_is_echoed_verbatim(self, size: int) -> None:
        # Arrange
        request = make_request("http://testserver/api/v1/devices")

        # Act
        links = build_pagination_links(request, page=1, size=size, total_pages=1)

        # Assert
        assert f"size={size}" in links.self

    def test_reserved_characters_in_filters_are_not_re_encoded(self) -> None:
        # Arrange — "100%" arrives percent-decoded from request.query_params
        request = make_request("http://testserver/api/v1/devices?name=100%25")

        # Act
        links = build_pagination_links(request, page=1, size=20, total_pages=1)

        # KNOWN GAP: links are joined with f-strings, not urlencode(), so the
        # emitted link carries a bare "%" and is not a valid URL to follow.
        assert "name=100%&" in links.self
