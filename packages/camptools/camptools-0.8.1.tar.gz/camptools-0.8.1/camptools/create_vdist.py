import os
import pickle as pkl
from argparse import ArgumentParser
from pathlib import Path

import emout
import f90nml
from emout.utils import InpFile, UnitConversionKey
from matplotlib import animation
import numpy as np
from vdsolver.tools.emses import PhaseGrid, VSolveTarget
from vdsolver.tools.emses.utils import create_default_simulator, create_default_pe_simulator
import matplotlib.pyplot as plt


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('--directory', '-d', default='./')
    parser.add_argument('--ispec', '-ispec', type=int, required=True)

    parser.add_argument('--istep', '-is', default=-1, type=int)
    parser.add_argument('--dt', '-dt', default=1.0, type=float)

    parser.add_argument('--position', '-p', type=float, nargs=3, required=True)
    parser.add_argument('--shape', '-s', type=int,
                        nargs=3, required=True)
    parser.add_argument('--vbox', '-vbox', type=float, nargs=6, required=True)

    parser.add_argument('--name', '-name', default='')
    parser.add_argument('--xy_iso', '-iso', action='store_true')

    # Parallel processing parameter
    parser.add_argument('--maxstep', '-ms', default=10000, type=int)
    parser.add_argument('--max_workers', '-mw', default=8, type=int)
    parser.add_argument('--chunksize', '-chk', default=100, type=int)
    parser.add_argument('--use_mpi', '-mpi', action='store_true')

    parser.add_argument('--output', '-o', default=None)
    parser.add_argument('--writer', '-writer', default='quantized-pillow')

    return parser.parse_args()


