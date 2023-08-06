import os
import csv
from pathlib import Path
import datetime
Path.cwd()
#import pynmea2
from statistics import stdev
now = datetime.datetime.now()
#print("Make sure there is no other File in the path except .nmea file only ")

class GPGSVrec:
    def __init__(self, res):
        print("Global Positioning System Fixed Data\n")
        self.res=res
        d=res.split(',')
        self.nofmsg=d[1]
        self.msgno=d[2]
        self.sinV=d[3]

        self.idch1=d[4]
        self.evch1=d[4]
        self.azch1=d[4]
        self.snrch1=d[4]

        self.idch2=d[5]
        self.evch2=d[5]
        self.azch2=d[5]
        self.snrch2=d[5]

        self.idch3=d[6]
        self.evch3=d[6]
        self.azch3=d[6]
        self.snrch3=d[6]

        self.idch4=d[7]
        self.evch4=d[7]
        self.azch4=d[7]
        self.snrch4=d[7].split('*')[0]
        x=self
        self.print=("Number of Messages1: "+x.nofmsg+" Message Number: "+x.msgno+" Satellites in View: "+x.sinV+
      " Satellite ID Ch1: "+x.idch1+" Elevation (degree) Ch1: "+x.evch1+" Azimuth (degree) ch1: "+x.azch1+" SNR ch1 (dBHz): "+x.snrch1+
      " Satellite ID Ch2: "+x.idch2+" Elevation (degree) Ch2: "+x.evch2+" Azimuth (degree) ch2: "+x.azch2+" SNR ch2 (dBHz): "+x.snrch2+
      " Satellite ID Ch3: "+x.idch3+" Elevation (degree) Ch3: "+x.evch3+" Azimuth (degree) ch3: "+x.azch3+" SNR ch3 (dBHz): "+x.snrch3+
      " Satellite ID Ch4: "+x.idch4+" Elevation (degree) Ch4: "+x.evch4+" Azimuth (degree) ch4: "+x.azch4+" SNR ch4 (dBHz): "+x.snrch4+"\n")

        

    
class GPGGArec:
    def __init__(self, res):
        print("Global Positioning System Fixed Data\n")
        self.res=res
        d=res.split(',')
        self.fix=d[1][0:2]+':'+d[1][2:4]+':'+d[1][4:6]
        self.lat=d[2]
        self.latd=d[3]
        self.long=d[4]
        self.longd=d[5]
        if d[6]=='0':
            self.view='Invalid'
        elif d[6]=='1':
            self.view='GPS fix'
        elif d[6]=='2':
            self.view='DGPS fix'
        elif d[6]=='3':
            self.view='PPS fix'
        elif d[6]=='4':
            self.view='Real Time Kinematic'
        elif d[6]=='5':
            self.view='Float RTK'
        elif d[6]=='6':
            self.view='Estimated'
        elif d[6]=='7':
            self.view='Manual Input mode'
        elif d[6]=='8':
            self.view='Simulation Mode'
        else:
            self.view='NA'
        self.nofsat=d[7] # No of sat
        self.hdop=d[8]
        self.alt=d[9]
        self.altunit=d[10]
        self.geoid=d[11]
        self.geoidunit=d[12]
        self.timeS=d[13]
        self.DGPSid=d[14].split('*')[0]
        x=self
        self.print=("Fix taken at UTC: "+x.fix+" Latitude: "+x.lat+" Latitude Direction: "+x.latd+" Long: "+x.long+" Long Direction: "+x.longd+" Fix Quality: "+x.view+"No of Satellite: "+x.nofsat+" Horizontal dilution of position: "+x.hdop+" Altitude above mean sea level: "+x.alt+" Units of altitude: "+x.altunit+" Height of geoid (mean sea level) above WGS84: "+x.geoid+" units of geoid: "+x.geoidunit+" time in seconds since last DGPS update: "+x.timeS+" DGPS station ID number: "+x.DGPSid+"\n")


class GPZDArec:
    def __init__(self, res):
        self.res=res
        print("SiRF Timing Message\n")
        d=res.split(',')
        self.time=d[1][0:2]+':'+d[1][2:4]+':'+d[1][4:6]
        self.d=d[2]
        self.m=d[3]
        self.y=d[4]
        self.lzh=d[5]
        self.lzm=d[6].split('*')[0]
        x=self
        self.print=("UTC time: "+x.time+" Day: "+x.d+" Month: "+x.m+" Year: "+x.y+" Local zone hour: "+x.lzh+" Local zone minutes: "+x.lzm+"\n")

        





        
