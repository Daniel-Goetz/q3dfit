# -*- coding: utf-8 -*-
import copy as copy
import importlib
import importlib.resources as pkg_resources
import matplotlib as mpl
import numpy as np
import os
import q3dfit.q3df_helperFunctions as q3dutil

from astropy.table import Table
from q3dfit.data import linelists


def q3da(q3di, cols=None, rows=None, noplots=False, quiet=True,
         inline=True):
    """
    Routine to collate spaxel information together plot the continuum fits to a
    spectrum.

    As input, it requires a q3di and q3do object.

    Parameters
    ----------
    q3di: in, required, type=string
        Name of procedure to initialize the fit.
    cols: in, optional, type=intarr, default=all
        Columns to fit, in 1-offset format. Either a scalar or a
        two-element vector listing the first and last columns to fit.
    rows: in, optional, type=intarr, default=all
        Rows to fit, in 1-offset format. Either a scalar or a
        two-element vector listing the first and last rows to fit.
    noplots: in, optional, type=byte
        Disable plotting.
    quiet: in, optional, type=boolean
        Print error and progress messages. Propagates to most/all subroutines.

    Returns
    -------

    """
    bad = 1e99

    if inline is False:
        mpl.use('agg')

    q3di = q3dutil.__get_q3dio(q3di)

    if q3di.dolinefit:

        linelist = q3dutil.__get_linelist(q3di)

        # table with doublets to combine
        with pkg_resources.path(linelists, 'doublets.tbl') as p:
            doublets = Table.read(p, format='ipac')
        # make a copy of singlet list
        lines_with_doublets = copy.deepcopy(q3di.lines)
        # append doublet names to singlet list
        for (name1, name2) in zip(doublets['line1'], doublets['line2']):
            if name1 in linelist['name'] and name2 in linelist['name']:
                lines_with_doublets.append(name1+'+'+name2)

    # READ DATA
    cube, vormap = q3dutil.__get_Cube(q3di, quiet)
    nspax, colarr, rowarr = q3dutil.__get_spaxels(cube, cols=cols, rows=rows)
    # TODO
    # if q3di.vormap is not None:
    #     vormap = q3di.vromap
    #     nvorcols = max(vormap)
    #     vorcoords = np.zeros(nvorcols, 2)
    #     for i in range(0, nvorcols):
    #         xyvor = np.where(vormap == i).nonzero()
    #         vorcoords[:, i] = xyvor

# INITIALIZE OUTPUT FILES, need to write helper functions (printlinpar,
# printfitpar) later

