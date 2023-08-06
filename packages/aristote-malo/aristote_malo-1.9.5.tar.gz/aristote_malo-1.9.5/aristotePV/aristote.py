'''Le logiciel principal de calcul de la prévision de production PV'''
import numpy as np,pytz,pandas as pd,os
from dorianUtils.utilsD import Utils
import plotly.express as px
import time
import math
import json
import datetime
import urllib3
import requests
import pygrib
import sklearn
from sklearn import metrics

class ConfigAristote():
    def __init__(self):
        self.name='configAristote'
        # self.geolocator = Nominatim(user_agent="Dorian",timeout=4)
        # self.tz = tzwhere.tzwhere()
        self.utils=Utils()
        self.appDir  = os.path.dirname(os.path.realpath(__file__))
        self.confFolder = self.appDir +'/confFiles/'

# ==============================================================================
#                               FORMULAS
# ==============================================================================
    def numberDayYear(self,myDate):
        """
        function that determine the number of days in the year.

        :param kind: year
        :type kind: int
        :return: the number of day in a year
        :rtype: int
        """
        myDate=pd.Timestamp(myDate)
        s=myDate.is_leap_year
        if s==True:
            return 366
        if s==False:
            return 365
        #return (pd.Timestamp(str(year))-pd.Timestamp(str(year-1))).days
        # return (pd.Timestamp(str(year+1))-pd.Timestamp(str(year))).days


    def indiceDayD(self,myDate):
        """
        function that determine the number of the day in the year

        :param kind: date
        :type kind: timestamp
        :return: the number of the day in the year
        :rtype: int
        """
        myDate=pd.Timestamp(myDate)
        # firstDay=pd.Timestamp(str(myDate.year)+'-1-1',tz=myDate.tz)
        # return (myDate-firstDay).days
        return myDate.day_of_year

    def irradiance(self,jourJ, nbj):
        """
        return the power flux [W/m²] of the radiation of the sun on a certain day

        :param kind: number of the year, number of days in the year
        :param type: int, int
        :return: the power flux
        :rtype: float
        """
        return 1367*(1+0.0334*np.cos(2*np.pi*(jourJ-94)/nbj))

    def timeEquation(self,jourJ, nbj):
        """
        function that give the result of the time equation that is caused by the difference between the relative cinematics of the sun and the mean sun.


        :param kind: number of the year, number of days in the year
        :param type: int, int
        :return: an offset of time
        :rtype: float
        """
        Temp = 2 * np.pi * (jourJ - 81) / nbj
        return -9.87 * np.sin(2 * Temp) + 7.53 * np.cos(Temp) + 1.5 * np.sin(Temp)

    def solartime(self,heureUTC, longituderad, equationTemps):
        """
        Define the real absolute time, not depending of the timezone

        :param kind: UTC hour, longitude, time equation
        :param type: timestamp, float and float
        :return: the real time
        :rtype: float
        """

        #hv = heureUTC.hour - longituderad * 24 / (2 * np.pi) - equationTemps / 60
        hv = heureUTC.hour + (equationTemps + longituderad*180/np.pi + heureUTC.minute) / 60
        if hv < 0 : hv = hv + 24
        return hv

    def hourAngle(self,solartime):
        """
        Return the angle between the sun beams and the ground at every time of the year.

        :param kind: UTC hour
        :param type: Timestamp
        :return: the time angle
        :rtype: float
        """

        return 0.2618 * (solartime - 12)

    def declination(self,jourJ, nbj):
        """
        Return the decline that allow to take count of the uprising of the sun in the sky during the year

        :param kind: day of the year and number of days in the year
        :param type: int, int
        :return: position of the sun in the sky
        :rtype: float
        """
        return 0.4093 * np.sin(2 * np.pi * (jourJ + 284) / nbj)


    def elevation(self,declination, latituderad, hourAngle):
        """
        give the height of the sun in the sky depending on the decline and the position.

        :param kind: decline, latitude, time angle
        :param type: float, float, float
        :return: the height of the sun in the sky
        :rtype: float
        """
        return np.max([np.arcsin(np.sin(declination) * np.sin(latituderad) + np.cos(declination) * np.cos(latituderad) * np.cos(hourAngle)),0])

    def azimuth(self,dec, h, latituderad, Ah):
        """
        return the angle formed between the sun and the geographical south

        :param kind: decline, height, latitude, Time angle
        :param type: floats
        :return: the azimuthh
        :rtype: float
        """
        return np.arcsin(np.cos(dec)*np.sin(Ah)/np.cos(h))


    def azimuth_v1_wrong(self,declination, elevation, latituderad, hourAngle):
        Temp = np.arccos((-np.sin(declination) * np.cos(latituderad) + np.sin(latituderad) * np.cos(hourAngle) * np.cos(declination)) / np.cos(elevation))
        if hourAngle < 0 : Temp = -Temp
        return -Temp


    def coeffIncidence_v2(self,inclinaison, orientation, azimuth, hauteurAng):
        """
        Return the coeficient that take count of the angle between the solar panels and the sun sunbeams

        :param kind: tilt, orientation, azimuthh, angular height
        :param type: floats
        :return: the coeficient due to the angle
        :rtype: float
        """
        temp = np.sin(inclinaison) * np.sin(orientation) * np.sin(azimuth)
        temp = temp + np.cos(orientation) * np.sin(inclinaison) * np.cos(azimuth)
        temp = (temp + np.cos(inclinaison)) * np.sin(hauteurAng)
        return np.max([temp, 0])
        # return temp

    def coeffIncidence(self,i,o,a,Ah):
            self.utils.printListArgs(i,o,a,Ah)
            return np.sin(Ah)*np.cos(i) + np.sin(a)*np.sin(i)*np.sin(o)*np.cos(Ah) + np.sin(i)*np.cos(Ah)*np.cos(a)*np.cos(o)

    def findFormulaIncidence(self):
        import sympy as sy
        o,a,i,Ah=sy.symbols('o a i Ah')
        M1=sy.Matrix([[sy.cos(o),-sy.sin(o),0],[sy.sin(o),sy.cos(o),0],[0,0,1]])
        Z=sy.Matrix([sy.cos(Ah)*sy.sin(a),sy.cos(Ah)*sy.cos(a),sy.sin(Ah)])
        M2 = sy.Matrix([[1,0,0],[0,sy.cos(i),-sy.sin(i)],[0,sy.sin(i),sy.cos(i)]])
        Zseconde = M2*M1*Z

