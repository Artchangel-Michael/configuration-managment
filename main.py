import os
import socket
import click
import time
import shutil

# допустимые команды
ex_com = ["exit", "ls", "cd", "quit", "out_var", "run_script", "head", "history", "uptime", "rmdir", "cp"]
start_time = time.time()
history_arr = []

def get_prompt(cwd: str, vfs:str) -> str:
    """Формируем приглашение как в bash: username@hostname:~/...$"""
    user = os.getenv("USER") or os.getenv("USERNAME") or "user"
    host = socket.gethostname()
    vfs1 = vfs[::]
    cwd1 = cwd.replace(vfs, "~", 1)
    return f"{user}@{host}:{cwd1}$"

@click.group()
@click.option("--vfs", type=click.Path(), required=True, help="Путь к виртуальной файловой системе")
@click.option("--script", type=click.Path(), help="Путь к стартовому скрипту")
@click.pass_context
def cli(ctx, vfs, script):
    """ Эмулятор с параметрами:
      --vfs    путь к VFS
      --script стартовый скрипт
    """

    if os.path.isdir(vfs):
        shutil.rmtree(vfs)
    os.mkdir(vfs)
    os.mkdir(vfs + "/scripts")
    os.mkdir(vfs + "/files")
    os.mkdir(vfs + "/proj")
    with open(os.path.join(vfs, "scripts", "test1.emu"), "w", encoding = "utf-8") as file:
        file.write("#Проверка out_var\n")
        file.write("out_var %USERPROFILE%\n")
        file.write("ls\n")
        file.write("cd scripts\n")
        file.write("ls\n")
        file.write("run_script myvfs/scripts/test2.emu\n")
        file.write("quit\n")
    with open(os.path.join(vfs, "scripts", "test2.emu"), "w", encoding = "utf-8") as file:
        file.write("# Проверка ошибки\ncd\nls\n"
                   "run_script myvfs/scripts/test3.emu")
    with open(os.path.join(vfs, "scripts", "test3.emu"), "w", encoding = "utf-8") as file:
        file.write("# Проверка сразу нескольких команд \n"
                   "out_var $PATH\ncd scripts\nrun_script test4.emu\nout_var $TEMP "
                   ""
                   "\nexit")
    with open(os.path.join(vfs, "scripts", "test4.emu"), "w", encoding = "utf-8") as file:
        file.write("uptime\n")
        file.write("head myvfs/files/text1.txt\n")
        file.write("history\n")
        file.write("run_script myvfs/scripts/test5.emu\n")
    with open(os.path.join(vfs, "scripts", "test5.emu"), "w", encoding = "utf-8") as file:
        file.write("cp myvfs/proj myvfs/files/proj\n")
        file.write("rmdir myvfs/proj\n")
        file.write("badcmd\n")
        file.write("exit\n")
    with open(os.path.join(vfs, "files", "text1.txt"), "w", encoding = "utf-8") as file:
        file.write("Я, в своем познании настолько преисполнился,\n"
                   "что как будто бы уже сто триллионов миллиардов лет,\n"
                   "проживаю на триллионах и триллионах таких же планет.\n"
                   "Планет, как эта Земля. Мне этот мир уже во многом понятен,\n"
                   "и ищу я здесь только одного - покоя, умиротворения,\n"
                   "и вот этой гармонии, от слияния с бесконечно-вечным,\n"
                   "от созерцания этого великого фрактального подобия,\n"
                   "и от вот этого замечательного всеединства существа,\n"
                   "бесконечно-вечного, куда ни посмотри:\n"
                   "хоть вглубь - в бесконечно малое,\n"
                   "хоть ввысь - в бесконечно большое.\n"
                   "А каков твой выбор? Иди же, суетись дальше...\n\n"
                   "Твое распределение — это твой путь,\n"
                   "и твой горизонт познаний, ощущений,\n"
                   "и ограниченность собственной природы.\n"
                   "И он несоизмеримо мелок по сравнению с моим...\n"
                   "Порой, я ощущаю себя глубоким старцем,\n"
                   "потратившим жизнь, в поисках рецепта бессмертия,\n"
                   "формулы вечной жизни.\n"
                   "Я нахожусь на этой планете, с самого момента её зарождения.\n"
                   "Когда облако прекурсоров, трансформируясь поэтапно,\n"
                   "превращалось в звезду, по имени Солнце.\n"
                   "Я помню ослепляющий взрыв газопылевого субстрата,\n"
                   "лучи Си, разрезающие мрак у врат Тангейзера,\n"
                   "атакующие корабли, пылающие над Орионом...\n\n"
                   "Меня не покидает ощущение, что я живу на этой Земле,\n"
                   "вот уже пять миллиардов лет, и знаю её вдоль и поперек.\n"
                   "Я был на этой планете, несчётное множество раз.\n"
                   "Я был величественнее Цезаря, беспощаднее Гитлера,\n"
                   "безжалостней всех самых свирепых тиранов.\n"
                   "Я был и рабом, и бесправным шудрой, изгоем, отщепенцем,\n"
                   "проживал жизни, в положении намного худшем, чем нынешнее.\n"
                   "Я говорю так, потому что чувствую в себе\n"
                   "эту пеструю мозаику пережитых событий и состояний.\n"
                   "Где-то я был подобен растению, где-то был подобен птице,\n"
                   "где-то - червю, а где-то был просто сгустком камня.")

    ctx.ensure_object(dict)
    ctx.obj["vfs"] = os.path.abspath(vfs)
    ctx.obj["cwd"] = ctx.obj["vfs"]   # начинаем в корне VFS
    ctx.obj["script"] = script

    click.echo(f"[DEBUG] VFS path: {ctx.obj['vfs']}")
    click.echo(f"[DEBUG] Script path: {script}")

    if script:
        # Превращаем относительный путь в абсолютный внутри VFS
        script_path = os.path.abspath(script)
        if os.path.isfile(script_path):
            run_script(script_path, ctx)
        else:
            click.echo(f"Не существует скрипта по пути: {script_path}")


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
                history_arr.insert(0, " ".join(spl))
                if command in ("exit", "quit"):
                    shutil.rmtree("myvfs")
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
                elif command == "head":
                    head(argument, ctx)
                elif command == "history":
                    history_def(argument)
                elif command == "uptime":
                    uptime_command()
                elif command == "rmdir":
                    rmdir_command(ctx, argument)
                elif command == "cp":
                    cp_command(ctx, argument)
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
        else: click.echo(f"Не существует скрипта по пути: {path}")
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
                    elif command == "head":
                        head(argument, ctx)
                    elif command == "history":
                        history_def(argument)
                    elif command == "uptime":
                        uptime_command()
                    elif command == "rmdir":
                        rmdir_command(ctx, argument)
                    elif command == "cp":
                        cp_command(ctx, argument)
                else:
                    click.echo(f"Неизвестная команда: {command}")
                    break
            except():
                click.echo("[INFO] Скрипт остановлен из-за ошибки")
                break

