#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import shutil
from astropy.io import ascii
from astropy.table import Table, vstack    
from astropy import units as u
from pathlib import Path

"""
Created on Tue Jun 14 15:51:39 2022

"""

def jwstlinez(z, gal, instrument, mode, grat_filt, waveunit = 'micron'):
    
    """
    Creates a table of emission lines expected to be found in a given instrument configuration for JWST. 
    References stored under linelists are .tbl of filenames:
    
    lines_H2
    lines_DSNR_micron   
    lines_TSB
    lines_ref
    
    ADD MORE ONCE PAH COMES OUT
    String inputs are not case sensitive, but must be entered with exact spelling
    
    Parameters
    ----------
    
    z : flt, required
        Galaxy redshift
    gal : str, required
        Galaxy name for filenaming
    instrument : str, required
        JWST instrumnent. Inputs: NIRSpec, MIRI
        Used to grab the right table for each instrument. 
    mode : str, required
        Instrument mode.
        NIRSpec Inputs: IFU, MOS, FSs, BOTS
        MIRI Inputs: MRS
    grat_filt : grating and filter combination for NIRSpec or channel for MIRI
        NIRSpec Inputs: G140M_F0701P, G140M_F1001P, G235M_F1701P, G395M_F2901P,
            G140H_F0701P, G140H_F1001P, G235H_F1701P, G395H_F2901P, Prism_Clear
        MIRI Inputs: Ch1_A, Ch1_B, Ch1_C, Ch2_A, Ch2_B, Ch2_C, Ch3_A, Ch3_B, Ch3_C, Ch4_A, Ch4_B, Ch4_C
    waveunit : str, default='micron'
        Units desired for output tables. 
        Inputs are 'micron' or 'angstrom'
            
    Returns
    --------
    
    lines : astropy table
        An astropy table of emission lines with keywords 'name', 'lines', 
            q'linelab', 'observed'
        Example Row: H2_43_Q6, 2.98412, H$_2$(4-3) Q(6), 4.282212 
        Interanlly, everything is processed in microns, so filename inclues 
            range values in microns. 
        The units of the table can be angstroms or microns, depending on the 
            entered value of waveunit.
        Output table contains comments descring data sources
    
    
    """
    
    
    
    home = str(Path.home())
    inst = instrument.lower()
    md = mode.lower()
    gf = grat_filt.lower()
    wu = waveunit.lower() #test w/o to see if necessary
    
    # filename variable based on instrument configuration
    
    if ((wu!='angstrom') & (wu!='micron')):
        print('Wave unit ',waveunit,' not recognized, proceeding with default, microns\n')
    
    
    #add links to more tables here
    lines_H2 = Table.read(home + '/q3dfit/q3dfit/data/linelists/linelist_H2.tbl',format='ipac')
    lines_DSNR = Table.read(home + '/q3dfit/q3dfit/data/linelists/linelist_DSNR_micron.tbl',format='ipac')
    lines_fine_str = Table.read(home + '/q3dfit/q3dfit/data/linelists/linelist_fine_str.tbl',format='ipac')
    lines_TSB = Table.read(home + '/q3dfit/q3dfit/data/linelists/linelist_TSB.tbl',format='ipac')
    lines_PAH = Table.read(home + '/q3dfit/q3dfit/data/linelists/linelist_PAH.tbl',format='ipac')     
    
    
    if (inst == 'miri' or inst =='nirspec'):
        inst_ref = Table.read('/Users/ryanmccrory/q3dfit/q3dfit/data/jwst_tables/' + instrument + '.tbl',format = 'ipac')
    else:
        print("\n--------------------------")
        print(inst + ' is not a valid instrument input')
        print("--------------------------\n")


    lines = vstack([lines_H2, lines_DSNR, lines_fine_str, lines_TSB, lines_PAH])
    tcol = lines.columns[1]

    # mask to search for row of provided entries
    mask = (inst_ref['mode'] == md) & (inst_ref['grat_filt'] == gf) 
    print('Instrument configuration rest wavelength range:\n')
    print(inst_ref[mask])

    lamb_min = inst_ref[mask]['lamb_min']
    lamb_max = inst_ref[mask]['lamb_max']
    #redshifts the table
    lines_air_z = np.multiply(tcol,z+1)
    #rounds the floats in list CHANGE IF MORE PRECISION NEEDED
    round_lines = lines_air_z.round(decimals = 7) * u.micron
    #adds column to lines table corresponding w/ redshifted wavelengths
    lines['observed'] = round_lines
    
    
    #helper function to identify lines in instrument range
    def inrange(table, key_colnames):
        colnames = [name for name in table.colnames if name  in key_colnames]
        for colname in colnames:
            if np.any(table[colname] < lamb_min) or np.any(table[colname] > lamb_max):
                return False
            return True
    
    
    tg = lines.group_by('observed')
    lines_inrange = tg.groups.filter(inrange)
    
 
    # converting table to desired units
    if (wu=='angstrom'):
        print('angstroms unit selected\n')

        lines_inrange['lines'] = (lines_inrange['lines']*1.e4).round(decimals = 7)
        lines_inrange['lines'].unit = 'angstrom'
        
        lines_inrange['observed'] = (lines_inrange['observed']*1.e4).round(decimals = 7)
        lines_inrange['observed'].unit = 'angstrom'
        
        # filename variable determined by units
        filename = 'lines_' + gal + '_' + str(lamb_min * 1.e4) + '_to_' + str(lamb_max * 1.e4) + \
            '_angstroms_jwst.tbl'
            
    else: 
        # filename for microns default
        filename = 'lines_' + gal + '_' + str(lamb_min) + '_to_' + str(lamb_max) + \
            '_microns_jwst.tbl'
      
    # var used to determine if a list has >0 entries along with printing length
    list_len = len(lines_inrange['lines'])
    
    #comments for each generated table
    lines_inrange.meta['comments'] = \
    ['Tables generated from reference tables created by Nadia Zakamska and Ryan McCrory',
    'All wavelengths are assumed to be in VACUUM',
    '>LINELIST_TSB:',
    '   Data Source 1: Storchi-Bergmann et al. 2009, MNRAS, 394, 1148',
    '   Data Source 2: Glikman et al. 2006, ApJ, 640, 579 (but looked up on NIST)',
    '>LINELIST_H2:',
    '   Data Source 1: JWST H_2 lines between 1 and 2.5 microns from this link:', 
    '   https://github.com/spacetelescope/jdaviz/tree/main/jdaviz/data/linelists',
    '   H2_alt.csv file; one typo corrected (the line marked as 2-9 Q(1) replaced with 2-0 Q(1))',
    '   Data Source 2: ISO H_2 lines from 2.5 microns onwards from this link:', 
    '   https://www.mpe.mpg.de/ir/ISO/linelists, file H2.html',
    '>LINELIST_FINE_STR',
    '   Data Source 1: ISO list of fine structure lines at 2-205 micron', 
    '   https://www.mpe.mpg.de/ir/ISO/linelists/FSlines.html',
    '>LINELIST_DSNR_MICRON:',
    '   Data Sources: line lists by David S.N. Rupke created both in vacuum',
    '   and in air and recomputed on the common vacuum grid using Morton 1991.',
    '   Morton is only accurate above 2000A, so the six lines with air',
    '   wavelengths under 2000A are explicitly fixed based on NIST database.',
    '   A handful of previousy missing Latex labels were added by hand to the',
    '   original two tables before combining.',
    '   Original table converted to microns to align with program standard measurements',
    '>LINELIST_PAH:',
    '   Data Source 1: data from the link',
    '   https://github.com/spacetelescope/jdaviz/blob/main/jdaviz/data/linelists',
    '',]
    
    
    if (list_len == 0):
        print('There are no emission lines in the provided sampling range\n')
        print('Terminating table save...\n')
    else:
        print('There are ' + str(list_len) + ' emission lines visible with this instrument configuration.\n')
        
        # writing and moving the table to the linelists folder
        ascii.write(lines_inrange, filename, format = 'ipac', overwrite=True)
        shutil.move((home + '/q3dfit/q3dfit/'+ filename), (home + '/q3dfit/q3dfit/data/linelists'))

        print('File written as ' + filename, sep='')        
        print('Under the directory : ' + home + '/q3dfit/data/linelists')
                
    