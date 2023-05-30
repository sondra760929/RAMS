import argparse
from pathlib import PurePath
from struct import unpack
import os

def bgr2plt(inFile, outFile, verbose):
    with open(inFile, "rb") as fp:
        header = _parseHeader(fp)
        _writePlt(header, fp, outFile)

    if verbose:
        _printHeader(header)

    print(f"Done: {inFile} ---> {outFile}")


def _parseHeader(fp):
    first4 = unpack("<4c", fp.read(4))
    desc = b"".join(list(first4)).decode("utf-8")

    if desc != "BGSP":
        raise UnknownBinaryFormatError(desc)

    return {
        "desc": desc,
        "vMax": unpack("<d", fp.read(8))[0],
        "vMin": unpack("<d", fp.read(8))[0],
        "dT": unpack("<d", fp.read(8))[0],
        "x0": unpack("<d", fp.read(8))[0],
        "y0": unpack("<d", fp.read(8))[0],
        "z0": unpack("<d", fp.read(8))[0],
        "dX": unpack("<d", fp.read(8))[0],
        "dY": unpack("<d", fp.read(8))[0],
        "nX": unpack("<i", fp.read(4))[0],
        "nY": unpack("<i", fp.read(4))[0],
        "nP": unpack("<i", fp.read(4))[0],
    }


def _writePlt(h, fp, outFile):
    x0 = h["x0"]
    y0 = h["y0"]
    dX = h["dX"]
    dY = h["dY"]
    with open(outFile, "w") as out:
        out.write(
            f"# {h['vMax']} {h['vMin']} {h['dT']} {h['x0']:3.6f} {h['y0']:2.6f} {h['z0']:2.6f} {h['dX']:.6f} {h['dY']:.6f} {h['nP']}\n"
        )
        out.write(f"ZONE I = {h['nX']}, J = {h['nY']}\n")
        for _ in range(h["nP"]):
            i = unpack("<i", fp.read(4))[0]
            x = x0 + i * dX
            j = unpack("<i", fp.read(4))[0]
            y = y0 + j * dY
            v = unpack("<d", fp.read(8))[0]
            out.write(f"{x:3.5f} {y:2.5f} {v}\n")


def _printHeader(h):
    print(f"desc: {h['desc']}")
    print(f"(vMax, vMin): ({h['vMax']}, {h['vMin']})")
    print(f"dT: {h['dT']}")
    print(f"(x0, y0, z0): ({h['x0']}, {h['y0']}, {h['z0']})")
    print(f"(dX, dY): ({h['dX']}, {h['dY']})")
    print(f"(nX, nY): ({h['nX']}, {h['nY']})")
    print(f"# of points: {h['nP']}")


def _parseArgs():
    parser = argparse.ArgumentParser(
        description="Generates .plt(ascii) from .bgr(binary)."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="input file full path",
    )

    parser.add_argument(
        "--output",
        required=False,
        help="output file full path(if omitted, same as input except extension)",
    )

    # parser.add_argument("--verbose", action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "--verbose", action="store_true", help="print header information"
    )
    parser.add_argument("--no-verbose", action="store_false")
    parser.set_defaults(verbose=False)

    args = parser.parse_args()

    if args.output is None:
        inFile = PurePath(args.input)
        dirname = inFile.parent
        basename = inFile.stem
        args.output = PurePath.joinpath(dirname, basename)

    return args


class UnknownBinaryFormatError(Exception):
    def __init__(self, desc):
        self.desc = desc

    def __str__(self):
        return f"Error: Unknown binary format {self.desc}"


if __name__ == "__main__":
    try:
        args = _parseArgs()
        bgr2plt(args.input, args.output, args.verbose)
    except (FileNotFoundError, UnknownBinaryFormatError) as e:
        print(e)