# ==============================================================================
#                     COMPUTE FROM CONFIGURATION
# ==============================================================================
    def getLongLat(self,address):
        """
        Take the adress of a place and return the longitude and latitude of this place

        :param kind: adress
        :param type: string
        :return: the latitude and the longitude of this place
        :rtype: float and float
        """
        location = self.geolocator.geocode(address)
        return location.latitude,location.longitude

    def declination_fromConf(self,myDate):
        """
        Get the decline of the sun from the configuration (the date)

        :param kind: date
        :param type: Timestamp
        :return: decline
        :rtype: float
        """
        jourJ  = self.indiceDayD(myDate)
        nbj    = self.numberDayYear(myDate.year)
        return self.declination(jourJ, nbj)

    def jourJ_fromConf(self,myDate):
        return self.indiceDayD(myDate)

    def nbj_fromConf(self,myDate):
        return self.numberDayYear(myDate)

    def timeEquation_fromConf(self,myDate):
        jourJ = self.indiceDayD(myDate)
        nbj = self.numberDayYear(myDate)
        return self.timeEquation(jourJ,nbj)


    def solartime_fromConf(self,myDate,longitude,latitude):
        """
        Get the real time from Conf by using the 'heure vraie' function

        :param kind: date, latitude and longitude
        :param type: timestemp, float and float
        :return: the real time
        :rtype: float
        """
        jourJ = self.indiceDayD(myDate)
        nbj = self.numberDayYear(myDate.year)
        equationTemps = self.timeEquation(jourJ, nbj)
        heureUTC     = myDate.tz_convert('UTC')
        longituderad,latituderad = longitude*np.pi/180,latitude*np.pi/180
        return self.solartime(heureUTC, longituderad, equationTemps)

    def hourAngle_fromConf(self,myDate,longitude,latitude):
        """
        Get the time angle from configuration, using the 'hourAngle' function

        :param kind: date and coordinates
        :param type: timestamp ans 2 floats
        :return: the time angle
        :rtype: float
        """
        solartime   = self.solartime_fromConf(myDate,longitude,latitude)
        return self.hourAngle(solartime)

    def getelevation_fromConf(self,myDate,longitude,latitude):
        """
        Get the angular height from configuration,using the 'elevation' function

        :param kind: date and coordinates
        :param type: timestamp and 2 floats
        :return: the height angle
        :rtype: float
        """
        latituderad = latitude*np.pi/180
        declination  = self.declination_fromConf(myDate)
        hourAngle = self.hourAngle_fromConf(myDate,longitude,latitude)
        return self.elevation(declination, latituderad, hourAngle)

    def getazimuth_fromConf(self,myDate,longitude,latitude):
        """
        Get the azimuthh from configuration, using 'azimuth' function

        :param kind: date and coordinates
        :param type: timestamp and 2 floats
        :return: azimuthh
        :rtype: float
        """
        declination  = self.declination_fromConf(myDate)
        hauteurAng = self.getelevation_fromConf(myDate,longitude,latitude)
        latituderad = latitude*np.pi/180
        hourAngle = self.hourAngle_fromConf(myDate,longitude,latitude)
        return self.azimuth(declination, hauteurAng, latituderad, hourAngle)

    def coefIncidence_fromConf(self,myDate,longitude,latitude,inclinaison,orientation):
        """
        Get the incidence coeficient taking count oh the angle between the solar panel and the sun beams from configuration, using the 'coeffIncidence_v2' function

        :param kind: dante, longitude, latitude, tilt and orientation
        :param type: timestamp and floats
        :return: incidencial coeficient
        :rtype: float
        """
        azimuth=self.getazimuth_fromConf(myDate,longitude,latitude)
        hauteurAng = self.getelevation_fromConf(myDate,longitude,latitude)
        return self.coeffIncidence_v2(inclinaison*np.pi/180, orientation*np.pi/180, azimuth, hauteurAng)

    def irradiance_fromConf(self,myDate):
        """
        Return the power flux of the radiation of the sun from configuration using 'irradiance' function

        :param kind: date
        :param type: timestamp
        :return: the power flux
        :rtype: float
        """
        jourJ = self.indiceDayD(myDate)
        nbj = self.numberDayYear(myDate.year)
        return self.irradiance(jourJ, nbj)

    def TheoricalPmax(self,surface,myDate,longitude,latitude,inclinaison,orientation):
        """
        Return the maximal power possible for our configuration taking the received power flux and the incidential coeficient

        :param kind: area, date, longitude, latitude, tilt and orientation
        :param type: int, date_range, float, float, float and float
        :return: the maximal theorical production of solar panels
        :rtype:  list of floats
        """
        E = self.irradiance_fromConf(myDate)
        coeffIncidence_v2 = self.coefIncidence_fromConf(myDate,longitude,latitude,inclinaison,orientation)
        return surface * E * coeffIncidence_v2

    def PV_power(self,surface,myDate,longitude,latitude,inclinaison,orientation,rendement):
        """
        Return the real theorical production of the solar panels, now considering the eficiency of the solar panels too

        :param kind: area, date, longitude, latitude, tilt, orientation and eficiency
        :param type: int, date_range, float, float, float, float and int
        :return: the theorical production of the solar panels
        :rtype: list of floats
        """
        return rendement*self.TheoricalPmax(surface,myDate,longitude,latitude,inclinaison,orientation)

    def PV_theorique_vector(self,date):
        latituderad=self.latitude*np.pi/180
        longituderad=self.longitude*np.pi/180


        df=pd.DataFrame({'time':date,'nbD':365})
        df=df.set_index('time')
        df['nbD']=df['nbD'].mask(df.index.year%4==0,366)

        df['d']=df.index.day_of_year

        inclinaison=self.inclinaison*np.pi/180
        orientation=self.orientation*np.pi/180

        df['Power flux radiation']=1367*(1+0.0334*np.cos(2*np.pi*(df['d']-94)/df['nbD']))

        df['i']=2*np.pi*(df['d']-81)/df['nbD']
        df['Time equation']=-9.87*np.sin(2*df['i'])+7.53*np.cos(df['i'])+1.5*np.sin(df['i'])

        df['heure UTC']=df.index.tz_convert('UTC').hour


        df['solar time']=df['heure UTC'] + ( df['Time equation'] + self.longitude + df.index.minute) / 60

        df['solar time']=df['solar time'].mask(df['solar time']<0,df['solar time']+24)

        df['time angle']=0.2618 * ( df['solar time'] - 12 )

        df['declination']=0.4093 * np.sin( 2 * np.pi * (df['d'] + 284) / df['nbD'] )

        df['elevation']=np.arcsin(np.sin(df['declination'])*np.sin(latituderad)+np.cos(df['declination'])*np.cos(latituderad)*np.cos(df['time angle']))
        df['elevation']=df['elevation'].mask(df['elevation']<0,0)
        df['elevation']=df['elevation']

        df['azimuthh']=np.arcsin(np.cos(df['declination'])*np.sin(df['time angle'])/np.cos(df['elevation']))

        df['temp']=np.sin(inclinaison)*np.sin(orientation)*np.sin(df['azimuthh'])
        df['temp']=df['temp'] + np.cos(orientation)*np.sin(inclinaison)*np.cos(df['azimuthh'])
        df['coef']=(df['temp']+np.cos(inclinaison))*np.sin(df['elevation'])
        df['coef']=df['coef'].mask(df['coef']<0,0)

        df['theorical Pmax']=df['Power flux radiation']*self.surface*df['coef']
        df['production']=df['theorical Pmax']*self.rendement
        df['timestamp']=df.index
        return df


