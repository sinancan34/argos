import pytest

from app.exceptions import AppException, ErrorBody, ErrorDetail, ErrorEnvelope


@pytest.mark.unit
class TestErrorModels:
    def test_error_detail(self):
        detail = ErrorDetail(loc=["body", "name"], message="required", type="missing")
        assert detail.loc == ["body", "name"]
        assert detail.message == "required"

    def test_error_body_defaults(self):
        body = ErrorBody(code="NOT_FOUND", message="Not found")
        assert body.details == []

    def test_error_envelope(self):
        envelope = ErrorEnvelope(
            error=ErrorBody(code="NOT_FOUND", message="Not found")
        )
        data = envelope.model_dump()
        assert data["error"]["code"] == "NOT_FOUND"
        assert data["error"]["details"] == []


@pytest.mark.unit
class TestAppException:
    def test_basic_exception(self):
        exc = AppException(status_code=404, code="NOT_FOUND", message="Not found")
        assert exc.status_code == 404
        assert exc.code == "NOT_FOUND"
        assert exc.message == "Not found"
        assert exc.details == []

    def test_exception_with_details(self):
        details = [ErrorDetail(loc=["body", "name"], message="required", type="missing")]
        exc = AppException(
            status_code=422,
            code="VALIDATION_ERROR",
            message="Validation failed",
            details=details,
        )
        assert len(exc.details) == 1
        assert exc.details[0].loc == ["body", "name"]

    def test_exception_is_exception(self):
        exc = AppException(status_code=500, code="ERROR", message="fail")
        assert isinstance(exc, Exception)
        assert str(exc) == "fail"
