import pytest
from src.decorators import log


def test_log_to_console_success(capsys):
    """Успешное выполнение функции логируется в консоль."""

    @log()
    def add(x, y):
        return x + y

    add(1, 2)

    captured = capsys.readouterr()
    assert captured.out == "add ok\n"
    assert captured.err == ""


def test_log_to_console_error(capsys):
    """Ошибка при выполнении функции логируется в консоль."""

    @log()
    def divide(x, y):
        return x / y

    with pytest.raises(ZeroDivisionError):
        divide(1, 0)

    captured = capsys.readouterr()
    assert captured.out == "divide error: ZeroDivisionError. Inputs: (1, 0), {}\n"


def test_log_to_console_error_with_kwargs(capsys):
    """Ошибка логируется с учётом именованных аргументов."""

    @log()
    def divide(x, y):
        return x / y

    with pytest.raises(ZeroDivisionError):
        divide(x=5, y=0)

    captured = capsys.readouterr()
    assert (
        captured.out
        == "divide error: ZeroDivisionError. Inputs: (), {'x': 5, 'y': 0}\n"
    )

    def test_log_to_file_success(tmp_path):
        """Успешное выполнение функции логируется в файл."""
        log_file = tmp_path / "mylog.txt"

        @log(filename=str(log_file))
        def my_function(x, y):
            return x + y

        my_function(1, 2)

        assert log_file.read_text(encoding="utf-8") == "my_function ok\n"

    def test_log_to_file_error(tmp_path):
        """Ошибка логируется в файл."""
        log_file = tmp_path / "mylog.txt"

        @log(filename=str(log_file))
        def divide(x, y):
            return x / y

        with pytest.raises(ZeroDivisionError):
            divide(1, 0)

        content = log_file.read_text(encoding="utf-8")
        assert content == "divide error: ZeroDivisionError. Inputs: (1, 0), {}\n"

    def test_log_to_file_appends(tmp_path):
        """Логи дописываются, а не перезаписывают файл."""
        log_file = tmp_path / "mylog.txt"

        @log(filename=str(log_file))
        def my_function(x, y):
            return x + y

        my_function(1, 2)
        my_function(3, 4)

        content = log_file.read_text(encoding="utf-8")
        assert content == "my_function ok\nmy_function ok\n"

    def test_log_to_file_no_console_output(tmp_path, capsys):
        """При указании filename в консоль ничего не выводится."""
        log_file = tmp_path / "mylog.txt"

        @log(filename=str(log_file))
        def my_function(x, y):
            return x + y

        my_function(1, 2)

        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""