class GPGSArec:
    def __init__(self, res):
        print("GPS DOP and active satellites\n")
        self.res=res
        d=res.split(',')
        if d[1]=='A':
            self.mode='Automatic, 3D/2D'
        elif d[1]=='M':
            self.mode='Manual, forced to operate in 2D or 3D'
        else:
            self.mode='Mode Not Identified'
        if d[2]=='1':
            self.view='Fix not available'
        elif d[2]=='2':
            self.view='2D'
        elif d[2]=='3':
            self.view='3D'
        else:
            self.view='NA'
        self.svid=d[3:15] # Space Vehicle SV ID
        self.pdop=d[15]
        self.hdop=d[16]
        self.vdop=d[17].split('*')[0]
        x=self
        self.print=("Mode: "+x.mode+" View: "+x.view+" IDs of SVs used in position fix: "+str(x.svid)+" PDOP (dilution of precision): "+x.pdop+" Horizontal dilution of precision(HDOP): "+x.hdop+" Vertical dilution of precision (VDOP): "+x.vdop+"\n")

        
class GPRMCrec:
    def __init__(self,res):
        print("Recommended minimum specific GPS/Transit data\n")
        self.res=res
        s=res.split(',')
        self.time=s[1][0:2]+':'+s[1][2:4]+':'+s[1][4:]+' UTC'
        if s[2]=='A':
            self.validity="Valid"
        elif s[2]=='V':
            self.validity="InValid"
        self.lat=s[3]#current Latitude
        self.latd=s[4]
        self.lon=s[5]
        self.lond=s[6]
        self.speed=s[7]
        self.tcourse=s[8]
        self.date=s[9][0:2]+'/'+s[9][2:4]+'/'+s[9][4:6]
        self.magVar=s[10]
        self.magVarDir=s[11].split('*')[0]
        x=self
        self.print=("Fix taken at: "+x.time+" Validity: "+x.validity+" Latitude: "+x.lat+" Latitude Direction "+x.latd+" Longitude: "+x.lon+" Longitude Direction: "+x.lond+" Speed in knots: "+x.speed+" Track angle in degrees True: "+x.tcourse+" Date: "+x.date+" Magnetic Variation: "+x.magVar+" Magnetic Variation Direction: "+x.magVarDir+"\n") 


class GPVTGrec:
    def __init__(self,res):
        print("Track made good and ground speed")
        self.res=res
        s=res.split(',')
        self.ttm=s[1]+','+s[2]
        self.mtm=s[3]+','+s[4]
        self.gspeedn=s[5]+','+s[6]
        self.gspeedk=s[7]+','+s[8]
        x=self
        self.print=("True track made good: "+x.ttm+" Magnetic track made good: "+x.mtm+" Ground speed, knots: "+x.gspeedn+" Ground speed, Kilometers per hour: "+x.gspeedk+"\n")

class PVTrec:
        def __init__(self,res):
            #print("Position Velocity Time")
            self.res=res
            s=res.split(',')
            self.si=s[1]
            self.gav=s[2]
            self.gsvflg=s[3]
            self.gtots=s[4]
            self.nav=s[5]
            self.navsvflg=s[6]
            self.navtots=s[7]
            self.pm=s[8]
            self.tow=s[9]
            self.ss=s[10]
            self.x=s[11]
            self.y=s[12]
            self.z=s[13]
            self.xv=s[14]
            self.yv=s[15]
            self.zv=s[16]
            self.td=s[17]
            self.totsp=s[18]
            self.totstrk=s[19]
            self.scl=s[20]
            self.ttffc=s[21]
            x=self
            self.print=("Solution integrity: "+x.si+" GPS almanac validity: "+x.gav+" GPS satellite visibility info available flag: "+x.gsvflg+" GPS total satellite: "+x.gtots+" NavIC almanac validity: "+x.nav+" NavIC satellite visibility info available flag: "+x.navsvflg+" NavIC total satellite: "+x.navtots+" Position mode: "+x.pm+" TOW: "+x.tow+" Sub seconds: "+x.ss+" X: "+x.x+" Y: "+x.y+" Z: "+x.z+" X velocity: "+x.xv+" Y velocity: "+x.yv+" Z velocity: "+x.zv+" 3d speed: "+x.td+" Total satellites used for position: "+x.totsp+" Total satellites tracking: "+x.totstrk+" System Counter latched: "+x.scl+" TTFF count: "+x.ttffc+"\n")
            

def find(res):
    d=res.split(',')
    if len(d[0].split('GP'))>1:
        sel='GP'
        op=d[0].split(sel)[-1]
        return op
    elif len(d[0].split('GI'))>1:
        sel='GI'
        op=d[0].split(sel)[-1]
        return op
    elif len(d[0].split('GN'))>1:
        sel='GN'
        op=d[0].split(sel)[-1]
        return op
    elif d[0]=='PVT':
	    op='PVT'
	    return op
    else:
        return "NaN"
	
    
    
    
