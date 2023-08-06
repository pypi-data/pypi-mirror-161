import click

printable = (
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOP"
    + "QRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
)

while True:
    c = click.getchar()
    if c == "y":
        click.echo("We will go on")
    elif c == "n":
        click.echo("Abort!")
        break
    elif c == "\x1b[D":
        click.echo("Left arrow <-")
    elif c == "\x1b[C":
        click.echo("Right arrow ->")
    elif c == "\r":
        click.echo("enter ->")
    else:
        click.echo("Invalid input :(")
        click.echo(
            'You pressed: "'
            + "".join(
                [
                    "\\" + hex(ord(i))[1:] if i not in printable else i
                    for i in c
                ]
            )
            + '"'
        )