# ==============================================================================
#                               GRAPHICS
# ==============================================================================
    def timespace(self,timeRange,N=100):
        start,end = [pd.Timestamp(k) for k in timeRange]
        t = np.linspace(start.value, end.value, N)
        return pd.to_datetime(t)

    def PV_timeSeries(self,timeRange,surface=165,longitude=5.997526,latitude=45.382238,
                                inclinaison=17,orientation=70,rendement=0.14,freqCalc='60s'):
        try : local_tz = self.tz.tzNameAt(latitude,longitude)
        except : local_tz='Europe/Paris'
        times = pd.date_range(start=timeRange[0],end=timeRange[1], freq=freqCalc,tz=local_tz)
        irradiances = [self.irradiance_fromConf(k) for k in times]
        coeffIncidences = [self.coefIncidence_fromConf(k,longitude,latitude,inclinaison,orientation) for k in times]
        puissanceMaxTh = [self.TheoricalPmax(surface,k,longitude,latitude,inclinaison,orientation)/1000 for k in times]
        puissancesPV = [rendement*k for k in puissanceMaxTh]

        df = pd.DataFrame([times,irradiances,coeffIncidences,puissanceMaxTh,puissancesPV]).transpose()
        df.columns = ['timestamp','irradiance(W/m2)',"coefficient d'incidence",
        'puissance théorique max(kW)','puissance PV (kW)']
        df = df.set_index('timestamp')
        return df

    def check_timeSeries(self,timeRange,longitude=5.997526,latitude=45.382238,
                                inclinaison=17,orientation=70,surface=165,freqCalc='60s'):
        try : local_tz = self.tz.tzNameAt(latitude,longitude)
        except : local_tz='Europe/Paris'
        times = pd.date_range(start=timeRange[0],end=timeRange[1], freq=freqCalc,tz=local_tz)
        timequation=[self.timeEquation_fromConf(k) for k in times]
        declinations = [self.declination_fromConf(k)*180/np.pi for k in times]
        nbj=[self.nbj_fromConf(k) for k in times]
        jourJ=[self.jourJ_fromConf(k) for k in times]
        heures_vrais = [self.solartime_fromConf(k,longitude,latitude) for k in times]
        angles_horaires = [self.hourAngle_fromConf(k,longitude,latitude)*180/np.pi for k in times]
        hauteurs_angulaires = [self.getelevation_fromConf(k,longitude,latitude)*180/np.pi for k in times]
        azimuths = [self.getazimuth_fromConf(k,longitude,latitude)*180/np.pi for k in times]
        coeffIncidences = [self.coefIncidence_fromConf(k,longitude,latitude,inclinaison,orientation) for k in times]
        puissanceMaxTh = [self.TheoricalPmax(surface,k,longitude,latitude,inclinaison,orientation)/1000 for k in times]
        df = pd.DataFrame([times,declinations,timequation,nbj,jourJ,heures_vrais,angles_horaires,hauteurs_angulaires,azimuths]).transpose()
        df.columns = ['timestamp','declination(°)','time equation','nbj','jourJ','heure vraie',
                        'angle horaire(°)','hauteur angulaire(°)','azimuth(°)']
        df = df.set_index('timestamp')
        return df

    def energy_PV_timeSeries(self,timeRange,surface=1.6*1.02,longitude=5.635,latitude=45.456,
                                inclinaison=45,orientation=0,rendement=19.2,period='1d',freqCalc='60s'):

        try : local_tz = self.tz.tzNameAt(latitude,longitude)
        except : local_tz='Europe/Paris'
        times = pd.date_range(start=timeRange[0],end=timeRange[1], freq=freqCalc,tz=local_tz)
        puissanceMaxTh = [self.TheoricalPmax(surface,k,longitude,latitude,inclinaison,orientation)/1000 for k in times]
        puissancesPV = [rendement/100*k for k in puissanceMaxTh]
        df = pd.DataFrame(puissancesPV,index=times)
        df = df.resample(period).sum()*df.index.freq.delta.total_seconds()
        df.columns=['energie produite(kWh)']
        return df

    def plot_energy_timeSeries(self,timeRange,**kwargs):
        import plotly.express as px
        df = self.energy_PV_timeSeries(timeRange,**kwargs)
        fig = px.bar(df,title='énergie produite par les PVs')
        fig.update_layout(yaxis_title='énergie en kWh')
        fig.update_layout(bargap=0.5)

        nbDays=(df.index[-1]-df.index[0]).days
        energieTotale=df.sum()[0]/1000
        txt = " Energie totale produite :  {:.2f} MWh \n Nombres de jours {:.0f}"

        fig.add_annotation(x=0.95, y=0.98,
        xref="x domain", yref="y domain",
        font=dict(
            family="Courier New, monospace",
            size=20,
            color="red"
            ),
        text=txt.format(energieTotale,nbDays),

        showarrow=False)

        return fig

    def vector_PV_timeSeries(self,timerange,inclinaison=17,orientation=70,rendement=0.2,surface=165,latitude=45.3669,longitude=5.98):
        x=pd.date_range(timerange[0],timerange[1],freq='t',tz='UTC')
        return ConfigAristote.PV_theorique_vector(inclinaison,orientation,rendement,surface,latitude,longitude,x)



