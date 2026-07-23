"""Shared helpers for list endpoints (LIKE escaping + pagination links)."""

from fastapi import Request

from app.schemas import PaginationLinks

LIKE_ESCAPE_CHAR = "\\"


def escape_like(value: str) -> str:
    """Escape SQL LIKE wildcard characters so they are matched literally."""
    return (
        value.replace(LIKE_ESCAPE_CHAR, LIKE_ESCAPE_CHAR * 2)
        .replace("%", f"{LIKE_ESCAPE_CHAR}%")
        .replace("_", f"{LIKE_ESCAPE_CHAR}_")
    )


def build_pagination_links(
    request: Request, page: int, size: int, total_pages: int
) -> PaginationLinks:
    """Build self/first/last/next/prev links preserving current query params."""
    base = str(request.url).split("?")[0]
    # Preserve non-pagination query params
    extra = {
        k: v
        for k, v in request.query_params.items()
        if k not in ("page", "size")
    }

    def _url(p: int) -> str:
        params = {**extra, "page": str(p), "size": str(size)}
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base}?{qs}"

    last_page = max(total_pages, 1)
    return PaginationLinks(
        self=_url(page),
        first=_url(1),
        last=_url(last_page),
        next=_url(page + 1) if page < last_page else None,
        prev=_url(page - 1) if page > 1 else None,
    )
