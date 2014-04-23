# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

%pylab inline

# <codecell>

def get_spectra(datadir):
    '''Creates spectrum array from directory 'datadir'.''' 
    spectra = []
    for filename in glob.glob(os.path.join(datadir, 'IR Spectra', '*.jdx')):
        d = jcamp.read_jcamp(filename)
        spectra.append(d)
    return spectra

# <codecell>

def get_ranges(spectra):
    '''Find the range of wavenumbers in (spectra).
    
    Returns [ranges, starting wavenumber, endingwave number]'''
   
    ranges = []
    for d in spectra:
        ranges += [[d['FIRSTX'], +1], [d['LASTX'], -1]]
    ranges.sort()
    ranges = array(ranges)
  
    #Figure out what the common wavenumber range is between all the spectra
    starting_wn = max(d['FIRSTX'] for d in spectra)
    ending_wn = min(d['LASTX'] for d in spectra)
    
    return ranges, starting_wn, ending_wn

range, swn, ewn = get_ranges(spec)

# <codecell>

def spectra_DataFrame(spectra, starting_wn, ending_wn, n):
    '''Resample the data at a set delta wavelength value (n) 
    between the starting wavelength and ending wavelength.'''
   
    delta = n
    
    common_numbers = arange(starting_wn, ending_wn+delta, delta)
    
    #Interpolate/resample to those values on the data
    ss = {}
    for d in spectra:
        s = pandas.Series(interp(common_numbers, d['XDATA'], d['YDATA']), index=common_numbers)
        ss[d['CAS REGISTRY NO']] = s
    
    #Get these into a dataframe
    df = pandas.DataFrame(ss)
    df.index.name = 'Wave number'
    return df

# <codecell>

def normalize(dataFrame):
    '''Normalise the data to an integral of 1.'''
    
    areas = [trapz(dataFrame[i], array(dataFrame.index)) for i in dataFrame]
    nf = dataFrame/areas
    return nf

# <codecell>

def mean_data(dataFrame):
    means = dataFrame.sub(dataFrame.mean(1), axis=0)
    return means

# <codecell>

def pca_data(data, n):
    '''Perform PCA on data for dimension reduction up to (n) components.
    
    Returns PCA components for data and 'pca' function of (n) components'''
    
    from sklearn.decomposition import PCA
    pca = PCA(n_components=n)
    X_PCA = pca.fit(data).transform(data)
    return X_PCA, pca

# <codecell>

def scree_plot(pca):
    '''Return a Scree Plot for the PCA function.'''
    
    plot(arange(1,(len(pca.explained_variance_ratio_))+1), pca.explained_variance_ratio_)
    xlabel('Num of Components')
    ylabel('Variance Ratio')
    title('Scree Plot')

# <codecell>

def pca_dataFrame(X_PCA, spectra):
    '''Returns the PCA scores for data in a DataFrame.'''
    
    pca_d = {}
    count = 0
    for k in spectra:
        if count < len(X_PCA):
            pca_d[k['CAS REGISTRY NO']] =  X_PCA[count]
            count = count + 1
        else:
            pca_d[k['CAS REGISTRY NO']] = X_PCA[len(X_PCA)-1]
            
            
    pca_df = pandas.DataFrame(pca_d)
    pca_df.index = arange(1,len(X_PCA[0])+1)
    pca_df.index.name = 'Score'
    return pca_df