class PV_SLS(ConfigAristote):
    def __init__(self,longitude,latitude,surface,orientation,inclinaison,rendement):
        """
        Configure the tracker from  ARISTOTE:

        :Parameters:
            longitude[float]
            latitude[float]
            surface[float]
            orientation[float]
            inclinaison[float]
            rendement[float]

        """
        ConfigAristote.__init__(self)
        self.longitude=longitude
        self.latitude=latitude
        self.surface=surface
        self.orientation=orientation
        self.inclinaison=inclinaison
        self.rendement=rendement

    def sls_PV_theorique(self,timestamp):
        '''
        Return the PV power generated with this configuration.

        :Parameters:
            The date and hour you want [Timestamp]

        :return:
            The PV power from configuration for the time given
        '''
        return ConfigAristote.PV_power(self,self.surface,timestamp,self.longitude,self.latitude,self.orientation,self.inclinaison,self.rendement)

    def sls_PV_theorique_vector(self,daterange):
        """
        Generate a DataFrame with the PV production generated by aristote with a vectorial method.

        :Parameters:
            An interval of time you want (first value: beggining, second value: end) [list of string as [YYYY-MM-DD hh:mm]]

        :return:
            DataFrame with PV production from the configuration and with time in index
        """
        df=ConfigAristote.PV_theorique_vector(self.inclinaison,self.orientation,self.rendement,self.surface,self.latitude,self.longitude,daterange)
        return df['production']

    def SLS_test(self,timestamp):
        """
        Allow you to check all the solar parameters calculated by aristote.

        :Parameters:
            The date and hour you want [Timestamp]

        :return:
            A dataframe for the time given with all the solar parameters
        """
        return ConfigAristote.check_timeSeries(self,timestamp,self.longitude,self.latitude,self.inclinaison,self.orientation,freqCalc='60s')


