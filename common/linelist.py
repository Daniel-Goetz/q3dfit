def linelist(inlines=None,linelab=True,waveunit='Angstrom',vacuum=True):
    """
    Generates an astropy Table of lines from the master file linelist_master.tbl
    
    Returns:
    
       An astropy Table of lines with keywords 'name','linelab','lines'
       Example: 'Lyalpha', 'Ly \$\alpha\$', 1215.67d
    
    Parameters:
    
       No required parameters; by default the entire table is read from the 
       linelist_master.tbl and returned
    
    Optional parameters:
    
       inlines: a list of strings to match against the 'name' part of the 
           master list (default is all)
       linelab: boolean variable (True or False) -- whether to return the 
           Tex-friendly labels for the lines (default is True)
       vacuum: boolean variable (True or False) -- whether to return 
           wavelengths in vacuum, default is True (otherwise returns air 
           wavelengths); conversion is equation 3 from Morton et al. 1991
           ApJSS 77 119
       waveunit: a string variable, 'A' or 'micron', default is Angstrom
    
    Examples:
        
        1.
        
        mylist=['Paa', '[SII]103b', 'Paa']
        u=linelist(inlines=mylist)
        
        will produce a table of vacuum wavelengths in Angstroms for three lines
        in the same order as given, and a warning there is a duplicated line 
        in mylist
        
        2.
        
        mylist=['Paa', '[SII]103b', 'junk']
        u=linelist(inlines=mylist,vacuum=False,waveunit='micron',linelab=False)
        
        will produce a table of air wavelengths in micron for two lines, report
        that one line is not in the line list, convert to air wavelengths and 
        to microns and remove the line lables
    """
    from astropy.table import Table, vstack
    import os
    #https://stackoverflow.com/questions/4060221/how-to-reliably-open-a-file-in-the-same-directory-as-a-python-script
    all_lines=Table.read(os.path.dirname(__file__)+'/linelist_master.tbl',format='ipac')
    outlines=all_lines
    # Dave had some checks on whether the master table was complete, in that there
    # is exactly one name per one Tex label per wavelength
    # it would not be crazy to read in this table and check that there are no 
    # empty fields in these key columns...
   
    # a helper function that removes duplicate lines to check for duplicates
    # https://stackoverflow.com/questions/12897374/get-unique-values-from-a-list-in-python
    def uniqlist(inlist):
        outlist=[]
        for x in inlist:
            if x not in outlist:
                outlist.append(x)
        return outlist

    # check if there is an input list of lines, those are the only ones we 
    # are retaining:                               
    if inlines:
        # first of all, let's check to see if any duplicate values in inlines:
        # https://stackoverflow.com/questions/12897374/get-unique-values-from-a-list-in-python
        if (inlines!=uniqlist(inlines)):
            print ('Multiple occurrences of the same lines, proceeding as user requested')
        outlines=Table(names=all_lines.colnames,
                       dtype=[all_lines.dtype[0],all_lines.dtype[1],all_lines.dtype[2]])
        for ind,inline in enumerate(inlines):
            sub_table=all_lines[(all_lines['name']==inline)]
            if (len(sub_table) == 0):
                print ('No line with name ',inline,' was found')
            # this error would only occur if the data table has duplications:    
            if (len(sub_table) > 1):
                print ('Too many lines with name ', inline, ' were found in the database,')
                print ('Returning the first database occurrence')
                sub_table=sub_table[0]
            outlines=vstack([outlines, sub_table])    

    # if the user doesn't want Latex labels, remove them
    if (linelab==False):
        outlines.keep_columns(['name','lines'])
        
    # switch from vacuum to air if requested; this needs to be done on Angstroms
    # so before any unit conversion is attempted
    if ((vacuum!=True) & (vacuum!=False)):
        print ('Incorrect input for vacuum vs air, proceeding with default (vacuum)')
    if (vacuum==False):
        temp=1.e4/outlines['lines']
        outlines['lines']=outlines['lines']/(1.+6.4328e-5+
                2.94981e-2/(146.-temp**2)+2.5540e-4/(41.-temp**2))
        
    # switch to microns if requested. Only Angstrom and microns are recognized 
    if ((waveunit!='Angstrom') & (waveunit!='micron')):
        print ('Wave unit ',waveunit,' not recognized, returning Angstroms')
    if (waveunit=='micron'):
        outlines['lines']=outlines['lines']*1.e-4
        outlines['lines'].unit='micron'
        
    # the healthy outcome is that the number of entries in the outlines
    # is the same as the number of entries in the inlines
    if inlines: 
        if (len(inlines)!=len(outlines)):
            print('Input list size different from output table size, most likely')
            print('because some lines were not found in the database')

    return outlines                                               