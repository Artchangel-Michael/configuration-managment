import os
import socket
import click

import os
import socket
import click

ex_com = ["exit", "ls", "cd", "quit", "out_var"]

def get_prompt() -> str:
    """Формируем приглашение как в bash: username@hostname:~$"""
    user = os.getenv("USER") or os.getenv("USERNAME") or "user"
    host = socket.gethostname()
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    # заменяем домашний каталог на ~
    if cwd.startswith(home):
        cwd = cwd.replace(home, "~", 1)
    return f"{user}@{host}:{cwd}$ "


@click.command()
def cli():
    """Пример CLI с кастомным приглашением"""
    while True:
        try:
            spl = (click.prompt(get_prompt(), prompt_suffix="", type=str)).split(" ")
            command = spl[0]
            argument = []

            for i in range(1, len(spl)):
                argument.append(spl[i])
            if command in ex_com:
                if command in ("exit", "quit"):
                    click.echo("Выход...")
                    break
                else:
                    click.echo(f"Выполнено: {command}")
                    if command == "out_var":
                        out_var(argument)
            else:
                click.echo(f"Неизвестная команда: {command}")
                break
        except (EOFError, KeyboardInterrupt):
            click.echo("\nВыход...")
            break


@click.command()
@click.argument("text", nargs=-1)

def out_var(text):
    input_str = " ".join(text)
    expanded = os.path.expandvars(input_str)
    click.echo(expanded)

if __name__ == "__main__":
    cli()