#############################################################################################################################################################################
#############################################################################################################################################################################
#                                                                                                                                                                           #
#                                                                                                                                                                           #
#                                                                   ARISTOTE TRACKER                                                                                        #
#                                                                                                                                                                           #
#                                                                                                                                                                           #
#############################################################################################################################################################################
#############################################################################################################################################################################


class PVtracker():
    def __init__(self,longitude,latitude,surface,orientation,inclinaison,rendement):
        """
        Configure the tracker from  ARISTOTE:

        :Parameters:
            longitude [float]

            latitude [float]

            surface [float]

            orientation [DataFrame with time in index and orientation in values]

            inclinaison [DataFrame with time in index and inclinaison in values]

            rendement [float]

        """
        self.longitude=longitude
        self.latitude=latitude
        self.surface=surface
        self.orientation=orientation
        self.inclinaison=inclinaison
        self.rendement=rendement


    def PVtheoriquetracker(self,daterange,tz,dfinclinaison,dforientation):
        """
        Simulate a PV tracker with dataframe

        :Parameters:
            daterange [list]
                List with the beggining date and the ending date
            timezone [string]
                The timezone has to be indicated as an abreviation like CET or UTC...
        """

        dforientation=dforientation.resample('1t').mean()
        dfinclinaison=dfinclinaison.resample('1t').mean()
        dforientation=dforientation.tz_convert(tz)
        dfinclinaison=dfinclinaison.tz_convert(tz)
        # dfazimuth=[pd.read_pickle('/home/malo/data_tracker/data_tracker/'+k.strftime('%Y-%m-%d')+'/PV00000002-tracker_okwind-TRACKER_ENVIRONMENT_SUN_AZIMUTH-°.pkl') for k in date2]
        # dfelevation=[pd.read_pickle('/home/malo/data_tracker/data_tracker/'+k.strftime('%Y-%m-%d')+'/PV00000002-tracker_okwind-TRACKER_ENVIRONMENT_SUN_ELEVATION-°.pkl') for k in date2]
        # dfazimuth=pd.concat(dfazimuth)
        # dfelevation=pd.concat(dfelevation)
        # dfazimuth=dfazimuth.resample('t').mean()
        # dfelevation=dfelevation.resample('t').mean()
        # dfelevation=dfelevation.tz_convert(tz)
        # dfazimuth=dfazimuth.tz_convert(tz)

        latituderad=self.latitude*np.pi/180
        longituderad=self.longitude*np.pi/180


        df=pd.DataFrame({'time':daterange,'nbD':365})
        df=df.set_index('time')
        df['nbD']=df['nbD'].mask(df.index.year%4==0,366)

        df['d']=df.index.day_of_year
        df['orientation']=dforientation
        df['inclinaison']=dfinclinaison
        df['inclinaison']=np.pi/2-df['inclinaison']*np.pi/180
        df['orientation']=df['orientation']*np.pi/180

        df['Power flux radiation']=1367*(1+0.0334*np.cos(2*np.pi*(df['d']-94)/df['nbD']))

        df['i']=2*np.pi*(df['d']-81)/df['nbD']
        df['Time equation']=-9.87*np.sin(2*df['i'])+7.53*np.cos(df['i'])+1.5*np.sin(df['i'])

        df['heure UTC']=df.index.tz_convert('UTC').hour

        df['solar time']=df['heure UTC'] + ( df['Time equation'] + longituderad + df.index.minute) / 60
        # df['solar time']=df.index.hour - longitude * 24 / 360 -df['Time equation']/60
        df['solar time']=df['solar time'].mask(df['solar time']<0,df['solar time']+24)

        df['time angle']=0.2618 * ( df['solar time'] - 12 )

        df['declination']=0.4093 * np.sin( 2 * np.pi * (df['d'] + 284) / df['nbD'] )

        df['elevation']=np.arcsin(np.sin(df['declination'])*np.sin(latituderad)+np.cos(df['declination'])*np.cos(latituderad)*np.cos(df['time angle']))
        # df['elevation']=dfelevation
        df['elevation']=df['elevation'].mask(df['elevation']<0,0)

        # df['azimuth']=np.arccos((np.sin(df['declination']*np.cos(latituderad)-np.sin(df['declination'])*np.cos(latituderad)*np.cos(df['time angle'])))/np.cos(df['elevation']))

        df['azimuth']=np.arcsin(np.cos(df['declination'])*np.sin(df['time angle'])/np.cos(df['elevation']))

        df['stock']=df['azimuth']
        df['azimuth']=-df['azimuth']
        df['azimuth']=df['azimuth'].mask(df['azimuth'].diff() < 0,np.pi-df['azimuth'])
        df['azimuth']=df['azimuth'].mask(df['azimuth']<0,df['azimuth']+2*np.pi)


        # df['azimuth']=df['azimuth'].mask(df.index.hour<6,df['stock'])
        # df['azimuth']=df['azimuth'].mask(df.index.hour>17,df['stock'])

        # df['temp']=np.sin(df['inclinaison'])*np.sin(df['orientation'])*np.sin(df['azimuth'])
        # df['temp']=df['temp'] + np.cos(df['orientation'])*np.sin(df['inclinaison'])*np.cos(df['azimuth'])
        # df['coef']=(df['temp']+np.cos(df['inclinaison']))*np.sin(df['elevation'])
        df['coef']=np.sin(df['inclinaison']) * np.cos(df['elevation']) * np.cos(df['orientation']-df['azimuth']) + np.cos(df['inclinaison']) * np.sin(df['elevation'])
        df['coef']=df['coef'].mask(df['coef']<0,0)

        df['theorical Pmax']=df['Power flux radiation']*self.surface*df['coef']
        df['production']=df['theorical Pmax']*self.rendement
        df['timestamp']=df.index
        df['azimuth']=df['azimuth']*180/np.pi
        df['elevation']=df['elevation']*180/np.pi
        df['declination']=df['declination']*180/np.pi
        df['time angle']=df['time angle']*180/np.pi

        # df.drop(columns=['temp','i'])
        return df