def uptime_command():
    """Вывод времени работы программы"""
    delta = time.time() - start_time
    hours, rem = divmod(int(delta), 3600)
    minutes, seconds = divmod(rem, 60)
    milliseconds = int((delta - int(delta)) * 1000)
    click.echo(f"Uptime: {hours}h {minutes}m {seconds}s {milliseconds}ms")

def rmdir_command(ctx, args):
    """Удаление директории внутри VFS"""
    if not args:
        click.echo("[ERROR] Укажите директорию для удаления")
        return
    path = args[0]
    if os.path.isdir(path):
        abs_path = os.path.abspath(path)
    else:
        new_path = os.path.join(ctx.obj["cwd"], path)
        if os.path.isdir(new_path):
            abs_path = os.path.abspath(new_path)
    if not abs_path.startswith(ctx.obj["vfs"]):
        click.echo("[ERROR] Нельзя выйти за пределы VFS")
        return
    if os.path.isdir(abs_path):
        try:
            os.rmdir(abs_path)  # удаляет только пустые каталоги
            click.echo(f"Директория удалена: {args[0]}")
        except OSError:
            click.echo(f"[ERROR] Директория {args[0]} не пуста")
    else:
        click.echo(f"[ERROR] Нет такой директории: {args[0]}")

def head(argument, ctx):
    """Выполнение скрипта построчно"""
    path = argument[0]
    if len(argument) > 1:
        number = argument[1]
    else:
        number = None
    if os.path.isfile(path):
        click.echo(f"Читаем файл: {path}")
    else:
        new_path = os.path.join(ctx.obj["cwd"], path)
        if os.path.isfile(new_path):
            click.echo(f"Читаем файл: {new_path.replace(ctx.obj['vfs'], '~', 1)}")
            path = new_path
        else:
            click.echo("Не существует файла по заданному пути")
            return

    if number is None:
        numb = 10
    elif number.isdigit():
        numb = int(number)
    else:
        click.echo("Вторым аргументом должно передаваться число")
        return
    i = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if numb == i:
                return
            line = line.strip()
            click.echo(f"{line}")
            i += 1
        if i != numb:
            click.echo(f"В файле меньше {number} строк.\n"
                       f"Считаны все возможные строки файла")

def history_def(args):
    if not args:
        for i in range(len(history_arr)):
            click.echo(f"Операция номер {i}: {history_arr[i]}")
        return
    else:
        for i in range(0, len(args)):
            if not args[i].isdigit():
                click.echo(f"Недопустимый аргумент: {args}")
                return
        if len(history_arr) < int(args):
            for q in range(len(history_arr)):
                click.echo(f"Операция номер {q}: {history_arr[q]}")
        else:
            for q in range(int(args)):
                click.echo(f"Операция номер {q}: {history_arr[q]}")

def cp_command(ctx, args):
    """Копирование файла или директории"""
    if len(args) < 2:
        click.echo("[ERROR] Использование: cp <источник> <назначение>")
        return

    abs_src = os.path.abspath(args[0])
    abs_dst = os.path.abspath(args[1])

    if not abs_src.startswith(ctx.obj["vfs"]) or not abs_dst.startswith(ctx.obj["vfs"]):
        click.echo("[ERROR] Нельзя выйти за пределы VFS")
        return

    if os.path.isdir(abs_src):
        try:
            shutil.copytree(abs_src, abs_dst)
            click.echo(f"Скопирована директория {args[0]} -> {args[1]}")
        except FileExistsError:
            click.echo(f"[ERROR] Директория {args[1]} уже существует")
    elif os.path.isfile(abs_src):
        try:
            shutil.copy2(abs_src, abs_dst)
            click.echo(f"Скопирован файл {args[0]} -> {args[1]}")
        except Exception as e:
            click.echo(f"[ERROR] Не удалось скопировать файл: {e}")
    else:
        click.echo(f"[ERROR] Источник не найден: {args[0]}")


if __name__ == "__main__":
    cli(obj={})

#Пример запуска
#python main.py --vfs myvfs --script myvfs/scripts/test1.emu repl
