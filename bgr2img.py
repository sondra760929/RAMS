import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import PurePath
from struct import unpack
from matplotlib.colors import LinearSegmentedColormap
import os
from PIL import Image

def bgr2plt(inFile, outFile, verbose):
    with open(inFile, "rb") as fp:
        header = _parseHeader(fp)
        _writePlt(header, fp, outFile)

    if verbose:
        _printHeader(header)

    print(f"Done: {inFile} ---> {outFile}")

def bgr2image(inFile, verbose):
    with open(inFile, "rb") as fp:
        inFile = PurePath(inFile)
        dirname = inFile.parent
        basename = inFile.stem
        output = PurePath.joinpath(dirname, basename + ".jpg")

        header = _parseHeader(fp)
        _writeImage(header, fp, output)

    if verbose:
        _printHeader(header)

    print(f"Done: {inFile} ")


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

def _writeImage(h, fp, outFile):
    x0 = h["x0"]
    y0 = h["y0"]
    dX = h["dX"]
    dY = h["dY"]
    nX = h["nX"]
    nY = h["nY"]
    
    data = np.zeros((nX, nY))
    # np.arange(nX * nY).reshape((nX, nY))
    for _ in range(h["nP"]):
        i = unpack("<i", fp.read(4))[0]
        x = x0 + i * dX
        j = unpack("<i", fp.read(4))[0]
        y = y0 + j * dY
        v = unpack("<d", fp.read(8))[0]
        # out.write(f"{x:3.5f} {y:2.5f} {v}\n")
        data[i-1][j-1] = v;
        
    fig, ax = plt.subplots()

    ax.set_xticks(np.arange(data.shape[1]) + 0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[0]) + 0.5, minor=False)

    ax.xaxis.tick_top()
    plt.xticks(rotation=90)

    # ax.set_xticklabels(xlabels, minor=False)
    # ax.set_yticklabels(ylabels, minor=False)
    
    # heatmap = ax.pcolor(data)

    ax = plt.gca()

    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False

    # plt.show()
    fig = plt.figure(frameon=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    # ax.imshow(data, aspect='auto',interpolation="quadric",cmap='rainbow_alpha')
    ax.imshow(data, aspect='auto',interpolation="quadric", cmap='gray', vmax=662.2709169303373)
    plt.savefig(str(outFile) + ".jpg")
    im = Image.open(str(outFile) + ".jpg").convert('RGB')
    im.save(str(outFile) + ".png", 'png')
    with open(str(outFile) + ".txt", "w") as out:
        out.write(
            f"# {h['vMax']} {h['vMin']} {h['dT']} {h['x0']:3.6f} {h['y0']:2.6f} {h['z0']:2.6f} {h['dX']:.6f} {h['dY']:.6f} {h['nP']}\n"
        )

    # with open(outFile, "w") as out:
    #     out.write(
    #         f"# {h['vMax']} {h['vMin']} {h['dT']} {h['x0']:3.6f} {h['y0']:2.6f} {h['z0']:2.6f} {h['dX']:.6f} {h['dY']:.6f} {h['nP']}\n"
    #     )
    #     out.write(f"ZONE I = {h['nX']}, J = {h['nY']}\n")
    #     for _ in range(h["nP"]):
    #         i = unpack("<i", fp.read(4))[0]
    #         x = x0 + i * dX
    #         j = unpack("<i", fp.read(4))[0]
    #         y = y0 + j * dY
    #         v = unpack("<d", fp.read(8))[0]
    #         out.write(f"{x:3.5f} {y:2.5f} {v}\n")


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
            # get colormap
        ncolors = 256
        color_array = plt.get_cmap('rainbow')(range(ncolors))

        # change alpha values
        # color_array[:,-1] = np.linspace(0.0,1.0,ncolors)
        color_array[0][3] = 0

        # create a colormap object
        map_object = LinearSegmentedColormap.from_list(name='rainbow_alpha',colors=color_array)

        # register this new colormap with matplotlib
        plt.register_cmap(cmap=map_object)

        path_dir = args.input
        folder_list = os.listdir(path_dir)
        for folder_name in folder_list:
            file_list = os.listdir(path_dir + "\\" + folder_name)
            for file_name in file_list:
                file_ext = os.path.splitext(file_name)[1]
                if file_ext == '.bgr' :
                    if os.path.isfile(path_dir + "\\" + folder_name + "\\" + os.path.splitext(file_name)[0] + ".jpg") == False :
                        bgr2image(path_dir + "\\" + folder_name + "\\" +  file_name, args.verbose)
                        
        # bgr2image(args.input, args.output, args.verbose)
    except (FileNotFoundError, UnknownBinaryFormatError) as e:
        print(e)
