import os
import socket
import click

# допустимые команды
ex_com = ["exit", "ls", "cd", "quit", "out_var", "run_script"]

def get_prompt() -> str:
    """Формируем приглашение как в bash: username@hostname:~$"""
    user = os.getenv("USER") or os.getenv("USERNAME") or "user"
    host = socket.gethostname()
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd.startswith(home):
        cwd = cwd.replace(home, "", 1)
    return f"{user}@{host}:~{cwd}$"
@click.group()
@click.option("--vfs", type=click.Path(), required=True, help="Путь к виртуальной файловой системе")
@click.option("--script", type=click.Path(exists=True), help="Путь к стартовому скрипту")
@click.pass_context
def cli(ctx, vfs, script):
    """
    Эмулятор с параметрами:
      --vfs    путь к VFS
      --script стартовый скрипт
    """
    # сохраняем параметры в контекст
    ctx.ensure_object(dict)
    ctx.obj["vfs"] = vfs
    ctx.obj["script"] = script

    # отладочный вывод
    click.echo(f"[DEBUG] VFS path: {vfs}")
    click.echo(f"[DEBUG] Script path: {script}")

    # если есть стартовый скрипт — выполняем
    if script:
        run_script(script)

@cli.command()
def repl():
    """Запуск интерактивного режима (REPL)"""
    while True:
        try:
            spl = (click.prompt(get_prompt(), prompt_suffix="", type=str)).split(" ")
            command = spl[0]
            argument = spl[1:]

            if command in ex_com:
                click.echo(f"Выполнено: {command}")
                if command in ("exit", "quit"):
                    click.echo("Выход...")
                    break
                elif command == "out_var":
                    out_var(argument)
                elif command == "run_script":
                    run_script(argument[0])

            else:
                raise ValueError(f"Неизвестная команда: {command}")
        except (EOFError, KeyboardInterrupt):
            click.echo("\nВыход...")
            break

def run_script(path: str):
    """Выполнение стартового скрипта построчно"""
    click.echo(f"Выполняем скрипт: {path}")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):  # пропускаем пустые и комментарии
                continue
            click.echo(f"$ {line}")  # имитация ввода пользователя
            try:
                spl = line.split(" ")
                command = spl[0]
                argument = spl[1:]
                if command in ex_com:
                    if command in ("exit", "quit"):
                        click.echo("Выход...")
                        break
                    elif command == "out_var":
                        out_var(argument)
                    else:
                        click.echo(f"Выполнено: {command}")
                else:
                    raise ValueError(f"Неизвестная команда: {command}")
            except Exception as e:
                click.echo(f"[ERROR] {e}")
                click.echo("[INFO] Скрипт остановлен из-за ошибки")
                break

def out_var(text):
    """Раскрытие переменных окружения"""
    input_str = " ".join(text)
    expanded = os.path.expandvars(input_str)
    click.echo(expanded)

if __name__ == "__main__":
    cli(obj={})



