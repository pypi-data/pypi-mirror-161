"""
simmanager create <name> --key <key> --from <directory> --extent
    create simulation set (directory name = exp_<name>(_<latest_index>)?)
    <name> : created directory name, e.g. exp_<name>
    --key <key> : directory set name
    --inp : input parameter filepath (e.g. plasma.inp)
    --from <directory> : continue from <directory>
    --extent : create directory exp_<name>_<latest_index + 1> from exp_<name>_<latest_index>
    --run : run simulation after craeting simulation set

simmanager run <name>
    run simulation (directory name = exp_<name>(_<latest_index>)?)
"""
import re
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Dict, List, Tuple

import emout
from emout.utils import InpFile, Units
from f90nml import Namelist

from ..utils import call, copy, symlinkdir
from .utils import (create_directory, create_inpFile, fork_inpFile,
                    latest_directory_index)
from dataclasses import dataclass
import math


@dataclass
class EmissionSurface:
    nemd: int
    curf: float
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    zmin: float
    zmax: float

    def saveinp(self, inp: InpFile, index: int):
        inp.setlist('emissn', 'nemd', self.nemd, start_index=index)
        inp.setlist('emissn', 'curfs', self.curf, start_index=index)
        inp.setlist('emissn', 'xmine', self.xmin, start_index=index)
        inp.setlist('emissn', 'xmaxe', self.xmax, start_index=index)
        inp.setlist('emissn', 'ymine', self.ymin, start_index=index)
        inp.setlist('emissn', 'ymaxe', self.ymax, start_index=index)
        inp.setlist('emissn', 'zmine', self.zmin, start_index=index)
        inp.setlist('emissn', 'zmaxe', self.zmax, start_index=index)



def extent_sim(from_dir: Path, to_dir: Path, nstep: int, params: Dict[Tuple[Any], Any] = {}):
    to_dir.mkdir(exist_ok=True)

    data = emout.Emout(from_dir)

    inp = fork_inpFile(data.inp, nstep, params)
    inp.jobnum[0] = 1

    inp.save(to_dir / 'plasma.inp')
    symlinkdir((from_dir / 'SNAPSHOT1').resolve(), to_dir / 'SNAPSHOT0')

    copy(from_dir / 'job.sh', to_dir / 'job.sh')
    copy(from_dir / 'mpiemses3D', to_dir / 'mpiemses3D')

    for prob in (from_dir).glob('prob*.inp'):
        copy(from_dir / prob, to_dir / prob)


def simmanager_create(args: Namespace):
    """simmanager create <name> --key <key> --from <directory> --extent

        create simulation set (directory name = exp_<name>(_<latest_index>)?)

        <name> : created directory name, e.g. exp_<name>
        --key <key> : directory set name
        --inp <filepath> ... <filepath>: input parameter filepath (e.g. plasma.inp)
        --from <directory> : continue from <directory>
        --extent : create directory exp_<name>_<latest_index + 1> from exp_<name>_<latest_index>
        --run : run simulation after craeting simulation set
        --interp: particle generation with interpolation

    Parameters
    ----------
    args : Namespace
        commandline arguments
    """
    base_directory_name = f'exp_{args.name}'
    latest_index = latest_directory_index(base_directory_name)
    new_directory = Path(f'{base_directory_name}_{latest_index+1}')
    new_directory.mkdir(exist_ok=True)

    inp = create_inpFile(*[InpFile(i) for i in args.inp])

    create_directory(new_directory, args.key)
    inp.save(new_directory / 'plasma.inp')


def simmanager_extent(args: Namespace):
    base_directory_name = f'exp_{args.name}'
    latest_index = latest_directory_index(base_directory_name)

    if args.from_dir:
        from_dir = Path(args.from_dir)
    else:
        from_dir = f'{base_directory_name}_{latest_index}'

    new_directory = Path(f'{base_directory_name}_{latest_index+1}')
    new_directory.mkdir(exist_ok=True)

    extent_sim(from_dir, new_directory, args.nstep)


