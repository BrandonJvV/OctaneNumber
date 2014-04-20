
# coding: utf-8

# In[1]:

get_ipython().magic(u'pylab inline')


# In[2]:

import pandas
import jcamp
import os.path
import glob
from numpy import *
from matplotlib.pyplot import *
from matplotlib import * 


# Read data directory. expanduser is used to expand the ~ symbol in the data.

# In[3]:

import json
config = json.load(open('config.json'))
datadir = os.path.expanduser(config['datadir'])


# In[4]:

spectra = []
for filename in glob.glob(os.path.join(datadir, 'IR Spectra', '*.jdx')):
    d = jcamp.read_jcamp(filename)
    spectra.append(d)


# Where do we have data?

# In[5]:

ranges = []
for d in spectra:
    ranges += [[d['FIRSTX'], +1], [d['LASTX'], -1]]
ranges.sort()
ranges = array(ranges)
plot(ranges[:, 0], cumsum(ranges[:, 1])/len(spectra))
xlabel('Wavenumber')
ylabel('Fraction of spectra with data here')


# Figure out what the common wavenumber range is between all the spectra

# In[6]:

starting_wn = max(d['FIRSTX'] for d in spectra)
ending_wn = min(d['LASTX'] for d in spectra)
print "Wavenumbers between", starting_wn, "and", ending_wn


# In[7]:

delta = 4


# In[8]:

common_numbers = arange(starting_wn, ending_wn+delta, delta)


# Interpolate/resample to those values on the data

# In[9]:

ss = {}
for d in spectra:
    s = pandas.Series(interp(common_numbers, d['XDATA'], d['YDATA']), index=common_numbers)
    ss[d['CAS REGISTRY NO']] = s


# Get these into a dataframe

# In[10]:

df = pandas.DataFrame(ss)
df.index.name = 'Wave number'


# Write the dataframe to a CSV file

# In[11]:

df.to_csv(os.path.join(datadir, 'absorbance_spectra.csv'))


# Normalise to sum of 1...   nf = normalised frame

# In[12]:

areas = [trapz(df[i], array(df.index)) for i in df]
nf = df/areas


# Write to file named "absorbance_spectra_unity"

# In[13]:

nf.to_csv(os.path.join(datadir, 'absorbance_spectra_unity.csv'))


# In[14]:

nf.head()


# PCA transformation on the Zero Mean values - 10 component vector

# In[15]:

means = nf.sub(nf.mean(1), axis=0)
means.plot(legend=False)
gca().invert_xaxis()


# In[15]:




# In[16]:

from sklearn.decomposition import PCA

#pca = PCA(n_components=10)
#X_PCA = pca.fit(nf.transpose()).transform(nf.transpose())
#print "Variance Ratio (10 components): " 
#print (pca.explained_variance_ratio_)


# In[17]:

pca = PCA(n_components=8)
X_PCA = pca.fit(means.transpose()).transform(means.transpose())
print "Variance Ratio (8 Components): "
print (pca.explained_variance_ratio_)


# SCREE PLOT: Determine how many Princpal components are needed

# In[18]:

plot(arange(len(pca.explained_variance_ratio_)), pca.explained_variance_ratio_)
xlabel('Num of Components', size=15)
ylabel('Variance Ratio', size =15)
title('Scree Plot', size=20)
#plt.savefig('Scree.JPEG')


# In[19]:


#old = X_PCA[11]
#old_pl = pca.inverse_transform(old)


# In[20]:

#pyplot.figure()
#gca().invert_xaxis()
#plot(nf.index, old_pl)
#title('Transformed')

#pyplot.figure()
#gca().invert_xaxis()
#plot(nf.index, nf['108-08-7'])
#title("Real")


# In[21]:

pca_d = {}
count = 0
for k in spectra:
    if count < 62:
        pca_d[k['CAS REGISTRY NO']] =  X_PCA[count]
        count = count + 1
    else:
        pca_d[k['CAS REGISTRY NO']] = X_PCA[61]
        
        
pca_df = pandas.DataFrame(pca_d)


##### PCA Data Frame: Each compound has been reduced to 10 coefficients

# In[22]:

pca_df


# Feed a random spectrum and determine its PCA vector

# In[23]:

#a = spectra[0]
#b = spectra[1]

#randSpec = (df[a['CAS REGISTRY NO']] + df[b['CAS REGISTRY NO']])/2.0
#rand_pca = pca.fit_transform(randSpec)


# In[24]:

#print X_PCA[0]
#print X_PCA[1]
#print rand_pca

#randSpec_new = pca.inverse_transform(rand_pca)


# In[25]:

#pyplot.figure()
#plot(df.index, randSpec_new[0])
#title('PCA Inverse')

#pyplot.figure()
#plot(df.index, randSpec)
#title('Original Random Spectrum')


##### >>>>  Therefore, it is possible to fit random spectra and find their PCA inverse

# Mean of the Octane Numbers: Using Only RON numbers...flatCAS in datadir is the updated RON and MON numbers

# In[26]:

ON_df = pandas.DataFrame()
ON = ON_df.from_csv(os.path.join(datadir, 'flatCAS.csv'))
ON.head()


# In[27]:

ON_mean = ON['RON'].mean(1)
ON_bar = ON - ON_mean
ON_bar.head()


##### FIRST LINE OF ACTION: Plot 'C1' against mean removed RON

# In[28]:

x = [];
for CAS in ON_bar.transpose():
    #So as to get the same CAS order as the ON data frame 
    x.append(pca_df[CAS][0])

pyplot.figure(figsize=(8,8))    
scatter(x, ON_bar['RON'])
xlabel('C1', size=15)
ylabel('RON_bar', size=15)
title('C1 vs RON', size=20)
#plt.savefig('C1vsRON.jpeg')


##### SECOND LINE OF ACTION: C1 vs C2 with colorMap

# In[34]:

c1 = [];
c2 = [];
tags = [ON_bar['RON'][i] for i in arange(len(ON_bar))];

for CAS in ON_bar.transpose():
    #So as to get the same CAS order as the ON data frame 
    c1.append(pca_df[CAS][1])
    c2.append(pca_df[CAS][2])  


# In[36]:

#change the color map here...which color scale will be most desirable
colmap = cm.winter 
    
fig, ax = subplots(1,1, figsize=(8,8))
scatter(c1, c2, c=tags, s=100, cmap=colmap)

ax2 = fig.add_axes([1.0, 0.1, 0.06, 0.8])
cb = colorbar.ColorbarBase(ax2, cmap=colmap)

ax.set_xlabel('C2', size=15)
ax.set_ylabel('C3', size=15)
ax.set_title('C2 vs C3, colorMap', size=20)

ax2.set_ylabel('Low RON to high RON %', size=15)

#plt.savefig('C2vsC3map.jpeg')


# In[ ]:



