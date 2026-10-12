from unittest.mock import Mock, patch

import pytest
import requests
from src.external_api import convert_to_rub


class TestConvertToRub:
    """Тесты для convert_to_rub."""

    @patch("src.external_api.os.getenv", return_value="fake_api_key")
    @patch("src.external_api.requests.get")
    def test_convert_usd_success(self, mock_get: Mock, mock_getenv: Mock) -> None:
        """Успешная конвертация USD -> RUB."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 9200.5}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = convert_to_rub(100.0, "USD")

        assert result == 9200.5
        mock_get.assert_called_once()
        _, kwargs = mock_get.call_args
        assert kwargs["headers"]["apikey"] == "fake_api_key"
        assert kwargs["params"]["from"] == "USD"
        assert kwargs["params"]["to"] == "RUB"
        assert kwargs["params"]["amount"] == 100.0

    @patch("src.external_api.os.getenv", return_value="fake_api_key")
    @patch("src.external_api.requests.get")
    def test_convert_eur_success(self, mock_get: Mock, mock_getenv: Mock) -> None:
        """Успешная конвертация EUR -> RUB."""
        mock_response = Mock()
        mock_response.json.return_value = {"result": 10500.0}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = convert_to_rub(100.0, "EUR")

        assert result == 10500.0
        _, kwargs = mock_get.call_args
        assert kwargs["params"]["from"] == "EUR"

    @patch("src.external_api.os.getenv", return_value=None)
    @patch("src.external_api.requests.get")
    def test_missing_api_key_returns_zero(
        self, mock_get: Mock, mock_getenv: Mock
    ) -> None:
        """Если ключ не задан — возвращаем 0.0 и НЕ обращаемся к API."""
        result = convert_to_rub(100.0, "USD")

        assert result == 0.0
        mock_get.assert_not_called()

    @patch("src.external_api.os.getenv", return_value="fake_api_key")
    @patch("src.external_api.requests.get")
    def test_network_error_returns_zero(
        self, mock_get: Mock, mock_getenv: Mock
    ) -> None:
        """При сетевой ошибке возвращаем 0.0."""
        mock_get.side_effect = requests.RequestException("network down")

        result = convert_to_rub(100.0, "USD")

        assert result == 0.0

    @patch("src.external_api.os.getenv", return_value="fake_api_key")
    @patch("src.external_api.requests.get")
    def test_http_error_returns_zero(self, mock_get: Mock, mock_getenv: Mock) -> None:
        """При HTTP-ошибке (raise_for_status) возвращаем 0.0."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("401")
        mock_get.return_value = mock_response

        result = convert_to_rub(100.0, "USD")

        assert result == 0.0

    @patch("src.external_api.os.getenv", return_value="fake_api_key")
    @patch("src.external_api.requests.get")
    def test_missing_result_key_returns_zero(
        self, mock_get: Mock, mock_getenv: Mock
    ) -> None:
        """Если в ответе нет ключа 'result' — возвращаем 0.0."""
        mock_response = Mock()
        mock_response.json.return_value = {"success": False}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = convert_to_rub(100.0, "USD")

        assert result == 0.0

    @patch("src.external_api.os.getenv", return_value="fake_api_key")
    @patch("src.external_api.requests.get")
    def test_non_numeric_result_returns_zero(
        self, mock_get: Mock, mock_getenv: Mock
    ) -> None:
        """Если result не приводится к float — возвращаем 0.0."""
        mock_response = Mock()
        mock_response.json.return_value = {"result": "not-a-number"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = convert_to_rub(100.0, "USD")

        assert result == 0.0