class imp:
    def allnmea():
        print(" opSel() , sampleFile()")
        print("x,y,z=devPVT()")
        print("sdev(x,y,z) and readAll() for reading content of nmea file")
        print("Classes used: msg=GPGGArec(res),x=GPGSArec(res),x=GPRMCrec(res),x=GPVTGrec(res), x=GPZDArec(res), x=GPGSVrec(res) \n")
        print("PVT,#$GPGGA,124632.122,5231.537,N,01320.203,E,1,12,1.0,0.0,M,0.0,M,,*6A \n #$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30\n #$GPRMC,124633.122,A,5231.938,N,01324.385,E,2228.2,011.3,020622,000.0,W*48\n #$GPZDA,181813,14,10,2003,00,00*4F\n #$GPVTG,309.62,T, ,M,0.13,N,0.2,K,A*23\n #$GPGSV,2,1,07,07,79,048,42,02,51,062,43,26,36,256,42,27,27,138,42*71")

            
    def opSel():
        res=input("Kindly Enter the Data string: ")
        d=res.split(',')
        y=find(res)
        #y=int(input("Select option of string \n1.GPGGA\n2.GPGSA\n3.GPRMC\n4.GPVTG\n5.GPZDA\nGPGSV\n: "))
        if y=='GGA':
            x=GPGGArec(res)
            print(x.print)
        elif y=='GSA':
            x=GPGSArec(res)
            print(x.print)
        elif y=='RMC':
            x=GPRMCrec(res)
            print(x.print)
        elif y=='VTG':
            x=GPVTGrec(res)
            print(x.print)
        elif y=='ZDA':
            x=GPZDArec(res)
            print(x.print)
        elif y=='GSV':
            x=GPGSVrec(res)
            print(x.print)
        elif y=='PVT':
            x=PVTrec(res)
            print(x.print)
        else:
            print("Data not recognized")
    
class readNmea():
    def __init__(self):
        en_pa = str(input("Kindly Enter path of files Example for Mac: /Users/codar/Desktop/ for Windows 'C:\\Users\\Al\\spam' Else 1 for Default path: "))
        pat = False
        if en_pa == '1':
            en_pa = "/Users/codar/Desktop/Kalpakkam_Interference_Issue/"  # default path
            path = en_pa
            os.chdir(path)
        else:
            #print("Entered else")
            while pat == False:
                #print("Entered while")
                try:
                    #print("Entered try")
                    win_dir = Path(en_pa)
                    win_dir.exists()
                    pat = True
                    os.chdir(en_pa)
                    path = en_pa
                except:
                    pat = False
                    #print("Entered Ezxcept")
                    en_pa = input(" Kindly Enter valid path: ")
                    continue
                
        def RmSpaceConvertFloat(x):
            return float(x.strip())


        def RmSpace(x):
            return x.strip()

        results = []
        # keep only files with extesnion .rdt
        results += [each for each in os.listdir(path) if each.endswith('.nmea')]
        for k in results:
            helloFile = open(path + k)
            helloContent = helloFile.readlines()
            StopCount = len(helloContent)
            helloFile.close()
            #print(helloContent)
            for a in range(0, StopCount - 1):
                res = helloContent[a]
                res1=find(res)
                #self.res=res
                #print(res1)
                if res1=='GGA':
                    print(res)
                    x=GPGGArec(res)
                    print("Fix taken at UTC: "+x.fix+" Latitude: "+x.lat+" Latitude Direction: "+x.latd+" Long: "+x.long+" Long Direction: "+x.longd+" Fix Quality: "+x.view+"No of Satellite: "+x.nofsat+" Horizontal dilution of position: "+x.hdop+" Altitude above mean sea level: "+x.alt+" Units of altitude: "+x.altunit+" Height of geoid (mean sea level) above WGS84: "+x.geoid+" units of geoid: "+x.geoidunit+" time in seconds since last DGPS update: "+x.timeS+" DGPS station ID number: "+x.DGPSid+"\n")
                elif res1=='GSA':
                    print(res)
                    x=GPGSArec(res)
                    print("Mode: "+x.mode+" View: "+x.view+" IDs of SVs used in position fix: "+str(x.svid)+" PDOP (dilution of precision): "+x.pdop+" Horizontal dilution of precision(HDOP): "+x.hdop+" Vertical dilution of precision (VDOP): "+x.vdop+"\n")
                elif res1=='RMC':
                    print(res)
                    x=GPRMCrec(res)
                    print("Fix taken at: "+x.time+" Validity: "+x.validity+" Latitude: "+x.lat+" Latitude Direction "+x.latd+" Longitude: "+x.lon+" Longitude Direction: "+x.lond+" Speed in knots: "+x.speed+" Track angle in degrees True: "+x.tcourse+" Date: "+x.date+" Magnetic Variation: "+x.magVar+" Magnetic Variation Direction: "+x.magVarDir+"\n") 
                elif res1=='VTG':
                    print(res)
                    x=GPVTGrec(res)
                    print("True track made good: "+x.ttm+" Magnetic track made good: "+x.mtm+" Ground speed, knots: "+x.gspeedn+" Ground speed, Kilometers per hour: "+x.gspeedk+"\n")
                elif res1=='ZDA':
                    print(res)
                    x=GPZDArec(res)
                    print("UTC time: "+x.time+" Day: "+x.d+" Month: "+x.m+" Year: "+x.y+" Local zone hour: "+x.lzh+" Local zone minutes: "+x.lzm+"\n")
                elif res1=='GSV':
                    print(res)
                    x=GPGSVrec(res)
                    print("Number of Messages1: "+x.nofmsg+" Message Number: "+x.msgno+" Satellites in View: "+x.sinV+
      " Satellite ID Ch1: "+x.idch1+" Elevation (degree) Ch1: "+x.evch1+" Azimuth (degree) ch1: "+x.azch1+" SNR ch1 (dBHz): "+x.snrch1+
      " Satellite ID Ch2: "+x.idch2+" Elevation (degree) Ch2: "+x.evch2+" Azimuth (degree) ch2: "+x.azch2+" SNR ch2 (dBHz): "+x.snrch2+
      " Satellite ID Ch3: "+x.idch3+" Elevation (degree) Ch3: "+x.evch3+" Azimuth (degree) ch3: "+x.azch3+" SNR ch3 (dBHz): "+x.snrch3+
      " Satellite ID Ch4: "+x.idch4+" Elevation (degree) Ch4: "+x.evch4+" Azimuth (degree) ch4: "+x.azch4+" SNR ch4 (dBHz): "+x.snrch4+"\n")
                elif res1=='PVT':
                    print(res)
                    x=PVTrec(res)
                    print("Solution integrity: "+x.si+" GPS almanac validity: "+x.gav+" GPS satellite visibility info available flag: "+x.gsvflg+" GPS total satellite: "+x.gtots+" NavIC almanac validity: "+x.nav+" NavIC satellite visibility info available flag: "+x.navsvflg+" NavIC total satellite: "+x.navtots+" Position mode: "+x.pm+" TOW: "+x.tow+" Sub seconds: "+x.ss+" X: "+x.x+" Y: "+x.y+" Z: "+x.z+" X velocity: "+x.xv+" Y velocity: "+x.yv+" Z velocity: "+x.zv+" 3d speed: "+x.td+" Total satellites used for position: "+x.totsp+" Total satellites tracking: "+x.totstrk+" System Counter latched: "+x.scl+" TTFF count: "+x.ttffc+"\n")
                else:
                    print("Not Recognized")

