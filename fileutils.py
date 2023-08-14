import os.path


def safeopenwrite(rawfilename, mode):
    '''
    Open a file for writing, without overwritting existing files
    if file already exists, open new file with '-2' or '-X'
    in the end of filename
    '''
    # see if filename exists
    filename = rawfilename

    while os.path.exists(filename):
        filename = _getnewfilename(filename)

    if mode == 'w':
        f = open(filename, mode, newline="")
    else:
        f = open(filename, mode)

    return f

def _getnewfilename(fname):
    pathlist = os.path.split(fname)
    dirname = pathlist[0]
    fnamewext = pathlist[1]
    ext = os.path.splitext(fnamewext)[1]
    fname = os.path.splitext(fnamewext)[0]
    # print('dirname = %s' % dirname)
    # print('ext = %s' % ext)
    # print('fname = %s' % fname)

    # see if the file name ends with -XXX
    copynum = _getcopynumber(fname)
    if copynum and (copynum != 1553):
        # print('copynum=%s' % copynum)
        copynum += 1
        filename = os.path.join(dirname, fname[:len(fname)-len('-%d' % (copynum-1))] + ('-%d' % copynum) + ext)

    else:
        copynum = 2
        filename = fname
        filename = os.path.join(dirname, fname + ('-%d' % copynum) + ext)

    # print('newfilename = %s' % filename)

    return filename

def _getcopynumber(fname):
    '''
    find the copy number
    ex:  file-name-4    -> copy number = 4
    ex:  file-name-4324 -> copy number = 4324
    ex:  file-name      -> copy number = None
    '''
    copynum = None
    # see if there is a dash
    dindex = fname.rfind('-')
    # print('dindex = %s' % dindex)

    if dindex > 0:
        # see if the stuff after the dash is a number
        try:
            copynum = int(fname[dindex+1:])
            pass

        except ValueError:
            # not a number so no copynumber
            copynum = None
            pass

    else:
        # no '-' so no copynumber
        pass

    return copynum

def main(fname):
    f = safeopenwrite(fname, 'w')
    f.write('test!\n')
    f.close()
    pass

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1]))