def simmanager_interp(args: Namespace):
    base_directory_name = f'exp_{args.name}'
    latest_index = latest_directory_index(base_directory_name)

    new_directory = Path(f'{base_directory_name}_{latest_index+1}')
    new_directory.mkdir(exist_ok=True)

    from_dir = Path(args.from_dir)

    data = emout.Emout(from_dir)

    inp = InpFile(from_dir / 'plasma.inp')
    inp = fork_inpFile(inp, args.nstep)

    unit_from = Units(inp.convkey.dx, inp.convkey.to_c)
    unit_to = Units(args.dx, inp.convkey.to_c)
    inp.conversion(unit_from, unit_to)

    inp.nx, inp.ny = args.nxy
    inp.zssurf = args.zssurf
    inp.setlist('emissn', 'nepl', [1, 1], start_index=1)
    if args.nodes:
        inp.setlist('tmgrid', 'nodes', args.nodes)

    if args.hole:
        wx, wy, zdepth = args.hole

        hole_xmin = (inp.nx - wx) / 2
        hole_xmax = (inp.nx + wx) / 2
        hole_ymin = (inp.ny - wy) / 2
        hole_ymax = (inp.ny + wy) / 2
        hole_zmin = inp.zssurf - zdepth
        hole_zmax = inp.zssurf

        zenith_deg = float(inp.vdthz[0])
        zenith_rad = math.radians((zenith_deg + 360) % 360)

        emit_x_min = hole_xmin + zdepth * math.tan(zenith_rad)
        if zenith_rad == 0:
            emit_z_min = math.inf
        else:
            emit_z_min = max(inp.zssurf - wx / math.tan(zenith_rad), hole_zmin)

        inp.setlist('ptcond', 'xlrechole', [inp.nx//2-wx/2]*2)
        inp.setlist('ptcond', 'xurechole', [inp.nx//2+wx/2]*2)
        inp.setlist('ptcond', 'ylrechole', [inp.ny//2-wy/2]*2)
        inp.setlist('ptcond', 'yurechole', [inp.ny//2+wy/2]*2)
        inp.setlist('ptcond', 'zlrechole', [args.zssurf-zdepth]*2)
        inp.setlist('ptcond', 'zurechole', [args.zssurf]*2)
        

    if inp.nspec == 3:
        curf = inp.curf[0]

        # 照射角を取得
        zenith_deg = float(inp.vdthz[0])
        zenith_rad = math.radians((zenith_deg + 360) % 360)

        # 光電子電流を計算
        curf_horizon = curf * abs(math.cos(zenith_rad))
        curf_vertical = curf * abs(math.sin(zenith_rad))

        
        esurfs = []
        if args.hole:
            wx, wy, zdepth = args.hole

            esurfs.append(EmissionSurface(3, curf_horizon,
                                            0, hole_xmin, 0, inp.ny, inp.zssurf, inp.zssurf))
            esurfs.append(EmissionSurface(3, curf_horizon,
                                            hole_xmin, hole_xmax, 0, hole_ymin, inp.zssurf, inp.zssurf))
            esurfs.append(EmissionSurface(3, curf_horizon,
                                            hole_xmax, inp.nx, 0, inp.ny, inp.zssurf, inp.zssurf))
            esurfs.append(EmissionSurface(3, curf_horizon,
                                            hole_xmin, hole_xmax, hole_ymax, inp.ny, inp.zssurf, inp.zssurf))
            if emit_x_min < hole_xmax:
                esurfs.append(EmissionSurface(3, curf_horizon,
                                                emit_x_min, hole_xmax, hole_ymin, hole_ymax, hole_zmin, hole_zmin))
            if emit_z_min < inp.zssurf:
                esurfs.append(EmissionSurface(-1, curf_vertical,
                                                hole_xmax, hole_xmax, hole_ymin, hole_ymax, emit_z_min, inp.zssurf))
        else:
            esurfs.append(EmissionSurface(3, curf_horizon,
                                            0, inp.nx, 0, inp.ny, inp.zssurf, inp.zssurf))

        nepl = len(esurfs) + 1
        inp.setlist('emissn', 'nepl', nepl, start_index=3)

        for i, esurf in enumerate(esurfs):
            esurf.saveinp(inp, index=inp.nspec+i+1) # 1: SWE-interp, 2: SWI-interp, 3: PE-interp, 4~: PE-emit


    if 'pclinj' not in inp.nml:
        inp.nml['pclinj'] = Namelist()
    inp.nml['pclinj']['use_pinj'] = True

    for probs_inp_path in Path(from_dir).glob(f'prob*_{args.prob_name}.inp'):
        probs_inp = InpFile(probs_inp_path)
        ispec = int(re.match(r'probs([0-9])_.+.inp',
                             probs_inp_path.name).group(1))

        xinterp = int(probs_inp.interp_domain[0][1])
        yinterp = int(probs_inp.interp_domain[1][1])
        zinterp = int(probs_inp.interp_domain[2][1])

        probs_inp.interp_domain[0][0] = 0
        probs_inp.interp_domain[0][1] = inp.nx
        probs_inp.interp_domain[1][0] = 0
        probs_inp.interp_domain[1][1] = inp.ny
        probs_inp.interp_domain[2][0] = inp.nz
        probs_inp.interp_domain[2][1] = inp.nz

        vxs = probs_inp.interp_domain[3][0]
        vxe = probs_inp.interp_domain[3][1]
        vys = probs_inp.interp_domain[4][0]
        vye = probs_inp.interp_domain[4][1]
        vzs = probs_inp.interp_domain[5][0]
        vze = probs_inp.interp_domain[5][1]
        probs_inp.interp_domain[3][0] = unit_to.v.trans(
            unit_from.v.reverse(vxs))
        probs_inp.interp_domain[3][1] = unit_to.v.trans(
            unit_from.v.reverse(vxe))
        probs_inp.interp_domain[4][0] = unit_to.v.trans(
            unit_from.v.reverse(vys))
        probs_inp.interp_domain[4][1] = unit_to.v.trans(
            unit_from.v.reverse(vye))
        probs_inp.interp_domain[5][0] = unit_to.v.trans(
            unit_from.v.reverse(vzs))
        probs_inp.interp_domain[5][1] = unit_to.v.trans(
            unit_from.v.reverse(vze))

        curf = unit_to.J.trans(unit_from.J.reverse(probs_inp.curf))
        probs_inp.curf = curf

        probs_inp.convkey = inp.convkey
        probs_inp.save(new_directory / probs_inp_path.name)

        # Emmision surface settings.
        index = ispec+1
        inp.setlist('emissn', 'nemd', [-3], start_index=index)
        inp.setlist('emissn', 'curfs', [curf], start_index=index)

        inp.setlist('pclinj', 'interp_param_files',
                    probs_inp_path.name, start_index=index)

        ez = data.ez[args.istep, zinterp, yinterp, xinterp]
        bc = unit_to.E.trans(unit_from.E.reverse(ez))
        inp.nml['system'].start_index['boundary_conditions'] = [2, 3]
        inp.nml['system']['boundary_conditions'] = [[bc]]

    inp.nz = inp.zssurf + unit_from.dx*(zinterp - inp.zssurf)/args.dx

    for probs_inp_path in Path(from_dir).glob(f'prob*_{args.prob_name}.inp'):
        probs_inp = InpFile(probs_inp_path)
        probs_inp.interp_domain[2][0] = inp.nz
        probs_inp.interp_domain[2][1] = inp.nz

    npin = inp.nx*inp.ny*inp.nz*args.dnsf

    inp.setlist('intp', 'npin', [npin, npin])
    if inp.nspec == 3:
        inp.setlist('intp', 'np', [npin*args.pebuf], start_index=3)

    inp.save(new_directory / 'plasma.inp')

    copy(from_dir / 'job.sh', new_directory / 'job.sh')
    copy(from_dir / 'mpiemses3D', new_directory / 'mpiemses3D')


def simmanager_run(args: Namespace):
    base_directory_name = f'exp_{args.name}'
    latest_index = latest_directory_index(base_directory_name)
    directory = Path(f'{base_directory_name}_{latest_index}')

    call(f'myqsub job.sh -d {directory.resolve()}')


def main():
    parser = ArgumentParser()

    subparsers = parser.add_subparsers()

    subparser_create = subparsers.add_parser('create')
    subparser_create.add_argument('name', type=str)
    subparser_create.add_argument('--key', '-key', type=str, required=True)
    subparser_create.add_argument('--inp', '-inp', type=str, nargs='*')
    subparser_create.add_argument('--params', '-p', type=str)
    subparser_create.set_defaults(handler=simmanager_create)

    subparser_extent = subparsers.add_parser('extent')
    subparser_extent.add_argument('name', type=str)
    subparser_extent.add_argument('--nstep', '-n', type=int, default=None)
    subparser_extent.add_argument('--from_dir', '-f', type=str, default=None)
    subparser_extent.set_defaults(handler=simmanager_extent)

    subparser_interp = subparsers.add_parser('interp')
    subparser_interp.add_argument('name', type=str)
    subparser_interp.add_argument('--nstep', '-n', type=int, default=None)
    subparser_interp.add_argument('--from_dir', '-f', type=str, default='./')
    subparser_interp.add_argument(
        '--prob_name', '-pn', type=str, required=True)
    subparser_interp.add_argument('--dx', '-dx', type=float, required=True)
    subparser_interp.add_argument('--zssurf', '-zs', type=int, required=True)
    subparser_interp.add_argument(
        '--hole', '-hole', type=int, nargs=3, help='wx, wy, zdepth', default=None)
    subparser_interp.add_argument(
        '--nxy', '-nxy', type=int, nargs=2, required=True)
    subparser_interp.add_argument('--istep', '-istep', type=int, default=-1)
    subparser_interp.add_argument('--nodes', '-nodes', type=int, nargs=3, default=None)
    subparser_interp.add_argument('--dnsf', '-dnsf', type=int, default=40)
    subparser_interp.add_argument('--pebuf', '-pebuf', type=int, default=10)
    subparser_interp.set_defaults(handler=simmanager_interp)

    subparser_run = subparsers.add_parser('run')
    subparser_run.add_argument('name')
    subparser_run.set_defaults(handler=simmanager_run)

    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