def solve_vdist(data: emout.Emout,
                ispec: int,
                istep: int,
                name: str,
                phase_grid: PhaseGrid,
                dt: float,
                maxstep: int,
                max_workers: int,
                chunksize: int = 16,
                use_mpi: bool = False,
                xy_iso: bool = False,
                output: str = None,
                writer: str = 'quantized-pillow'):

    NX = phase_grid.xlim.num
    NY = phase_grid.ylim.num
    NZ = phase_grid.zlim.num
    NVX = phase_grid.vxlim.num
    NVY = phase_grid.vylim.num
    NVZ = phase_grid.vzlim.num

    if ispec in (0, 1):
        sim = create_default_simulator(data,
                                       ispec,
                                       istep,
                                       use_si=False,
                                       use_hole=False)
    elif ispec in (2, ):
        sim = create_default_pe_simulator(data,
                                          ispec,
                                          istep,
                                          use_si=False,
                                          use_hole=False)
    else:
        raise Exception('ispec is not 0 or 1 or 2.')

    if xy_iso:
        vxs, vxe, nvx = phase_grid.vxlim.tolist()
        dvx = (vxe - vxs) / nvx
        phase_grid_xz = PhaseGrid(
            x=phase_grid.xlim,
            y=phase_grid.ylim,
            z=phase_grid.zlim,
            vx=(0, 2*vxe+dvx, nvx),
            vy=(0, 0, 1),
            vz=phase_grid.vzlim,
        )

        target = VSolveTarget(data,
                              sim,
                              phase_grid_xz,
                              maxstep,
                              max_workers,
                              chunksize,
                              ispec,
                              dt,
                              istep,
                              show_progress=True,
                              use_mpi=use_mpi,
                              )

        phases_xz, probs_xz = target.solve()

        phases = phase_grid.create_grid()
        phases = phases[0, 0, 0].reshape(NVZ, NVY, NVX, 6)

        # probs[nz, ny, nx, nvz, nvy, nvx]
        probs = np.zeros((NZ, NY, NX, NVZ, NVY, NVX))
        for ivy in range(NVY):
            for ivx in range(NVX):
                v = np.sqrt((vxs+ivx*dvx)**2 + (vxs+ivy*dvx)**2)/np.sqrt(2)
                v /= (phase_grid_xz.vxlim.end -
                      phase_grid_xz.vxlim.start) / phase_grid_xz.vxlim.num

                iv = int(v)
                r = v - iv

                probs[:, :, :, :, ivy, ivx] = \
                    probs_xz[:, :, :, :, 0, iv]*(1-r) \
                    + probs_xz[:, :, :, :, 0, iv+1]*r

    else:
        target = VSolveTarget(data,
                              sim,
                              phase_grid,
                              maxstep,
                              max_workers,
                              chunksize,
                              ispec,
                              dt,
                              istep,
                              show_progress=True,
                              use_mpi=use_mpi,
                              )

        phases, probs = target.solve()

        phases = phases[0, 0, 0].reshape(NVZ, NVY, NVX, 6)

    VZ = phases[:, :, :, 5]

    with open(f'probs{ispec}_{name}.pkl', 'wb') as f:
        pkl.dump(probs, f)

    # Integrate by 0-degree integration
    dvx = (phase_grid.vxlim.end - phase_grid.vxlim.start) / \
        phase_grid.vxlim.num
    dvy = (phase_grid.vylim.end - phase_grid.vylim.start) / \
        phase_grid.vylim.num
    dvz = (phase_grid.vzlim.end - phase_grid.vzlim.start) / \
        phase_grid.vzlim.num

    n0 = data.inp.wp[ispec]**2 / data.inp.qm[ispec]
    curf = (n0 * probs[0, 0, 0] * VZ).sum() * (dvx * dvy * dvz)
    curf = abs(curf)

    # Output data.
    filepath = Path(f'probs{ispec}_{name}.dat')
    nmlpath = Path(f'{filepath.stem}.inp')

    # Output probabilities defined on grid.
    # probs[nz, ny, nx, nvz, nvy, nvx] to new_probs[nvz, nvy, nvx, nz, ny, nx]
    new_probs = np.zeros((NVZ, NVY, NVX, NZ, NY, NX))
    for ix in range(NX):
        for iy in range(NY):
            for iz in range(NZ):
                new_probs[:, :, :, iz, iy, ix] = \
                    probs[iz, iy, ix, :, :, :]
    endian = '<'
    new_probs.reshape([-1]) \
        .astype(endian+'d') \
        .tofile(str(filepath))

    vmin = new_probs.min()
    vmax = new_probs.max()

    def plot(ivy):
        plt.clf()

        im = plt.imshow(new_probs[:, ivy, :, 0, 0, 0],
                        origin='lower', vmin=vmin, vmax=vmax)

        plt.xlabel('VX')
        plt.ylabel('VZ')
        plt.title(f'VY = {ivy}')
        plt.colorbar()

    if output:
        fig = plt.figure()

        ani = animation.FuncAnimation(fig, plot, range(NVY), interval=100)
        ani.save(output, writer=writer)

    nml = {
        'interp':
            {
                'ispec': ispec+1,
                'curf': curf,
                'interp_filename': str(filepath.resolve()),
                'interp_domain': [
                    phase_grid.xlim.tolist(),
                    phase_grid.ylim.tolist(),
                    phase_grid.zlim.tolist(),
                    phase_grid.vxlim.tolist(),
                    phase_grid.vylim.tolist(),
                    phase_grid.vzlim.tolist(),
                ],
            }
    }

    inp = InpFile()
    inp.nml = nml
    inp.convkey = data.inp.convkey

    if os.path.exists(nmlpath):
        os.remove(str(nmlpath))

    inp.save(nmlpath)


def main():
    args = parse_args()

    data = emout.Emout(args.directory)

    NX = NY = NZ = 1
    NVX, NVY, NVZ = args.shape
    X, Y, Z = args.position

    vxs, vxe, vys, vye, vzs, vze = args.vbox

    phase_grid = PhaseGrid(
        x=(X, X, NX),
        y=(Y, Y, NY),
        z=(Z, Z, NZ),
        vx=(vxs, vxe, NVX),
        vy=(vys, vye, NVY),
        vz=(vzs, vze, NVZ),
    )

    solve_vdist(data,
                args.ispec,
                args.istep,
                args.name,
                phase_grid,
                args.dt,
                args.maxstep,
                args.max_workers,
                args.chunksize,
                args.use_mpi,
                xy_iso=args.xy_iso,
                output=args.output,
                writer=args.writer)


if __name__ == '__main__':
    main()
