from commands import (
    ICommand,
    OpenCommand,
    WriteCommand,
    WriteAsCommand,
    QuitCommand,
    QuitForceCommand,
    WriteQuitCommand,
    GotoLineCommand,
    ToggleNumbersCommand,
    HelpCommand,
    ToggleSyntaxCommand,
    UnknownCommand,
)


def create_command(editor, cmd_string: str) -> ICommand:
    cmd = cmd_string.strip()

    if not cmd:
        return UnknownCommand("")

    if cmd.startswith("o "):
        return OpenCommand(editor, cmd[2:].strip())

    if cmd == "w":
        return WriteCommand(editor)

    if cmd.startswith("w "):
        return WriteAsCommand(editor, cmd[2:].strip())

    if cmd == "q":
        return QuitCommand(editor)

    if cmd == "q!":
        return QuitForceCommand()

    if cmd in ("wq!", "x"):
        return WriteQuitCommand(editor)

    if cmd.isdigit():
        return GotoLineCommand(editor, int(cmd))

    if cmd == "set num":
        return ToggleNumbersCommand(editor)

    if cmd == "h":
        return HelpCommand(editor)

    if cmd == "sy":
        return ToggleSyntaxCommand(editor)

    return UnknownCommand(cmd)
