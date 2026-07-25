"""Tests for app/database.py — the request-scoped session dependency."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.database import Base, get_db


@pytest.mark.unit
class TestGetDb:
    def test_yields_a_session_from_the_factory(self, session_factory) -> None:
        # Arrange
        with patch("app.database.SessionLocal", session_factory):
            generator = get_db()

            # Act
            session = next(generator)

            # Assert
            assert isinstance(session, Session)
            generator.close()

    def test_closes_the_session_on_normal_exit(self) -> None:
        # Arrange
        mock_session = MagicMock()
        with patch("app.database.SessionLocal", return_value=mock_session) as factory:
            generator = get_db()
            yielded = next(generator)

            # Assert — still open while the request is being served
            assert yielded is mock_session
            mock_session.close.assert_not_called()

            # Act — exhausting the generator runs the finally block
            with pytest.raises(StopIteration):
                next(generator)

            # Assert
            factory.assert_called_once_with()
            mock_session.close.assert_called_once_with()

    def test_closes_the_session_when_the_caller_raises(self) -> None:
        # Arrange
        mock_session = MagicMock()
        with patch("app.database.SessionLocal", return_value=mock_session):
            generator = get_db()
            next(generator)

            # Act / Assert — the error propagates, the session still closes
            with pytest.raises(RuntimeError, match=r"handler blew up"):
                generator.throw(RuntimeError("handler blew up"))
            mock_session.close.assert_called_once_with()

    def test_closes_the_session_when_the_generator_is_abandoned(self) -> None:
        # Arrange
        mock_session = MagicMock()
        with patch("app.database.SessionLocal", return_value=mock_session):
            generator = get_db()
            next(generator)

            # Act — GeneratorExit path, as when a request is cancelled
            generator.close()

            # Assert
            mock_session.close.assert_called_once_with()

    def test_each_call_opens_a_fresh_session(self) -> None:
        # Arrange
        with patch("app.database.SessionLocal") as factory:
            factory.side_effect = [MagicMock(), MagicMock()]

            # Act
            first = next(get_db())
            second = next(get_db())

            # Assert
            assert first is not second
            assert factory.call_count == 2


@pytest.mark.unit
class TestBase:
    def test_models_are_registered_on_the_shared_metadata(self) -> None:
        # Assert — alembic autogenerate depends on this registry
        assert set(Base.metadata.tables) == {"devices", "scenarios"}

    def test_scenarios_table_declares_the_device_foreign_key(self) -> None:
        # Arrange
        scenarios = Base.metadata.tables["scenarios"]

        # Act
        foreign_keys = list(scenarios.c.device_id.foreign_keys)

        # Assert
        assert len(foreign_keys) == 1
        assert foreign_keys[0].target_fullname == "devices.id"
