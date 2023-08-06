import numpy
import xarray
import matplotlib.pyplot as plt

class objearth():
    def __init__(self):
        pass
    @staticmethod
    def montage(img1,img2):
        plt.figure(figsize=(15,15))
        plt.subplot(121),plt.imshow(img1, cmap = 'gray')
        plt.title('Image 1'), plt.xticks([]), plt.yticks([])
        plt.subplot(122),plt.imshow(img2, cmap = 'viridis')
        plt.title('Image 2'), plt.xticks([]), plt.yticks([])
        plt.show()
    @staticmethod
    def falsecolor(Dataset1,Dataset2,Dataset3,bright=10):
        BAND1    = xarray.where(Dataset1==-9999,numpy.nan,Dataset1)
        band1    = BAND1.to_numpy()/10000*bright
        BAND2    = xarray.where(Dataset2==-9999,numpy.nan,Dataset2)
        band2    = BAND2.to_numpy()/10000*bright
        BAND3    = xarray.where(Dataset3==-9999,numpy.nan,Dataset3)
        band3    = BAND3.to_numpy()/10000*bright
        product  = numpy.stack([band1,band2,band3],axis=2)
        return product
    @staticmethod
    def truecolor(Dataset,bright=10):
        RED    = xarray.where(Dataset.red==-9999,numpy.nan,Dataset.red)
        red    = RED.to_numpy()/10000*bright
        BLUE   = xarray.where(Dataset.blue==-9999,numpy.nan,Dataset.blue)
        blue   = BLUE.to_numpy()/10000*bright
        GREEN  = xarray.where(Dataset.green==-9999,numpy.nan,Dataset.green)
        green  = GREEN.to_numpy()/10000*bright
        rgb    = numpy.stack([red,green,blue],axis=2)
        return rgb
    def clearcloud(self,Dataset0,Dataset1):
        self.Dataset0 = Dataset0
        self.Dataset1 = Dataset1
        pixel0 = self.Dataset0.pixel_qa
        mask1 = xarray.where(pixel0==352,1,0)    
        mask2 = xarray.where(pixel0==480,1,0)
        mask3 = xarray.where(pixel0==944,1,0)
        sum = mask1+mask2+mask3
        mask0 = xarray.where(sum.data>0,1,0)
        blue        = xarray.where(mask0,self.Dataset1.blue,self.Dataset0.blue)
        green       = xarray.where(mask0,self.Dataset1.green,self.Dataset0.green)
        red         = xarray.where(mask0,self.Dataset1.red,self.Dataset0.red)
        nir         = xarray.where(mask0,self.Dataset1.nir,self.Dataset0.nir)
        pixel_qa    = xarray.where(mask0,self.Dataset1.pixel_qa,self.Dataset0.pixel_qa)
        # Create DataArray
        return xarray.merge([blue,green,red,nir,pixel_qa])
    def plotshow(self,DataArray,lst=True):
        self.DataArray = DataArray
        self.lst = lst
        if type(self.DataArray) == xarray.core.dataarray.DataArray:
            if self.lst==True:
                ymax = 0 ; ymin = self.DataArray.shape[0]
                xmin = 0 ; xmax = self.DataArray.shape[1] 
            else:
                ymax = self.lst[0] ; ymin = self.lst[1]
                xmin = self.lst[2] ; xmax = self.lst[3]
            lon  =  self.DataArray.longitude.to_numpy()[xmin:xmax]
            lon0 =  lon[0] ; lon1 =  lon[-1]
            lat  =  self.DataArray.latitude.to_numpy()[ymax:ymin]
            lat0 = -lat[-1] ; lat1 = -lat[0]
            def longitude(lon):
                return [lon0,lon1]
            def latitude(lat):
                return [lat0,lat1]
            def axis(x=0):
                return x
            fig,ax = plt.subplots(constrained_layout=True)
            fig.set_size_inches(7,7)
            ax.set_xlabel('x axis size')
            ax.set_ylabel('y axis size')
            ax.imshow(self.DataArray[ymax:ymin,xmin:xmax],extent=[xmin,xmax,ymin,ymax])
            secax_x = ax.secondary_xaxis('top',functions=(longitude,axis))
            secax_x.set_xlabel('longitude')
            secax_x = ax.secondary_xaxis('top',functions=(longitude,axis))
            secax_x.set_xlabel('longitude')
            secax_y = ax.secondary_yaxis('right',functions=(latitude,axis))
            secax_y.set_ylabel('latitute')
            plt.grid(color='w', linestyle='-', linewidth=0.15)
            plt.show()
        elif type(self.DataArray) == numpy.ndarray:
            if self.lst==True:
                ymax = 0 ; ymin = self.DataArray.shape[0]
                xmin = 0 ; xmax = self.DataArray.shape[1]
            else:
                ymax = self.lst[0] ; ymin = self.lst[1]
                xmin = self.lst[2] ; xmax = self.lst[3]
            plt.figure(figsize=(8,8))
            plt.imshow(self.DataArray[ymax:ymin,xmin:xmax],extent=[xmin,xmax,ymin,ymax])
            plt.xlabel("x axis size")
            plt.ylabel("y axis size")
            plt.grid(color='w', linestyle='-', linewidth=0.15)
            plt.show()

        else:
            print("Nonetype :",type(self.DataArray))
    def percentcloud(self,Dataset):
        self.Dataset = Dataset
        FashCloud = [352,480,944]
        dstest    = self.Dataset.pixel_qa
        dsnew     = xarray.where(dstest == FashCloud[0],numpy.nan,dstest)
        dsnew     = xarray.where(dsnew  == FashCloud[1],numpy.nan,dsnew)
        dsnew     = xarray.where(dsnew  == FashCloud[2],numpy.nan,dsnew)
        Cpixel    = (numpy.isnan(dsnew.to_numpy())).sum()
        Allpixel  = int(self.Dataset.pixel_qa.count())
        Cloudpercent = (Cpixel/Allpixel)*100
        print("Percent Cloud : %.4f"%Cloudpercent,"%")
    def NDVI(self,DataArray):
        """Normalized Difference vegetation Index"""
        self.DataArray = DataArray
        red = xarray.where(self.DataArray.red==-9999,numpy.nan,self.DataArray.red)
        nir = xarray.where(self.DataArray.nir==-9999,numpy.nan,self.DataArray.nir)
        ndvi1 = (nir-red)/(nir+red).to_numpy()
        ndvi3 = numpy.clip(ndvi1,-1,1)
        im_ratio = ndvi3.shape[1]/ndvi3.shape[0]
        plt.figure(figsize=(8,8))
        plt.xticks([]), plt.yticks([])
        plt.imshow(ndvi3,cmap='viridis')
        plt.clim(-1,1)
        plt.colorbar(orientation="vertical",fraction=0.0378*im_ratio)
        plt.show()
        return ndvi3
    def NDMI(self,DataArray):
        """Normalized Difference Moisture Index"""
        self.DataArray = DataArray
        swir = xarray.where(self.DataArray.swir1==-9999,numpy.nan,self.DataArray.swir1)
        nir = xarray.where(self.DataArray.nir==-9999,numpy.nan,self.DataArray.nir)
        ndmi1 = (nir-swir)/(nir+swir).to_numpy()
        ndmi3 = numpy.clip(ndmi1,-1,1)
        im_ratio = ndmi3.shape[1]/ndmi3.shape[0]
        plt.figure(figsize=(8,8))
        plt.xticks([]), plt.yticks([])
        plt.imshow(ndmi3,cmap='viridis')
        plt.clim(-1,1)
        plt.colorbar(orientation="vertical",fraction=0.0378*im_ratio)
        plt.show()
        return ndmi3
    def BSI(self,DataArray):
        """Bare Soil Index"""
        self.DataArray = DataArray
        green = xarray.where(self.DataArray.green==-9999,numpy.nan,self.DataArray.green)
        nir = xarray.where(self.DataArray.nir==-9999,numpy.nan,self.DataArray.nir)
        bsi1 = (nir+green)/(green-nir).to_numpy()
        bsi3 = numpy.clip(bsi1,-1,1)
        im_ratio = bsi3.shape[1]/bsi3.shape[0]
        plt.figure(figsize=(8,8))
        plt.xticks([]), plt.yticks([])
        plt.imshow(bsi3,cmap='viridis')
        plt.clim(-1,1)
        plt.colorbar(orientation="vertical",fraction=0.0378*im_ratio)
        plt.show()
        return bsi3
    def EVI(self,DataArray):
        """Enhanced Vegetation Index"""
        self.DataArray = DataArray
        red = xarray.where(self.DataArray.red==-9999,numpy.nan,self.DataArray.red)
        blue = xarray.where(self.DataArray.blue==-9999,numpy.nan,self.DataArray.blue)
        nir = xarray.where(self.DataArray.nir==-9999,numpy.nan,self.DataArray.nir)
        evi1 = (nir-red)/(nir+6*red-7.5*blue+1).to_numpy()
        evi3 = numpy.clip(evi1,-1,1)
        im_ratio = evi3.shape[1]/evi3.shape[0]
        plt.figure(figsize=(8,8))
        plt.xticks([]), plt.yticks([])
        plt.imshow(evi3,cmap='viridis')
        plt.clim(-1,1)
        plt.colorbar(orientation="vertical",fraction=0.0378*im_ratio)
        plt.show()
        return evi3
    def NDWI(self,DataArray):
        """Normalized Difference Water Index"""
        self.DataArray = DataArray
        swir = xarray.where(self.DataArray.swir1==-9999,numpy.nan,self.DataArray.swir1)
        nir = xarray.where(self.DataArray.nir==-9999,numpy.nan,self.DataArray.nir)
        ndwi1 = (nir-swir)/(nir+swir).to_numpy()
        ndwi3 = numpy.clip(ndwi1,-1,1)
        im_ratio = ndwi3.shape[1]/ndwi3.shape[0]
        plt.figure(figsize=(8,8))
        plt.xticks([]), plt.yticks([])
        plt.imshow(ndwi3,cmap='viridis')
        plt.clim(-1,1)
        plt.colorbar(orientation="vertical",fraction=0.0378*im_ratio)
        plt.show()
        return ndwi3
    def NMDI(self,DataArray):
        """Normalized Multi-Band Drought Index"""
        self.DataArray = DataArray
        swir1 = xarray.where(self.DataArray.swir1==-9999,numpy.nan,self.DataArray.swir1)
        swir2 = xarray.where(self.DataArray.swir2==-9999,numpy.nan,self.DataArray.swir2)
        nir   = xarray.where(self.DataArray.nir==-9999,numpy.nan,self.DataArray.nir)
        nmdi1 = (nir-(swir1-swir2))/(nir-(swir1+swir2)).to_numpy()
        nmdi3 = numpy.clip(nmdi1,-1,1)
        im_ratio = nmdi3.shape[1]/nmdi3.shape[0]
        plt.figure(figsize=(8,8))
        plt.xticks([]), plt.yticks([])
        plt.imshow(nmdi3,cmap='viridis')
        plt.clim(-1,1)
        plt.colorbar(orientation="vertical",fraction=0.0378*im_ratio)
        plt.show()
        return nmdi3
    def NDDI(self,DataArray):
        """Normalized Difference Drought Index"""
        self.DataArray = DataArray
        red = xarray.where(self.DataArray.red==-9999,numpy.nan,self.DataArray.red)
        nir = xarray.where(self.DataArray.nir==-9999,numpy.nan,self.DataArray.nir)
        swir = xarray.where(self.DataArray.swir1==-9999,numpy.nan,self.DataArray.swir1)
        ndvi = (nir-red)/(nir+red)
        ndwi = (nir-swir)/(nir+swir)       
        nddi1 = (ndvi-ndwi)/(ndvi+ndwi).to_numpy() 
        nddi3 = numpy.clip(nddi1,-1,1)
        im_ratio = nddi3.shape[1]/nddi3.shape[0]
        plt.figure(figsize=(8,8))
        plt.xticks([]), plt.yticks([])
        plt.imshow(nddi3,cmap='viridis')
        plt.clim(-1,1)
        plt.colorbar(orientation="vertical",fraction=0.0378*im_ratio)
        plt.show()
        return nddi3