# INITIALIZE LINE HASH
    if q3di.dolinefit:
        emlwav = dict()
        emlwaverr = dict()
        emlsig = dict()
        emlsigerr = dict()
        emlweq = dict()
        emlflx = dict()
        emlflxerr = dict()
        emlncomp = dict()
        emlweq['ftot'] = dict()
        emlflx['ftot'] = dict()
        emlflxerr['ftot'] = dict()
        for k in range(0, q3di.maxncomp):
            cstr = 'c' + str(k + 1)
            emlwav[cstr] = dict()
            emlwaverr[cstr] = dict()
            emlsig[cstr] = dict()
            emlsigerr[cstr] = dict()
            emlweq['f' + cstr] = dict()
            emlflx['f' + cstr] = dict()
            emlflxerr['f' + cstr] = dict()
            emlflx['f' + cstr + 'pk'] = dict()
            emlflxerr['f' + cstr + 'pk'] = dict()
        for line in lines_with_doublets:
            emlncomp[line] = np.zeros((cube.ncols, cube.nrows), dtype=int)
            emlweq['ftot'][line] = np.zeros((cube.ncols, cube.nrows),
                                            dtype=float) + bad
            emlflx['ftot'][line] = np.zeros((cube.ncols, cube.nrows),
                                            dtype=float) + bad
            emlflxerr['ftot'][line] = np.zeros((cube.ncols, cube.nrows),
                                               dtype=float) + bad
            for k in range(0, q3di.maxncomp):
                cstr = 'c' + str(k + 1)
                emlwav[cstr][line] = np.zeros((cube.ncols, cube.nrows),
                                              dtype=float) + bad
                emlwaverr[cstr][line] = np.zeros((cube.ncols, cube.nrows),
                                                 dtype=float) + bad
                emlsig[cstr][line] = np.zeros((cube.ncols, cube.nrows),
                                              dtype=float) + bad
                emlsigerr[cstr][line] = np.zeros((cube.ncols, cube.nrows),
                                                 dtype=float) + bad
                emlweq['f'+cstr][line] = np.zeros((cube.ncols, cube.nrows),
                                                  dtype=float) + bad
                emlflx['f'+cstr][line] = np.zeros((cube.ncols, cube.nrows),
                                                  dtype=float) + bad
                emlflxerr['f'+cstr][line] = np.zeros((cube.ncols, cube.nrows),
                                                     dtype=float) + bad
                emlflx['f'+cstr+'pk'][line] = \
                    np.zeros((cube.ncols, cube.nrows),
                             dtype=float) + bad
                emlflxerr['f'+cstr+'pk'][line] = \
                    np.zeros((cube.ncols, cube.nrows),
                             dtype=float) + bad

    # LOOP THROUGH SPAXELS
    # switch to track when first continuum processed
    firstcontproc = True

    for ispax in range(0, nspax):
        i = colarr[ispax]
        j = rowarr[ispax]

        if not quiet:
            print(f'Column {i+1} of {cube.ncols}')

        # set this to false unless we're using Voronoi binning
        # and the tiling is missing
        vortile = True
        labin = '{0.outdir}{0.label}'.format(q3di)
        if cube.dat.ndim == 1:
            flux = cube.dat
            err = cube.err
            dq = cube.dq
            labout = labin
        elif cube.dat.ndim == 2:
            flux = cube.dat[:, i]
            err = cube.err[:, i]
            dq = cube.dq[:, i]
            labin += '_{:04d}'.format(i+1)
            labout = labin
        else:
            if not quiet:
                print(f'    Row {j+1} of {cube.nrows}')

            # TODO
            # if q3di.vormap is not None:
            #    if np.isfinite(q3di.vormap[i][j]) and \
            #            q3di.vormap[i][j] is not bad:
            #        iuse = vorcoords[q3di.vormap[i][j] - 1, 0]
            #        juse = vorcoords[q3di.vormap[i][j] - 1, 1]
            #    else:
            #        vortile = False
            #else:
            iuse = i
            juse = j

            if vortile:
                flux = cube.dat[iuse, juse, :].flatten()
                err = cube.err[iuse, juse, :].flatten()
                dq = cube.dq[iuse, juse, :].flatten()
                labin = '{0.outdir}{0.label}_{1:04d}_{2:04d}'.\
                    format(q3di, iuse+1, juse+1)
                labout = '{0.outdir}{0.label}_{1:04d}_{2:04d}'.\
                    format(q3di, i+1, j+1)

        # Restore fit after a couple of sanity checks
        if vortile:
            infile = labin + '.npy'
            outfile = labout
            nodata = flux.nonzero()
            ct = len(nodata[0])
        else:
            # missing data for this spaxel
            filepresent = False
            ct = 0

        if ct == 0 or not os.path.isfile(infile):

            badmessage = f'        No data for [{i+1}, {j+1}]'
            print(badmessage)

        else:

            q3do = q3dutil.__get_q3dio(infile)

            # Restore original error.
            q3do.spec_err = err[q3do.fitran_indx]

            # q3do.sepfitpars(tflux=True, doublets=doublets)

            if q3do.dolinefit:
                # get correct number of components in this spaxel
                thisncomp = 0
                thisncompline = ''

                for line in lines_with_doublets:
                    sigtmp = q3do.line_fitpars['sigma'][line]
                    fluxtmp = q3do.line_fitpars['flux'][line]
                    # TODO
                    igd = [idx for idx in range(len(sigtmp)) if
                           (sigtmp[idx] != 0 and
                            sigtmp[idx] != bad and
                            fluxtmp[idx] != 0 and
                            fluxtmp[idx] != bad)]
                    ctgd = len(igd)

                    if ctgd > thisncomp:
                        thisncomp = ctgd
                        thisncompline = line

                    # assign total fluxes
                    if ctgd > 0:
                        emlflx['ftot'][line][i, j] = \
                            q3do.line_fitpars['tflux'][line]
                        emlflxerr['ftot'][line][i, j] = \
                            q3do.line_fitpars['tfluxerr'][line]

                    # assign to output dictionary
                    emlncomp[line][i,j] = ctgd

                if thisncomp == 1:
                    isort = [0]
                elif thisncomp >= 2:
                    # sort components on sigma
                    igd = np.arange(thisncomp)
                    sigtmp = q3do.line_fitpars['sigma'][thisncompline]
                    # fluxtmp = q3do.line_fitpars['flux'][thisncompline]
                    isort = np.argsort(sigtmp[igd])
                if thisncomp > 0:
                    for line in lines_with_doublets:
                        kcomp = 1
                        for sindex in isort:
                            cstr = 'c' + str(kcomp)
                            emlwav[cstr][line][i, j] \
                                = q3do.line_fitpars['wave'][line].data[sindex]
                            emlwaverr[cstr][line][i, j] \
                                = q3do.line_fitpars['waveerr'][line].data[sindex]
                            emlsig[cstr][line][i, j] \
                                = q3do.line_fitpars['sigma'][line].data[sindex]
                            emlsigerr[cstr][line][i, j] \
                                = q3do.line_fitpars['sigmaerr'][line].data[sindex]
