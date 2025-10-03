import os
import socket
import click

# допустимые команды
ex_com = ["exit", "ls", "cd", "quit", "out_var", "run_script"]

def get_prompt(cwd: str, vfs:str) -> str:
    """Формируем приглашение как в bash: username@hostname:~/...$"""
    user = os.getenv("USER") or os.getenv("USERNAME") or "user"
    host = socket.gethostname()
    vfs1 = vfs[::]
    cwd1 = cwd.replace(vfs, "~", 1)
    return f"{user}@{host}:{cwd1}$"

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
    ctx.ensure_object(dict)
    ctx.obj["vfs"] = os.path.abspath(vfs)
    ctx.obj["cwd"] = ctx.obj["vfs"]   # начинаем в корне VFS
    ctx.obj["script"] = script

    click.echo(f"[DEBUG] VFS path: {ctx.obj['vfs']}")
    click.echo(f"[DEBUG] Script path: {script}")

    if script:
        run_script(script, ctx)

@cli.command()
@click.pass_context
def repl(ctx):
    """Запуск интерактивного режима (REPL)"""
    while True:
        try:
            spl = (click.prompt(get_prompt(ctx.obj["cwd"], ctx.obj["vfs"]), prompt_suffix="", type=str)).split(" ")
            command = spl[0]
            argument = spl[1:]
            if command in ex_com:
                if command in ("exit", "quit"):
                    click.echo("Выход...")
                    break
                elif command == "ls":
                    ls_command(ctx)
                elif command == "cd":
                    cd_command(ctx, argument)
                elif command == "out_var":
                    out_var(argument)
                elif command == "run_script":
                    run_script(argument[0], ctx)
                else:
                    click.echo(f"Выполнено: {command}")
            else:
                raise ValueError(f"Неизвестная команда: {command}")

        except (EOFError, KeyboardInterrupt):
            click.echo("\nВыход...")
            break
        except Exception as e:
            click.echo(f"[ERROR] {e}")

def ls_command(ctx):
    """Список файлов внутри текущей директории VFS"""
    path = ctx.obj["cwd"]
    try:
        files = os.listdir(path)
        click.echo("\n".join(files) if files else "[пусто]")
    except Exception as e:
        click.echo(f"[ERROR] ls: {e}")

def cd_command(ctx, args):
    """Смена директории внутри VFS"""
    if not args:
        ctx.obj["cwd"] = ctx.obj["vfs"]
        return
    new_path = os.path.join(ctx.obj["cwd"], args[0])
    if os.path.isdir(new_path):
        # Проверяем, что остаёмся внутри VFS
        abs_new = os.path.abspath(new_path)
        if abs_new.startswith(ctx.obj["vfs"]):
            ctx.obj["cwd"] = abs_new
        else:
            click.echo("[ERROR] Нельзя выйти за пределы VFS")
    else:
        click.echo(f"[ERROR] Нет такой директории: {args[0]}")

def out_var(text):
    """Раскрытие переменных окружения"""
    input_str = " ".join(text)
    expanded = os.path.expandvars(input_str)
    click.echo(expanded)

def run_script(path: str, ctx):
    """Выполнение скрипта построчно"""
    if os.path.isfile(path):
        click.echo(f"Выполняем скрипт: {path}")
    else:
        new_path = os.path.join(ctx.obj["cwd"], path)
        if os.path.isfile(new_path):
            path = new_path.replace(ctx.obj["vfs"], "~", 1)
            click.echo(f"Выполняем скрипт: {path}")
            path = new_path
        else:
            click.echo("Не существует скрипта по заданному пути")
            return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            click.echo(f"$ {line}")
            try:
                spl = line.split()
                if not spl:
                    continue
                command, *argument = spl
                if command in ex_com:
                    if command in ("exit", "quit"):
                        click.echo("Выход...")
                        break
                    elif command == "ls":
                        ls_command(ctx)
                    elif command == "cd":
                        cd_command(ctx, argument)
                    elif command == "out_var":
                        out_var(argument)
                    elif command == "run_script":
                        run_script(argument[0], ctx)
                    else:
                        click.echo(f"Выполнено: {command}")
                else:
                    raise ValueError(f"Неизвестная команда: {command}")
            except Exception as e:
                click.echo(f"[ERROR] {e}")
                click.echo("[INFO] Скрипт остановлен из-за ошибки")
                break

if __name__ == "__main__":
    cli(obj={})

#Пример запуска
#python main.py --vfs myvfs --script myvfs/scripts/test1.emu repl