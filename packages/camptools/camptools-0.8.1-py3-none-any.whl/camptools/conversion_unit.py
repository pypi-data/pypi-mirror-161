from argparse import ArgumentParser
from pathlib import Path
from emout.utils import Units, InpFile


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('inp')
    parser.add_argument('--dx', '-dx', required=True, type=float)
    parser.add_argument('--output', '-o', default=None)

    return parser.parse_args()


def main():
    args = parse_args()

    inp = InpFile(args.inp)

    unit_from = Units(inp.convkey.dx, inp.convkey.to_c)
    unit_to = Units(args.dx, inp.convkey.to_c)

    inp.conversion(unit_from, unit_to)

    inppath = Path(args.inp)
    filename = args.output or f'{inppath.stem}_conv.{inppath.suffix}'

    inp.save(filename)


if __name__ == '__main__':
    main()
