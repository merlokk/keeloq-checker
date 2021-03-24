# (c) 2021, Merlok

import pathlib
import click
from numpy import int64

from leekoq import decrypt

@click.group()
def kcheck_cli():
    pass


__version__ = open(pathlib.Path(__file__).parent / "VERSION").read().strip()


def hex_bit_reverse(data: str) -> str:
    bdata = int('{:08b}'.format(int(data, base=16))[::-1], 2)
    return hex(bdata)[2:]


def diversify_key(man_code: int, serial: int = 0, simple: bool = True) -> int64:
    if simple:
        return man_code

    srcH = 0x60000000 + (serial & 0x0fffffff)
    srcL = 0x20000000 + (serial & 0x0fffffff)

    keyH: int64 = decrypt(srcH, man_code)
    keyL: int64 = decrypt(srcL, man_code)

    print(hex(keyH), hex(keyL))

    return (keyH << 32) + keyL


@kcheck_cli.command()
def version():
    """Version of keeloq checker."""
    click.echo("keeloq checker version: " + __version__)


@kcheck_cli.command()
@click.argument("kmessage")
@click.argument("key")
@click.option("-r", "--reverse", is_flag=True, help="check message in the reverse order")
@click.option("-s", "--simple", is_flag=True, help="use simple learning. manufacturer code is remote's code")
def decode(kmessage, key, reverse, simple):
    kmessage = kmessage.replace(" ", "").replace("\t", "")
    msglen = len(kmessage)
    if msglen != 4 * 2 and msglen != 8 * 2 and msglen != 8 * 2 + 1:
        print("invalid message length " + str(msglen))
        return

    if reverse:
        kmessage = hex_bit_reverse(kmessage)
        print("reversed = " + kmessage)

    intStaticPart = 0
    if msglen > 4 * 2:
        intStaticPart = int(kmessage[:msglen - 8], base=16)
    intMsg = int(kmessage[-8:], base=16)

    intKey = int(key, base=16)
    print("key=" + hex(intKey) + " static=" + hex(intStaticPart) + " msg=" + hex(intMsg))
    stSerial = intStaticPart & 0x0fffffff    # 28 bit
    print("serial number: " + hex(stSerial))

    divKey = diversify_key(intKey, stSerial, simple)
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

        stSerialDisc = stSerial & 0x3ff
        dDisc = msg >> 16 & 0x3ff
        if stSerialDisc == dDisc:
            print("Serial OK [" + hex(stSerialDisc) + "]")
        else:
            if dDisc == 0:
                print("decoded DISC==0. key candidate.")
            else:
                print("Serial an DISC compare error: " + hex(stSerialDisc) + "!=" + hex(dDisc))



if __name__ == '__main__':
    kcheck_cli()