#############################################################################################################################################################################
#############################################################################################################################################################################
#                                                                                                                                                                           #
#                                                                                                                                                                           #
#                                                                       FORECAST                                                                                            #
#                                                                                                                                                                           #
#                                                                                                                                                                           #
#############################################################################################################################################################################
#############################################################################################################################################################################

class prediction():
    def __init__(self,APItoken):
        """
        Configure the class for the cloud cover prediction

        :Parameters:
            APItoken [string]
                API token you can get on MeteoFrance/AROME model
        """
        self.APItoken=APItoken
        self.path=os.getenv("HOME")+'/DataForecast'
        if os.path.exists(self.path)==False:
            os.mkdir(self.path)
        if os.path.exists(self.path+'/DataPrevision.pkl')==False:
            with open(self.path+"/DataPrevision.pkl", "wb") as f:
                df=pd.DataFrame({'time':[],'lowclouds':[],'mediumclouds':[],'highclouds':[],'call time':[]})
                df=df.set_index('time')
                df.to_pickle(self.path+'/DataPrevision.pkl')
                f.close()


    def forecast(self):
        """
        Function that create and refresh a file containing a DataFrame with the cloud cover forecast datas for in 4 hours.

        :Parameters:
            None
        """
        date1=pd.Timestamp(datetime.datetime.now())
        date=date1
        date1=date1.floor(freq='h')
        date2=date1+pd.Timedelta('4h')
        for i in range(3):
            if date1.hour%3!=0:
                date1=date1-pd.Timedelta('1h')
            if date1.hour%3!=0:
                date1=date1-pd.Timedelta('1h')
            if date1.hour%3!=0:
                date1=date1-pd.Timedelta('1h')


        date1=date1-pd.Timedelta('6h')


        # Example of a Python implementation for a continuous authentication client.
        # It's necessary to :
        # - update APPLICATION_ID
        # - update request_url at the end of the script

        # unique application id : you can find this in the curl's command to generate jwt token or with Base64(consumer-key:consumer-secret) keys application
        APPLICATION_ID = self.APItoken
        # url to obtain acces token
        TOKEN_URL = "https://portail-api.meteofrance.fr/private/nativeAPIs/token"
        urllib3.disable_warnings()

        class Client(object):

            def __init__(self):
                self.session = requests.Session()

            def request(self, method, url, **kwargs):
                # First request will always need to obtain a token first
                if 'Authorization' not in self.session.headers:
                    self.obtain_token()

                # Optimistically attempt to dispatch reqest
                response = self.session.request(method, url, **kwargs)
                if self.token_has_expired(response):
                    # We got an 'Access token expired' response => refresh token
                    self.obtain_token()
                    # Re-dispatch the request that previously failed
                    response = self.session.request(method, url, **kwargs)

                return response

            def token_has_expired(self, response):
                status = response.status_code
                content_type = response.headers['Content-Type']
                if status == 401 and 'application/json' in content_type:
                    if 'expired' in response.headers['WWW-Authenticate']:
                        return True

                return False

            def obtain_token(self):
                # Obtain new token
                data = {'grant_type': 'client_credentials'}
                headers = {'Authorization': 'Basic ' + APPLICATION_ID}
                access_token_response = requests.post(TOKEN_URL, data=data, verify=False, allow_redirects=False, headers=headers)
                token = access_token_response.json()['access_token']
                # Update session with fresh token
                self.session.headers.update({'Authorization': 'Bearer %s' % token})

        def mainlow():
            client = Client()
            # Issue a series of API requests an example. For use this test, you must first subscribe to the arome api with your application
            client.session.headers.update({'Accept': 'application/json'})

            for i in range(1):
                response = client.request('GET', 'https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/GetCoverage?service=WCS&version=2.0.1&coverageid=LOW_CLOUD_COVER__GROUND_OR_WATER_SURFACE___'+date1.strftime('%Y-%m-%dT%H.%M.%SZ')+'&subset=time%28'+date2.strftime('%Y-%m-%dT%H')+'%3A00%3A00Z%29&format=application%2Fwmo-grib', verify=False)
                print(response.status_code)
                # print(json.raw_decode(response.json))
                time.sleep(1)
                return response


        lowdatas=mainlow()
        with open(self.path+"/responselow.grib", "wb") as f:
            f.write(lowdatas.content)
            f.close()
        # if __name__ == '__main__':
            # mainlow()


        def mainmedium():
            client = Client()
            # Issue a series of API requests an example. For use this test, you must first subscribe to the arome api with your application
            client.session.headers.update({'Accept': 'application/json'})

            for i in range(1):
                response = client.request('GET', 'https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/GetCoverage?service=WCS&version=2.0.1&coverageid=MEDIUM_CLOUD_COVER__GROUND_OR_WATER_SURFACE___'+date1.strftime('%Y-%m-%dT%H.%M.%SZ')+'&subset=time%28'+date2.strftime('%Y-%m-%dT%H')+'%3A00%3A00Z%29&format=application%2Fwmo-grib', verify=False)
                print(response.status_code)
                # print(json.raw_decode(response.json))
                time.sleep(1)
                return response


        mediumdatas=mainmedium()
        with open(self.path+"/responsemedium.grib", "wb") as f:
            f.write(mediumdatas.content)
            f.close()


        def mainhigh():
            client = Client()
            # Issue a series of API requests an example. For use this test, you must first subscribe to the arome api with your application
            client.session.headers.update({'Accept': 'application/json'})

            for i in range(1):
                response = client.request('GET', 'https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/GetCoverage?service=WCS&version=2.0.1&coverageid=HIGH_CLOUD_COVER__GROUND_OR_WATER_SURFACE___'+date1.strftime('%Y-%m-%dT%H.%M.%SZ')+'&subset=time%28'+date2.strftime('%Y-%m-%dT%H')+'%3A00%3A00Z%29&format=application%2Fwmo-grib', verify=False)
                print(response.status_code)
                # print(json.raw_decode(response.json))
                time.sleep(1)
                return response


        highdatas=mainhigh()
        with open(self.path+"/responsehigh.grib", "wb") as f:
            f.write(highdatas.content)
            f.close()


        # def pressure():
        #     client = Client()
        #     # Issue a series of API requests an example. For use this test, you must first subscribe to the arome api with your application
        #     client.session.headers.update({'Accept': 'application/json'})
        #
        #     for i in range(1):
        #         response = client.request('GET', 'https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/GetCoverage?service=WCS&version=2.0.1&coverageid=PRESSURE__GROUND_OR_WATER_SURFACE___'+date1.strftime('%Y-%m-%dT%H.%M.%SZ')+'&subset=time%28'+date2.strftime('%Y-%m-%dT%H')+'%3A00%3A00Z%29&format=application%2Fwmo-grib', verify=False)
        #         print(response.status_code)
        #         # print(json.raw_decode(response.json))
        #         time.sleep(1)
        #         return response
        #
        #
        # pressure=pressure()
        # with open(self.path+"/pressure.grib", "wb") as f:
        #     f.write(pressure.content)
        #     f.close()


        grbs=pygrib.open(self.path+'/responsehigh.grib')
        grb=grbs.select(name='High cloud cover')[0]
        data,lat,lon=grb.data(lat1=45,lon1=5.5,lat2=46,lon2=6.5)
        highclouds=data[62][47]

        grbs=pygrib.open(self.path+'/responsemedium.grib')
        grb=grbs.select(name='Medium cloud cover')[0]
        data,lat,lon=grb.data(lat1=45,lon1=5.5,lat2=46,lon2=6.5)
        mediumclouds=data[62][47]

        grbs=pygrib.open(self.path+'/responselow.grib')
        grb=grbs.select(name='Low cloud cover')[0]
        data,lat,lon=grb.data(lat1=45,lon1=5.5,lat2=46,lon2=6.5)
        lowclouds=data[62][47]

        # grbs=pygrib.open(self.path+'/pressure.grib')
        # grb=grbs.select(name='Pressure')[0]
        # data,lat,lon=grb.data(lat1=45,lon1=5.5,lat2=46,lon2=6.5)
        # pressure=data[62][47]

        df=pd.read_pickle(self.path+'/DataPrevision.pkl')
        df.loc[date2]=[lowclouds,mediumclouds,highclouds,date]
        df.to_pickle(self.path+'/DataPrevision.pkl')