#                            emlweq['f' + cstr][line][i, j] \
#                                = lineweqs['comp'][line].data[sindex]
                            emlflx['f' + cstr][line][i, j] \
                                = q3do.line_fitpars['flux'][line].data[sindex]
                            emlflxerr['f' + cstr][line][i, j] \
                                = q3do.line_fitpars['fluxerr'][line].data[sindex]
                            emlflx['f' + cstr + 'pk'][line][i, j] \
                                = q3do.line_fitpars['fluxpk'][line].data[sindex]
                            emlflxerr['f' + cstr + 'pk'][line][i, j] \
                                = q3do.line_fitpars['fluxpkerr'][line].data[sindex]
                            kcomp += 1

            # Process and plot continuum data
            # make and populate output data cubes
            if firstcontproc is True:
                hostcube = \
                   {'dat': np.zeros((cube.ncols, cube.nrows, cube.nwave)),
                    'err': np.zeros((cube.ncols, cube.nrows, cube.nwave)),
                    'dq':  np.zeros((cube.ncols, cube.nrows, cube.nwave)),
                    'norm_div': np.zeros((cube.ncols, cube.nrows,
                                          cube.nwave)),
                    'norm_sub': np.zeros((cube.ncols, cube.nrows,
                                          cube.nwave))}

                if q3di.decompose_ppxf_fit is not None:
                    contcube = \
                        {'wave': q3do.wave,
                         'all_mod': np.zeros((cube.ncols, cube.nrows,
                                              cube.nwave)),
                         'stel_mod': np.zeros((cube.ncols, cube.nrows,
                                               cube.nwave)),
                         'poly_mod': np.zeros((cube.ncols, cube.nrows,
                                               cube.nwave)),
                         'stel_mod_tot': np.zeros((cube.ncols, cube.nrows))
                         + bad,
                         'poly_mod_tot': np.zeros((cube.ncols, cube.nrows))
                         + bad,
                         'poly_mod_tot_pct': np.zeros((cube.ncols,
                                                       cube.nrows))
                         + bad,
                         'stel_sigma': np.zeros((cube.ncols, cube.nrows))
                         + bad,
                         'stel_sigma_err': np.zeros((cube.ncols,
                                                     cube.nrows, 2))
                         + bad,
                         'stel_z': np.zeros((cube.ncols, cube.nrows))
                         + bad,
                         'stel_z_err': np.zeros((cube.ncols, cube.nrows,
                                                 2)) + bad,
                         'stel_rchisq': np.zeros((cube.ncols, cube.nrows))
                         + bad,
                         'stel_ebv': np.zeros((cube.ncols, cube.nrows))
                         + bad,
                         'stel_ebv_err': np.zeros((cube.ncols, cube.nrows,
                                                   2)) + bad}

                elif q3di.decompose_qso_fit is not None:
                    contcube = \
                        {'wave': q3do.wave,
                         'qso_mod':
                             np.zeros((cube.ncols, cube.nrows,
                                       cube.nwave)),
                         'qso_poly_mod':
                             np.zeros((cube.ncols, cube.nrows,
                                       cube.nwave)),
                         'host_mod':
                             np.zeros((cube.ncols, cube.nrows,
                                       cube.nwave)),
                         'poly_mod':
                             np.zeros((cube.ncols, cube.nrows,
                                       cube.nwave)),
                         'npts':
                             np.zeros((cube.ncols, cube.nrows)) + bad,
                         'stel_sigma':
                             np.zeros((cube.ncols, cube.nrows)) + bad,
                         'stel_sigma_err':
                             np.zeros((cube.ncols, cube.nrows, 2)) + bad,
                         'stel_z':
                             np.zeros((cube.ncols, cube.nrows)) + bad,
                         'stel_z_err':
                             np.zeros((cube.ncols, cube.nrows, 2)) + bad,
                         'stel_rchisq':
                             np.zeros((cube.ncols, cube.nrows)) + bad,
                         'stel_ebv':
                             np.zeros((cube.ncols, cube.nrows)) + bad,
                         'stel_ebv_err':
                             np.zeros((cube.ncols, cube.nrows, 2)) + bad}
                else:
                    contcube = \
                        {'all_mod':
                         np.zeros((cube.ncols, cube.nrows, cube.nwave)),
                         'stel_z':
                             np.zeros((cube.ncols, cube.nrows)) + bad,
                         'stel_z_err':
                             np.zeros((cube.ncols, cube.nrows, 2)) + bad,
                         'stel_rchisq':
                             np.zeros((cube.ncols, cube.nrows)) + bad,
                         'stel_ebv':
                             np.zeros((cube.ncols, cube.nrows)) + bad,
                         'stel_ebv_err':
                             np.zeros((cube.ncols, cube.nrows, 2)) + bad}
                firstcontproc = False

            hostcube['dat'][i, j, q3do.fitran_indx] = \
                q3do.cont_dat
            hostcube['err'][i, j, q3do.fitran_indx] = \
                err[q3do.fitran_indx]
            hostcube['dq'][i, j, q3do.fitran_indx] = \
                dq[q3do.fitran_indx]
            hostcube['norm_div'][i, j, q3do.fitran_indx] \
                = np.divide(q3do.cont_dat, q3do.cont_fit)
            hostcube['norm_sub'][i, j, q3do.fitran_indx] \
                = np.subtract(q3do.cont_dat, q3do.cont_fit)

            if q3di.decompose_ppxf_fit is not None:
                # Total flux fromd ifferent components
                cont_fit_tot = np.sum(q3do.cont_fit)
                contcube['all_mod'][i, j, q3do.fitran_indx] = \
                    q3do.cont_fit
                contcube['stel_mod'][i, j, q3do.fitran_indx] = \
                    cont_fit_stel
                contcube['poly_mod'][i, j, q3do.fitran_indx] = \
                    cont_fit_poly
                contcube['stel_mod_tot'][i, j] = np.sum(cont_fit_stel)
                contcube['poly_mod_tot'][i, j] = np.sum(cont_fit_poly)
                contcube['poly_mod_tot_pct'][i, j] \
                    = np.divide(contcube['poly_mod_tot'][i, j], cont_fit_tot)
                contcube['stel_sigma'][i, j] = q3do.ct_ppxf_sigma
                contcube['stel_z'][i, j] = q3do.zstar

                if q3do.ct_ppxf_sigma_err is not None:
                    contcube['stel_sigma_err'][i, j, :] \
                        = q3do.ct_ppxf_sigma_err
                if q3do.zstar_err is not None:
                    contcube['stel_z_err'][i, j, :] \
                        = q3do.zstar_err

            elif q3di.decompose_ppxf_fit is not None:
                if q3di.fcncontfit == 'fitqsohost':
                    if 'refit' in q3di.argscontfit and \
                        'args_questfit' not in q3di.argscontfit:

                        contcube['stel_sigma'][i, j] = \
                            q3do.ct_coeff['ppxf_sigma']
                        contcube['stel_z'][i, j] = q3do.zstar

                        if q3do.ct_ppxf_sigma_err is not None:
                            contcube['stel_sigma_err'][i, j, :] \
                                = q3do.ct_ppxf_sigma_err
                        if q3do.ct_zstar_err is not None:
                            contcube['stel_z_err'][i, j, :] \
                                = q3do.zstar_err

            elif q3di.fcncontfit == 'questfit':

                contcube['all_mod'][i, j, q3do.fitran_indx] = \
                    q3do.cont_fit
                contcube['stel_z'][i, j] = q3do.zstar
                if q3do.ct_zstar_err is not None:
                    contcube['stel_z_err'][i, j, :] = q3do.zstar_err
                else:
                    contcube['stel_z_err'][i, j, :] = [0, 0]

            # continuum attenuation
            if q3do.ct_ebv is not None:
                contcube['stel_ebv'][i, j] = q3do.ct_ebv

            # Plot QSO and host only continuum fit
            if q3di.decompose_qso_fit:

                contcube['qso_mod'][i, j, q3do.fitran_indx] = \
                    qsomod.copy()
                contcube['qso_poly_mod'][i, j, q3do.fitran_indx] = \
                    qsomod_polynorm
                contcube['host_mod'][i, j, q3do.fitran_indx] = \
                    hostmod.copy()
                if isinstance(polymod_refit, float):
                    contcube['poly_mod'][i, j, q3do.fitran_indx] = 0.
                else:
                    contcube['poly_mod'][i, j, q3do.fitran_indx] = \
                        polymod_refit.copy()
                contcube['npts'][i, j] = len(q3do.fitran_indx)

                #if 'remove_scattered' in q3di:
                #    contcube['host_mod'][i, j, q3do.fitran_indx']] -= \
                #        polymod_refit

                # Update hostcube.dat to remove tweakcnt mods
                # Data minus (emission line model + QSO model,
                # tweakcnt mods not included in QSO model)

                hostcube['dat'][i, j, q3do.fitran_indx] \
                    = q3do.cont_dat - qsomod_notweak


    if filepresent and ct != 0:
        # Save emission line and continuum dictionaries
        np.savez('{0.outdir}{0.label}'.format(q3di)+'.lin.npz',
                 emlwav=emlwav, emlwaverr=emlwaverr,
                 emlsig=emlsig, emlsigerr=emlsigerr,
                 emlflx=emlflx, emlflxerr=emlflxerr,
                 emlweq=emlweq, emlncomp=emlncomp,
                 ncols=cube.ncols, nrows=cube.nrows)
        np.save('{0.outdir}{0.label}'.format(q3di)+'.cont.npy',
                contcube)

    # Output to fits files -- test
    #from astropy.io import fits
    #hdu = fits.PrimaryHDU(emlflx['ftot']['[OIII]5007'][:,:])
    #hdu.writeto('{[outdir]}{[label]}'.format(q3di, q3di)+'_OIII5007flx.fits')


def cap_range(x1, x2, n):
    a = np.zeros(1, dtype=float)
    interval = (x2 - x1) / (n - 1)
    #    print(interval)
    num = x1
    for i in range(0, n):
        a = np.append(a, num)
        num += interval
    a = a[1:]
    return a


def array_indices(array, index):
    height = len(array[0])
    x = index // height
    y = index % height
    return x, y