def readAll():
    en_pa = str(input("Kindly Enter path of files Example for Mac: /Users/codar/Desktop/ for Windows 'C:\\Users\\Al\\spam' Else 1 for Default path: "))
    pat = False
    if en_pa == '1':
        en_pa = "/Users/codar/Desktop/Kalpakkam_Interference_Issue/"  # default path
        path = en_pa
        os.chdir(path)
    else:
        #print("Entered else")
        while pat == False:
            #print("Entered while")
            try:
                #print("Entered try")
                win_dir = Path(en_pa)
                win_dir.exists()
                pat = True
                os.chdir(en_pa)
                path = en_pa
            except:
                pat = False
                #print("Entered Ezxcept")
                en_pa = input(" Kindly Enter valid path: ")
                continue
            
    def RmSpaceConvertFloat(x):
        return float(x.strip())


    def RmSpace(x):
        return x.strip()

    results = []
    # keep only files with extesnion .rdt
    results += [each for each in os.listdir(path) if each.endswith('.nmea')]
    for k in results:
        helloFile = open(path + k)
        helloContent1 = helloFile.readlines()
        helloFile.close()
        return(helloContent1)


def devPVT():
    x=[]
    y=[]
    z=[]
    data=readAll()
    for a in data:
        if find(a)=='PVT':
            b=PVTrec(a)
            x.append(int(b.x))
            y.append(int(b.y))
            z.append(int(b.z))
    return x,y,z

def sdev(x,y,z):
    return stdev(x),stdev(y),stdev(z)
#$GPGGA,124632.122,5231.537,N,01320.203,E,1,12,1.0,0.0,M,0.0,M,,*6A
#$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30
#$GPRMC,124633.122,A,5231.938,N,01324.385,E,2228.2,011.3,020622,000.0,W*48
#$GPZDA,181813,14,10,2003,00,00*4F
#$GPVTG,309.62,T, ,M,0.13,N,0.2,K,A*23
#$GPGSV,2,1,07,07,79,048,42,02,51,062,43,26,36,256,42,27,27,138,42*71

            
