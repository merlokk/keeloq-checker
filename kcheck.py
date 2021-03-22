# (c) 2021, Merlok

import pathlib
import click
from leekoq import decrypt

@click.group()
def kcheck_cli():
    pass


__version__ = open(pathlib.Path(__file__).parent / "VERSION").read().strip()


def diversify_key(key) -> int:
    return key

@kcheck_cli.command()
def version():
    """Version of keeloq checker."""
    click.echo("keeloq checker version: " + __version__)


@kcheck_cli.command()
@click.argument("kmessage")
@click.argument("key")
def decode(kmessage, key):
    kmessage = kmessage.replace(" ", "").replace("\t", "")
    msglen = len(kmessage)
    if msglen != 4 * 2 and msglen != 8 * 2 and msglen != 8 * 2 + 1:
        print("invalid message length " + str(msglen))
        return

    intStaticPart = 0
    if msglen > 4 * 2:
        intStaticPart = int(kmessage[:msglen - 8], base=16)
    intMsg = int(kmessage[-8:], base=16)

    intKey = int(key, base=16)
    print("key=" + hex(intKey) + " static=" + hex(intStaticPart) + " msg=" + hex(intMsg))

    divKey = diversify_key(intKey)
    print("div key=" + hex(divKey))
    print("-----")

    msg = decrypt(intMsg, divKey)
    print("msg=" + hex(msg))

    print("counter: " + hex(msg & 0xffff))
    print("OVR: " + hex(msg >> 26 & 0x3))
    if intStaticPart != 0:
        stKey = intStaticPart >> 28 & 0x0f
        dKey = msg >> 28 & 0x0f
        if stKey == dKey:
            print("Buttons OK [" + hex(stKey) + "]")
        else:
            print("Buttons compare error: " + hex(stKey) + "!=" + hex(dKey))

        stSerial = intStaticPart & 0xffffff
        print("serial number: " + hex(stSerial))
        stSerialDisc = stSerial & 0x3ff
        dDisc = msg >> 16 & 0x3ff
        if stSerialDisc == dDisc:
            print("Serial OK [" + hex(stSerialDisc) + "]")
        else:
            print("Serial an DISC compare error: " + hex(stSerialDisc) + "!=" + hex(dDisc))



if __name__ == '__main__':
    kcheck_cli()