#############################################################################################################################################################################
#############################################################################################################################################################################
#                                                                                                                                                                           #
#                                                                                                                                                                           #
#                                                                       CLOUDS MODEL                                                                                        #
#                                                                                                                                                                           #
#                                                                                                                                                                           #
#############################################################################################################################################################################
#############################################################################################################################################################################

class acquisitionPVdata():
    def __init__(self,longitude,latitude,surface,orientation,inclinaison,rendement,city):
        self.longitude=longitude
        self.latitude=latitude
        self.surface=surface
        self.orientation=orientation
        self.inclinaison=inclinaison
        self.rendement=rendement
        self.city=city


    def getdataPV(self,dataPV,freq):
        """
        Get the real PV data for a certain day

        :Parameters:
            dataPV [DataFrame with your PV data and an index composed of timestamps]
                Dataframe with your photovoltaic production, note that the production must be in W
            freq [string as in pandas.date_range]
                the sample frequency

        :return:
            PV data [DataFrame]
        """
        df=dataPV
        df=df.resample(freq).mean()
        return df


    def getdividedPV(self,datapv,datatheoric,f,timezone):
        """
        Function that return a dataframe with real PV data, theorical PV data from Aristote and relative divided PV data.

        :Parameters: Datapv [DataFrame]
                     datatheoric [the theorical PV data (can be generated by aristote)]
                     f [string (frequancy available for date_range)]

        :return: Dataframe with real PV production data, theorical PV production data and relative divided PV for a day.
        """
        df=self.getdataPV(datapv,f)
        pvth=datatheoric.resample(f).mean()
        datapv=datapv.tz_convert(timezone)
        datatheoric=datatheoric.tz_convert(timezone)

        # dftot=df.join(pvth)
        dftot=pd.DataFrame({'time':df.index,'PV reel':df.values,'PV théorique':pvth.values})

        dftot=dftot.set_index('time')
        dftot['PV divisé']=dftot['PV reel']/dftot['PV théorique']
        o=np.ones(len(dftot))
        dftot=dftot.fillna(0)
        dftot['PV divisé']=dftot['PV divisé'][dftot['PV divisé']<=1]
        return dftot

    def getcoord(self):
        """
        This function return the coordinate of a city.

        :Parameters:
            city [string]

        :return:
            latitude [float]
            longitude [float]
        """
        part1="http://api.openweathermap.org/geo/1.0/direct?q="
        part3="&limit=1&appid=79e8bbe89ac67324c6a6cdbf76a450c0"
        urlcity=part1+self.city+part3
        dataloc=rq.get(urlcity)
        dataloc=dataloc.json()[0]
        lat=dataloc['lat']
        lon=dataloc['lon']
        return (lat,lon)

    timezone="Europe/Paris"
    def gettimezone(self):
        """
        This function give the timezone of a city of your choice.

        :Parameters:
            city [string]

        :return:
            the name of the timezone [string]
        """
        r1="http://api.timezonedb.com/v2.1/get-time-zone?key=0R5IBUJZQO01&format=json&by=position&lat="
        r2="&lng="
        lat,lon=getcoord(self.city)
        urltimezone=r1+str(lat)+r2+str(lon)
        datatz=rq.get(urltimezone)
        datatz=datatz.json()
        timezone=datatz['zoneName']
        return timezone

class modelePV():
    def __init__(self,longitude,latitude,surface,orientation,inclinaison,rendement,city):
        self.longitude=longitude
        self.latitude=latitude
        self.surface=surface
        self.orientation=orientation
        self.inclinaison=inclinaison
        self.rendement=rendement
        self.city=city



    def formula(self,datapv,datatheoric,dataclouds,freq):
        p=acquisitionPVdata(self.longitude,self.latitude,self.surface,self.orientation,self.inclinaison,self.rendement,self.city)
        df=p.getdividedPV(datapv,datatheoric,freq,'CET')
        dfclouds=dataclouds.resample(freq).mean()
        dfclouds.name = 'cloud coverage'
        df=df.join(dfclouds)
        df.dropna(inplace=True)
        x=df['cloud coverage'][df.index.hour>8]
        x=x[x.index.hour<18]
        y=df['PV divisé'][df.index.hour>8]
        y=y[y.index.hour<18]
        z=np.polyfit(df['cloud coverage'],df['PV divisé'],2)
        m=np.poly1d(z)
        df['pv divise modele']=m(df['cloud coverage'])*df['PV théorique']
        df['modele 1-x']=(1-df['cloud coverage']/100)*df['PV théorique']
        df['modele theo']=(1-0.75*((df['cloud coverage']/100)**(3.4)))*df['PV théorique']
        return df,m

    def modele(self,datapv,datatheoric,dataclouds,freq):
        """
        This function return the pv depending on the time and with the prediction of the diferent models

        :Parameters:
            None

        :return:
            A fig with real PV and the 3 fits vs timestamps.
        """
        df,f=self.formula(datapv,datatheoric,dataclouds,freq)

        df['modele poly']=df['PV théorique']*(-4.963e-5*df['cloud coverage']**2-0.0009734*df['cloud coverage']+0.8355)
        df['modele theorique']=df['PV théorique']*(1-0.75*(df['cloud coverage']/100)**(3.4))

        r1=sklearn.metrics.r2_score(df['PV reel'],df['modele poly'])
        r2=sklearn.metrics.r2_score(df['PV reel'],df['modele theorique'])
        df=df.drop(columns=['cloud coverage'])
        fig=px.scatter(df,title='Superposition du PV réel et des résultats du modèle prévisionnel appliqué')
        fig.update_traces(mode='markers+lines')

        txt = " Score r2 avec le modele polynomial d ordre 2 :  {:.2f}   \n Score r2 du modele theorique :{:.2f} "

        fig.add_annotation(x=0.95, y=0.98,
        xref="x domain", yref="y domain",
        font=dict(
            family="Courier New, monospace",
            size=20,
            color="black"
            ),
        text=txt.format(r1,r2),
        showarrow=False)
        return fig
