from pickletools import read_unicodestring1
import traceback
from math import atan, degrees

import cv2
from PIL import Image

from EDlogger import logger
import Image_Templates
import Screen
import Screen_Regions
from EDJournal import *
from EDKeys import *
from EDafk_combat import AFK_Combat
from Overlay import *
from Voice import *


"""
File:EDAP.py    EDAutopilot

Description:

Note:
Much of this taken from EDAutopilot on github, turned into a class and enhanced
see: https://github.com/skai2/EDAutopilot

Author: sumzer0@yahoo.com
"""

# Exception class used to unroll the call tree to to stop execution
class  EDAP_Interrupt(Exception):
    pass



class EDAutopilot:

    def __init__(self, cb, doThread=True):

        self.vce = Voice()
        self.vce.set_on()
        self.vce.say("Welcome to Autopilot")

        self.overlay = Overlay("")

        self.fsd_assist_enabled = False
        self.sc_assist_enabled = False
        self.fss_scan_enabled = False
        self.afk_combat_assist_enabled = False

        self.scr    = Screen.Screen()
        self.templ  = Image_Templates.Image_Templates(self.scr.scaleX, self.scr.scaleY)
        self.scrReg = Screen_Regions.Screen_Regions(self.scr, self.templ)
        self.jn     = EDJournal()
        self.keys   = EDKeys()
        self.afk_combat = AFK_Combat(self.keys, self.jn, self.vce)

        # rate as ship dependent.   Can be found on the outfitting page for the ship.  However, it looks like supercruise
        # has worse performance for these rates
        # see:  https://forums.frontier.co.uk/threads/supercruise-handling-of-ships.396845/
        #
        # If you find that you are overshoot in pitch or roll, need to adjust these numbers.
        # Algorithm will roll the vehicle for the nav point to be north or south and then pitch to get the nave point
        # to center
        self.yawrate   = 8.0 
        self.rollrate  = 80.0  
        self.pitchrate = 33.0 

        self.jump_cnt   = 0
        self.refuel_cnt = 0

        self.ap_ckb = cb
        
        # debug window
        self.cv_view = False
        self.cv_view_x = 10
        self.cv_view_y = 10

        #start the engine thread
        self.terminate = False
        if doThread == True:
            self.ap_thread = kthread.KThread(target = self.engine_loop, name = "EDAutopilot")
            self.ap_thread.start()
  
    def draw_match_rect(self, img, pt1, pt2, color, thick):
        wid = pt2[0] - pt1[0]
        hgt = pt2[1] - pt1[1]

        if wid < 20:
            #cv2.rectangle(screen, pt, (pt[0] + compass_width, pt[1] + compass_height),  (0,0,255), 2)
            cv2.rectangle(img, pt1, pt2, color, thick)
        else:
            len_wid = wid / 5
            len_hgt = hgt / 5
            half_wid = wid/ 2
            half_hgt = hgt/ 2
            tic_len = thick-1
            # top
            cv2.line(img, (int(pt1[0]),             int(pt1[1])), (int(pt1[0]+len_wid),      int(pt1[1])), color, thick)
            cv2.line(img, (int(pt1[0]+(2*len_wid)), int(pt1[1])), (int(pt1[0]+(3*len_wid)),  int(pt1[1])), color, 1)
            cv2.line(img, (int(pt1[0]+(4*len_wid)), int(pt1[1])), (int(pt2[0]),              int(pt1[1])), color, thick)
            # top tic
            cv2.line(img, (int(pt1[0]+half_wid),    int(pt1[1])), (int(pt1[0]+half_wid),     int(pt1[1])-tic_len), color, thick)
            # bot
            cv2.line(img, (int(pt1[0]),             int(pt2[1])), (int(pt1[0]+len_wid),      int(pt2[1])), color, thick)
            cv2.line(img, (int(pt1[0]+(2*len_wid)), int(pt2[1])), (int(pt1[0]+(3*len_wid)),  int(pt2[1])), color, 1)
            cv2.line(img, (int(pt1[0]+(4*len_wid)), int(pt2[1])), (int(pt2[0]),              int(pt2[1])), color, thick)
            # bot tic
            cv2.line(img, (int(pt1[0]+half_wid),    int(pt2[1])), (int(pt1[0]+half_wid),     int(pt2[1])+tic_len), color, thick)
            # left
            cv2.line(img, (int(pt1[0]),  int(pt1[1])),             (int(pt1[0]),  int(pt1[1]+len_hgt)),    color, thick)
            cv2.line(img, (int(pt1[0]),  int(pt1[1]+(2*len_hgt))), (int(pt1[0]),  int(pt1[1]+(3*len_hgt))), color, 1)
            cv2.line(img, (int(pt1[0]),  int(pt1[1]+(4*len_hgt))), (int(pt1[0]),  int(pt2[1])),            color, thick)
            # left tic
            cv2.line(img, (int(pt1[0]),    int(pt1[1]+half_hgt)), (int(pt1[0]-tic_len),   int(pt1[1]+half_hgt)), color, thick)
            # right
            cv2.line(img, (int(pt2[0]),  int(pt1[1])),             (int(pt2[0]),  int(pt1[1]+len_hgt)),    color, thick)
            cv2.line(img, (int(pt2[0]),  int(pt1[1]+(2*len_hgt))), (int(pt2[0]),  int(pt1[1]+(3*len_hgt))), color, 1)
            cv2.line(img, (int(pt2[0]),  int(pt1[1]+(4*len_hgt))), (int(pt2[0]),  int(pt2[1])),            color, thick)
            # right tic
            cv2.line(img, (int(pt2[0]),    int(pt1[1]+half_hgt)), (int(pt2[0]+tic_len),   int(pt1[1]+half_hgt)), color, thick)


    # check to see if the compass is on the screen
    def have_destination(self, scr_reg):
        icompass_image, (minVal, maxVal, minLoc, maxLoc), match  = scr_reg.match_template_in_region('compass', 'compass')
        
        logger.debug("has_destination:"+str(maxVal))

        # need > 50% in the match to say we do have a destination
        if maxVal < 0.50:
            return False
        else:
            return True

    # determine the x,y offset from center of the compass of the nav point
    def get_nav_offset(self, scr_reg):

        icompass_image, (minVal, maxVal, minLoc, maxLoc), match  = scr_reg.match_template_in_region('compass', 'compass')
        pt = maxLoc    
    
        # get wid/hgt of templates  
        c_wid = scr_reg.templates.template['compass']['width']
        c_hgt = scr_reg.templates.template['compass']['height']
        wid = scr_reg.templates.template['navpoint']['width']
        hgt = scr_reg.templates.template['navpoint']['height']

        # cut out the compass from the region          
        pad = 5
        compass_image = icompass_image[abs(pt[1]-pad) : pt[1]+c_hgt+pad, abs(pt[0]-pad) : pt[0]+c_wid+pad].copy()
        
        # find the nav point within the compass box
        navpt_image, (n_minVal, n_maxVal, n_minLoc, n_maxLoc), match  = scr_reg.match_template_in_image(compass_image, 'navpoint')   
        n_pt = n_maxLoc

        if self.cv_view:
            self.draw_match_rect(icompass_image, pt, (pt[0] + c_wid, pt[1] + c_hgt), (255,255,255), 2)                                   
            #self.draw_match_rect(compass_image, n_pt, (n_pt[0] + wid, n_pt[1] + hgt), (255,255,255), 2)   
            self.draw_match_rect(icompass_image, (pt[0]+n_pt[0]-pad, pt[1]+n_pt[1]-pad), (pt[0]+n_pt[0] + wid-pad, pt[1]+n_pt[1] + hgt-pad), (255,255,255), 1)   

            #   dim = (int(destination_width/3), int(destination_height/3))

            #   img = cv2.resize(dst_image, dim, interpolation =cv2.INTER_AREA)   
            cv2.putText(icompass_image, f'{n_maxVal:5.2f} >0.8', (1, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow('compass', icompass_image)
            #cv2.imshow('nav', navpt_image)
            cv2.moveWindow('compass', self.cv_view_x, self.cv_view_y) 
            #cv2.moveWindow('nav', self.cv_view_x, self.cv_view_y) 
            cv2.waitKey(10)

        # must be > 0.80 to have solid hit, otherwise we are facing wrong way (empty circle)
        if n_maxVal < 0.80:
            result = None    
        else:
            final_x = ((n_pt[0] + ((1/2)*wid)) - ((1/2)*c_wid)) -5.5
            final_y = (((1/2)*c_hgt) - (n_pt[1] + ((1/2)*hgt))) +6.5
            logger.debug(("maxVal="+str(n_maxVal)+" x:"+str(final_x)+" y:"+str(final_y)))    
            result = {'x':final_x, 'y':final_y}

        return result


    # Go into FSS, check to see if we have a signal waveform in the Earth, Water or Ammonia zone
    #  if so, announce finding and log the type of world found
    def fss_detect_elw(self, scr_reg):

        #open fss
        self.keys.send('SetSpeedZero')
        sleep(0.1)
        self.keys.send('ExplorationFSSEnter')
        sleep(2.5)
        
        # look for a circle or signal in this region
        elw_image, (minVal, maxVal, minLoc, maxLoc), match  = scr_reg.match_template_in_region('fss', 'elw')
        elw_sig_image, (minVal1, maxVal1, minLoc1, maxLoc1), match  = scr_reg.match_template_in_image(elw_image, 'elw_sig')
        
        # dvide the region in thirds.  Earth, then Water, then Ammonio
        wid_div3 = scr_reg.reg['fss']['width'] / 3

        # Exit out of FSS 
        self.keys.send('ExplorationFSSQuit')

        # Uncomment this to show on the ED Window where the region is define.  Must run this file as an App, so uncomment out 
        # the main at the bottom of file
        #self.overlay.overlay_rect('fss', (scr_reg.reg['fss']['rect'][0], scr_reg.reg['fss']['rect'][1]),
        #                (scr_reg.reg['fss']['rect'][2],  scr_reg.reg['fss']['rect'][3]), (120, 255, 0),2)    
        #self.overlay.overlay_paint()           
     
        if self.cv_view:
            self.draw_match_rect(elw_image, maxLoc, (maxLoc[0]+15,maxLoc[1]+15), (255,255,255), 1) 
            self.draw_match_rect(elw_image, maxLoc1, (maxLoc1[0]+15,maxLoc1[1]+25), (255,255,55), 1)  
            cv2.putText(elw_image, f'{maxVal:5.2f}> .60', (1, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow('fss', elw_image)
            cv2.moveWindow('fss', self.cv_view_x,self.cv_view_y) 
            cv2.waitKey(10)

        logger.info("in elw detector:{0:6.2f} ".format(maxVal)+ " sig:{0:6.2f}".format(maxVal1))

        # check if the circle or the signal meets probability number, if so, determine which type by its region
        if (maxVal > 0.65 or (maxVal1 > 0.60 and maxLoc1[1] < 30) ):
            if maxLoc1[0] < wid_div3:
                sstr = "Earth"
            elif maxLoc1[0] > (wid_div3*2):
                sstr = "Water"
            else:
                sstr = "Ammonia"
            # log the entry into the elw.txt file
            f = open("elw.txt", 'a')
            f.write(self.jn.ship_state()["location"]+"  %(dot,sig): {0:6.2f}, {1:6.2f} ".format(maxVal, maxVal1)+sstr+" date: "+str(datetime.now())+str("\n"))
            f.close
            self.vce.say(sstr+ " like world discovered ")
            logger.info(sstr+" world at: "+str(self.jn.ship_state()["location"]))

        self.keys.send('SetSpeed50')  
        sleep(1)

        return


    # Determine how far off we are from the destination being in the middle of the screen (in this case the specified region
    def get_destination_offset(self, scr_reg):
        dst_image, (minVal, maxVal, minLoc, maxLoc), match  = scr_reg.match_template_in_region('target', 'target')
    
        pt = maxLoc
                
        destination_width  = scr_reg.reg['target']['width']
        destination_height = scr_reg.reg['target']['height']
        
        width  = scr_reg.templates.template['target']['width']
        height = scr_reg.templates.template['target']['height']

        # need some fug numbers since our template is not symetric to determine center
        final_x = ((pt[0] + ((1/2)*width)) - ((1/2)*destination_width)) - 5
        final_y = (((1/2)*destination_height) - (pt[1] + ((1/2)*height))) + 19
        
    #  print("get dest, final:" + str(final_x)+ " "+str(final_y))
    #  print(destination_width, destination_height, width, height)
    #  print(maxLoc)
    
        if self.cv_view:
            try:
                self.draw_match_rect(dst_image, pt, (pt[0] + width, pt[1] + height), (255,255,255), 2)
                dim = (int(destination_width/3), int(destination_height/3))

                img = cv2.resize(dst_image, dim, interpolation =cv2.INTER_AREA)
                cv2.putText(img, f'{maxVal:5.2f} >.55', (1, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.imshow('target', img)
                #cv2.imshow('tt', scr_reg.templates.template['target']['image'])
                cv2.moveWindow('target', self.cv_view_x,self.cv_view_y+400)
            except Exception as e:
                print("exception in getdest: "+str(e))
            cv2.waitKey(10)

    #   print (maxVal)
        # must be > 0.55 to have solid hit, otherwise we are facing wrong way (empty circle)
        if maxVal < 0.55:
            result = None    
        else:
            result = {'x':final_x, 'y':final_y}

        return result


    # look for the "PRESS [XX] TO DISENGAGE", if in this region then return true
    def sc_disengage(self, scr_reg) -> bool:
        dis_image, (minVal, maxVal, minLoc, maxLoc), match  = scr_reg.match_template_in_region('disengage', 'disengage')

        pt = maxLoc

        width  = scr_reg.templates.template['disengage']['width']
        height = scr_reg.templates.template['disengage']['height']

        if self.cv_view:
            self.draw_match_rect(dis_image, pt, (pt[0] + width, pt[1] + height), (0,255,0), 2)
            cv2.putText(dis_image, f'{maxVal:5.2f} >.50', (1, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow('disengage', dis_image)
            cv2.moveWindow('disengage', self.cv_view_x,self.cv_view_y+200)
            cv2.waitKey(1)

        logger.debug("Disenage = "+str(maxVal))

        if (maxVal > 0.50):
            self.vce.say("Disengaging Frameshift")
            return True
        else:
            return False



    def request_docking(self, toCONTACT):
        self.keys.send('UI_Back', repeat=10)
        self.keys.send('HeadLookReset')
        self.keys.send('UIFocus', state=1)
        self.keys.send('UI_Left')
        self.keys.send('UIFocus', state=0)
        sleep(0.5)
        
        # we start with the Left Panel having "NAVIGATION" highlighted, we then need to right
        # right twice to "CONTACTS".  Notice of a FSD run, the LEFT panel is reset to "NAVIGATION"
        # otherwise it is on the last tab you selected.  Thus must start AP with "NAVIGATION" selkected
        if (toCONTACT == 1):
            self.keys.send('CycleNextPanel', hold=0.2 )
            sleep(0.2)
            self.keys.send('CycleNextPanel', hold=0.2 )

        # On the CONTACT TAB, go to top selection, do this 4 times to ensure at top
        # then go right, which will be "REQUEST DOCKING" and select it
        self.keys.send('UI_Up', hold=4)
        self.keys.send('UI_Right')
        self.keys.send('UI_Select')
        
        sleep(0.3)
        self.keys.send('UI_Back')
        self.keys.send('HeadLookReset')

    def dock(self): 
        # if not in normal space, give a few more sections as at times it will take a little bit
        if self.jn.ship_state()['status'] != "in_space":
            sleep(3)  # sleep a little longer

        if self.jn.ship_state()['status'] != "in_space":
            logger.error('In dock(), after wait, but still not in_space')
            
        sleep(5)   # wait 5 seconds to get to 7.5km to request docking
        self.keys.send('SetSpeed50')

        if self.jn.ship_state()['status'] != "in_space":
            self.keys.send('SetSpeedZero')
            logger.error('In dock(), after long wait, but still not in_space')
            raise Exception('Docking error') 

        sleep(12)
        # At this point (of sleep()) we should be < 7.5km from the station.  Go 0 speed
        # if we get docking granted ED's docking computer will take over
        self.keys.send('SetSpeedZero', repeat=2)   

        self.request_docking(1)
        sleep(1)

        tries = 2
        granted = False
        if self.jn.ship_state()['status'] == "dockinggranted":
            granted = True
        else:
            for i in range(tries):
                self.request_docking(0)
                self.keys.send('SetSpeedZero', repeat=2)   
                sleep(1.5)
                if self.jn.ship_state()['status'] == "dockinggranted":
                    granted = True
                    break
                if self.jn.ship_state()['status'] == "dockingdenied": 
                    pass
                
        if not granted:
            self.ap_ckb('log', 'Docking denied: '+str(self.jn.ship_state()['no_dock_reason']))
            logger.warning('Did not get docking authorization, reason:'+str(self.jn.ship_state()['no_dock_reason']))
        else:     
            # allow auto dock to take over
            wait = 120
            for i in range(wait):
                sleep(1)
                if self.jn.ship_state()['status'] == "in_station":
                    # go to top item, select (which should be refuel)
                    self.keys.send('UI_Up', hold=3)
                    self.keys.send('UI_Select')
                    # down to station services
                    self.keys.send('UI_Down')
                    self.keys.send('UI_Select')
                    break


    def sun_align(self, scr_reg):
        logger.debug('align= avoid sun')
        while scr_reg.sun_percent(scr_reg.screen) > 5:
            self.keys.send('PitchUpButton', state=1)

        sleep(0.3)    # wait another 1/2sec to get more pitch away from Sun
        self.keys.send('PitchUpButton', state=0)


    # we know x, y offset of the nav point from center, use arc tan to determine the angle, convert to degrees
    # we want the angle to the 90 (up) and 180 (down) axis 
    def x_angle(self, point=None):
        if not point:
            return None
        if point['x'] == 0:
            point['x'] = 0.1
        result = degrees(atan(abs(point['y'])/abs(point['x'])))
        
        return 90-result
        
            
    def nav_align(self, scr_reg):
        close = 2
        if not (self.jn.ship_state()['status'] == 'in_supercruise' or self.jn.ship_state()['status'] == 'in_space'):
           logger.error('align=err1')
           raise Exception('nav_align not in super or space') 

        self.keys.send('SetSpeed100')
        self.vce.say("Navigation Align")

        # get the x,y offset from center, or none, which means our point is behind us
        off = self.get_nav_offset(scr_reg)
  
        # check to see if we are already converged, if so return    
        if off != None and abs(off['x']) < close and abs(off['y']) < close:
            return
         
        # nav point must be behind us, pitch up until somewhat in front of us
        while not off:
            self.keys.send('PitchUpButton', state=1)   
            off = self.get_nav_offset(scr_reg)            
        self.keys.send('PitchUpButton', state=0)

        # check if converged, unlikely at this point
        if abs(off['x']) < close and abs(off['y']) < close:
            return;

        # try multiple times to get aligned.  If the sun is shining on console, this it will be hard to match
        # the vehicle should be positioned with the sun below us via the sun_align() routine after a jump
        for ii in range(3):
            off = self.get_nav_offset(scr_reg)
          
            if off != None and abs(off['x']) < close and abs(off['y']) < close:
                break
              
            while not off:
                self.keys.send('PitchUpButton', hold=0.35)   
                off = self.get_nav_offset(scr_reg)

            # determine the angle and the hold time to keep the button pressed to roll that number of degrees
            ang = self.x_angle(off) % 90
            htime = ang / self.rollrate    
                
            logger.debug("Angle:" +str(ang)+" x: "+str(off['x'])+" rolltime:"+str(htime))
            
            # first roll to get the nav point at the vertical position
            if (abs(off['x']) > close):
                # top right quad, then roll right to get to 90 up
                if (off['x'] > 0 and off['y'] > 0 ):
                    self.keys.send('RollRightButton', hold=htime)  
                # bottom right quad, then roll left
                elif (off['x'] > 0 and off['y'] < 0):
                    self.keys.send('RollLeftButton', hold=htime) 
                # top left quad, then roll left
                elif (off['x'] < 0 and off['y'] > 0):
                    self.keys.send('RollLeftButton', hold=htime) 
                # bottom left quad, then roll right
                else:
                    self.keys.send('RollRightButton', hold=htime) 
            else:
                #print("X is <= "+str(close))
                pass

            sleep(0.15)    # wait for image to stablize
            off = self.get_nav_offset(scr_reg)
            while not off:
                self.keys.send('PitchUpButton', hold=0.35)   
                off = self.get_nav_offset(scr_reg)
 
            utime = (abs(off['y']) / 40.) * (90./self.pitchrate)
            logger.debug("ptichtime:"+str(utime)+" x:"+str(off['x'])+" y:"+str(off['y']))

            if (abs(off['y']) > close):
                if (off['y'] < 0):
                    self.keys.send('PitchDownButton', hold=utime) 
                else:
                    self.keys.send('PitchUpButton', hold=utime) 
            else:
                #print("Y is <= "+str(close))
                pass
            sleep(.1)
            logger.debug("final x:"+str(off['x'])+" y:"+str(off['y']))



    def target_align(self, scr_reg):
        self.vce.say("Target Align")

        logger.debug('align= fine align')
    
        close = 50
    # TODO: was .200  change to .150 for asp
        hold_pitch = 0.150
        hold_yaw = 0.300
        for i in range(5):
            new = self.get_destination_offset(scr_reg)
            if new:
                off = new
                break
            sleep(0.25)

        # try one more time to align
        if (new == None):
            self.nav_align(scr_reg)
            new = self.get_destination_offset(scr_reg)
            if new:
                off = new
            else:
                logger.debug('  out of fine -not off-'+ '\n')   
                return
        # 
        while (off['x'] > close) or \
            (off['x'] < -close) or \
            (off['y'] > close) or \
            (off['y'] < -close):
    
            #print("off:"+str(new))  
            if off['x'] > close:
                self.keys.send('YawRightButton', hold=hold_yaw)
            if off['x'] < -close:
                self.keys.send('YawLeftButton', hold=hold_yaw)
            if off['y'] > close:
                self.keys.send('PitchUpButton', hold=hold_pitch)
            if off['y'] < -close:
                self.keys.send('PitchDownButton', hold=hold_pitch)
                
            if self.jn.ship_state()['status'] == 'starting_hyperspace':
                return
        
            for i in range(5):
                sleep(0.1)
                new = self.get_destination_offset(scr_reg)
                if new:
                    off = new
                    break
                sleep(0.25)
                
                
            if not off:
                return
        
        logger.debug('align=complete')



    def mnvr_to_target(self, scr_reg):
        logger.debug('align')
        if not (self.jn.ship_state()['status'] == 'in_supercruise' or self.jn.ship_state()['status'] == 'in_space'):
            logger.error('align() not in sc or space')
            raise Exception('align() not in sc or space')

        self.sun_align(scr_reg)
        self.nav_align(scr_reg)
        self.target_align(scr_reg)
        
    # This function stays tight on the target, monitors for disengage
    def sc_target_align(self, scr_reg):    
        close = 6

        hold_pitch = 0.100
        hold_yaw = 0.100
        for i in range(5):
            new = self.get_destination_offset(scr_reg)
            if new:
                off = new
                break
            sleep(0.25)

        logger.debug("sc_target_align x: "+str(off['x'])+ " y:"+str(off['y']))
        
        while (abs(off['x']) > close) or \
              (abs(off['y']) > close):

            if (abs(off['x']) > 25):
                hold_yaw = 0.2
            else:
                hold_yaw = 0.09

            if (abs(off['y']) > 25):
                hold_pitch = 0.15
            else:
                hold_pitch = 0.075

            logger.debug("  sc_target_align x: "+str(off['x'])+ " y:"+str(off['y']))

            if off['x'] > close:
                self.keys.send('YawRightButton', hold=hold_yaw)
            if off['x'] < -close:
                self.keys.send('YawLeftButton', hold=hold_yaw)
            if off['y'] > close:
                self.keys.send('PitchUpButton', hold=hold_pitch)
            if off['y'] < -close:
                self.keys.send('PitchDownButton', hold=hold_pitch)
            
            sleep(.1)  # time for image to catch up

            new = self.get_destination_offset(scr_reg)
            if new:
                off = new


    # Position() happens afer a refuel and performs
    #   - accelerate past sun
    #   - perform Discovery scan
    #   - perform fss (if enabled) 
    #   = pitch down 90 degree if target not in front of us
    def position(self, scr_reg, did_refuel=True):
        logger.debug('position')

        self.vce.say("Maneuvering")   
        
        self.sun_align(scr_reg)

        # if we didn't refuel, lets to a on-the-fly refueling going past the Sun 
        if (not did_refuel):
            self.keys.send('SetSpeed100')
            sleep(4)
            self.keys.send('SetSpeed50')
            sleep(8)
        
        self.keys.send('SetSpeed100')

        # find which fire button to use to do system scan and press and hold the button
        scan = 1
        if scan == 1:
            logger.debug('position=scanning')
            self.keys.send('PrimaryFire', state=1)
        elif scan == 2:
            logger.debug('position=scanning')
            self.keys.send('SecondaryFire', state=1)
            
        sleep(10)

        # stop pressing the Scanner button
        if scan == 1:
            logger.debug('position=scanning complete')
            self.keys.send('PrimaryFire', state=0)
        elif scan == 2:
            logger.debug('position=scanning complete')
            self.keys.send('SecondaryFire', state=0)
        
        if (did_refuel):
            sleep(4)

        # TODO: skip until figure out better way of defining the region
        if self.fss_scan_enabled == True:
            self.fss_detect_elw(scr_reg)

        # only pitch down if the target isn't in front of us
        if  (self.get_nav_offset(scr_reg) == None):
            self.vce.say("Positioning")   
            self.pitch90Down()

        logger.debug('position=complete')
        return True



    # jump() happens after we are aligned to Target
    def jump(self, scr_reg):
        logger.debug('jump')

        self.vce.say("Frameshift Jump")
        tries = 3
        for i in range(tries):
            
            logger.debug('jump= try:'+str(i))
            if not (self.jn.ship_state()['status'] == 'in_supercruise' or self.jn.ship_state()['status'] == 'in_space'):
                logger.error('jump=err1')
                raise Exception('not ready to jump')
            sleep(0.5)
            logger.debug('jump= start fsd')
            self.keys.send('HyperSuperCombination', hold=1)
            sleep(16)
            
            if self.jn.ship_state()['status'] != 'starting_hyperspace':
                logger.debug('jump= misalign stop fsd')
                self.keys.send('HyperSuperCombination', hold=1)
                sleep(2)
                self.mnvr_to_target(scr_reg)  # attempt realign to target
            else:
                logger.debug('jump= in jump')
                while self.jn.ship_state()['status'] != 'in_supercruise':
                    sleep(1)
                logger.debug('jump= speed 0')
                self.jump_cnt = self.jump_cnt + 1
                self.keys.send('SetSpeedZero')
                sleep(1)             # wait 1 sec after jump to allow graphics to stablize and accept inputs
                logger.debug('jump=complete')
                return True
            
        logger.error('jump=err2')
        raise Exception("jump failure")    


    def rotate90Left(self):
        htime = 90/self.rollrate
        self.keys.send('RollLeftButton', hold=htime)

    def pitch90Down(self):
        htime = 90/self.pitchrate
        self.keys.send('PitchDownButton', htime)


    def refuel(self, scr_reg,refuel_threshold=65):
        global refuel_cnt

        logger.debug('refuel')
        scoopable_stars = ['F', 'O', 'G', 'K', 'B', 'A', 'M']
        if self.jn.ship_state()['status'] != 'in_supercruise':
            logger.error('refuel=err1')
            return False
            raise Exception('not ready to refuel')

        self.vce.say("Sun avoidance")
        # if we are under our refuel threshold then we will:
        #  - Set Speed to 100 for 4 seconds to get a little closer to the Sun
        #  - Put Speed to 0, we should be scooping now
        #  - wait until fuel is full
        # Return true if we refueled, faulse otherwise

        self.rotate90Left()

        sleep(0.5)   # give time for display to update

        self.sun_align(scr_reg)
        
        if self.jn.ship_state()['fuel_percent'] < refuel_threshold and self.jn.ship_state()['star_class'] in scoopable_stars:
            logger.debug('refuel= start refuel')
            self.vce.say("Refueling")
            self.keys.send('SetSpeed100')
    
            sleep(5)
            self.keys.send('SetSpeed50')
            sleep(1.7)
            self.keys.send('SetSpeedZero', repeat=3)

            refuel_cnt = self.refuel_cnt + 1

            # The log will reflect a FuelScoop until first 5 tons filled, then every 5 tons until complete
            #if we don't scoop first 5 tons with 40 sec break, since not scooping or not fast enough or not at all, go to next star
            startime = time.time();
            while not self.jn.ship_state()['is_scooping'] and not self.jn.ship_state()['fuel_percent'] == 100:
                if ((time.time()-startime) > 40):
                    self.vce.say("Refueling abort, insufficient scooping")
                    return True;
            sleep(1)

            logger.debug('refuel= wait for refuel')

            while not self.jn.ship_state()['fuel_percent'] == 100:
                sleep(1)
            logger.debug('refuel=complete')
            return True
        elif self.jn.ship_state()['fuel_percent'] >= refuel_threshold:
            logger.debug('refuel= not needed')
            return False
        elif self.jn.ship_state()['star_class'] not in scoopable_stars:
            logger.debug('refuel= needed, unsuitable star')
            return False
        else:
            return False
 
    def set_focus_elite_window(self):
        handle = win32gui.FindWindow(0, "Elite - Dangerous (CLIENT)")   
        if handle != None:
            win32gui.SetForegroundWindow(handle)  # give focus to ED

    def fsd_assist(self, scr_reg):
        logger.debug('self.jn.ship_state='+str(self.jn.ship_state()))

        self.jump_cnt = 0
        self.refuel_cnt = 0

        starttime = time.time()
        starttime -= 20   # to account for first instance not doing positioning

        sleep(2)    # give time to set focus to ED

        while self.jn.ship_state()['target']:
            if self.jn.ship_state()['status'] == 'in_space' or self.jn.ship_state()['status'] == 'in_supercruise':
                self.ap_ckb('statusline',"Align")

                self.mnvr_to_target(scr_reg)

                self.ap_ckb('statusline',"Jump")

                self.jump(scr_reg)
                
                avg_time_jump = (time.time() - starttime)/self.jump_cnt
                self.ap_ckb('jumpcount',"j#"+str(self.jump_cnt)+" : r#:"+ str(self.refuel_cnt) +" : ""{:.0f}".format(avg_time_jump)+"s/j")

                self.ap_ckb('statusline',"Refuel")

                refueled = self.refuel(scr_reg)

                self.ap_ckb('statusline',"Maneuvering")

                self.position(scr_reg, refueled)

                if (self.jn.ship_state()['fuel_percent'] < 35):
                    self.ap_ckb('log'"AP Aborting, low fuel")
                    self.vce.say("AP Aborting, low fuel")
                    break

        sleep(2)  # wait until screen stablizes from possible last positioning
        if self.have_destination(scr_reg) == False:
            self.keys.send('SetSpeedZero')
            self.vce.say("Destination Reached") 
            return True
        else:
            self.keys.send('SetSpeed100')  
            self.vce.say("System Reached, preparing for supercruise") 
            sleep(10)         
            return False

   

    def sc_assist(self, scr_reg):
        # see if we have a compass up, if so then we have a target
        if self.have_destination(scr_reg) == False:
            return

        # Need unit target_Align,   do  nav_Align out side of loop,
        # sc_target_Align will look to see if out of whack and then adjust
        #
        #while self.jn.ship_state()['target']:
        sleep(2)

        self.keys.send('SetSpeed50')
        self.nav_align(scr_reg)
        self.keys.send('SetSpeed50')

        while True:
            sleep(1)
            if self.jn.ship_state()['status'] == 'in_supercruise':
        #       nav_mnvr_to_target(scr_reg)
                self.sc_target_align(scr_reg)
            # check if Drop of SC
            if (self.sc_disengage(scr_reg) == True):
                self.keys.send('HyperSuperCombination', hold=0.001)
                break

        sleep(4)   #wait for the journal to catch up
        self.dock()
        self.ap_ckb('sc_stop')
 
    def afk_combat_loop(self):
        while True:
            if self.afk_combat.check_shields_up() == False:
                self.set_focus_elite_window()
                self.vce.say("Shields down, evading")
                self.afk_combat.evade()
                # after supercruise the menu is reset to top
                self.afk_combat.launch_fighter()  # at new location launch fighter
                break
                
            if self.afk_combat.check_fighter_destroyed() == True:
                self.set_focus_elite_window()
                self.vce.say("Fighter Destroyed, redeploying") 
                self.afk_combat.launch_fighter()  # assuming two fighter bays
                
        self.vce.say("Terminating AFK Combat Assist")


    def ctype_async_raise(self, thread_obj, exception):
        found = False
        target_tid = 0
        for tid, tobj in threading._active.items():
            if tobj is thread_obj:
                found = True
                target_tid = tid
                break

        if not found:
            raise ValueError("Invalid thread object")

        ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(target_tid),
                                                        ctypes.py_object(exception))
        # ref: http://docs.python.org/c-api/init.html#PyThreadState_SetAsyncExc
        if ret == 0:
            raise ValueError("Invalid thread ID")
        elif ret > 1:
            # Huh? Why would we notify more than one threads?
            # Because we punch a hole into C level interpreter.
            # So it is better to clean up the mess.
            ctypes.pythonapi.PyThreadState_SetAsyncExc(target_tid, 0)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    
  
    def set_fsd_assist(self, enable=True):
        if enable == False and self.fsd_assist_enabled == True:
            self.ctype_async_raise(self.ap_thread,EDAP_Interrupt)
        self.fsd_assist_enabled = enable
        
    def set_sc_assist(self, enable=True):
        if enable == False and self.sc_assist_enabled == True:
            self.ctype_async_raise(self.ap_thread,EDAP_Interrupt)
        self.sc_assist_enabled = enable
        
    def set_fss_scan(self, enable=True):
        self.fss_scan_enabled = enable
        
    def set_afk_combat_assist(self, enable=True):
        self.afk_combat_assist_enabled = enable

    def set_cv_view(self, enable=True, x=0, y=0):
        self.cv_view = enable
        if enable == True:
            self.cv_view_x = x
            self.cv_view_y = y
        else:
            cv2.destroyAllWindows()
            cv2.waitKey(50)

    def set_voice(self, enable=True):
        if enable == True:
            self.vce.set_on()
        else:
            self.vce.set_off()

    def quit(self):
        if self.vce != None:
            self.vce.quit()
        if self.overlay != None:
            self.overlay.overlay_quit()
        self.terminate = True
        
    # this could be a thread, then we command it via msgQue
    def engine_loop(self):
        while not self.terminate:
            if self.fsd_assist_enabled == True:
                logger.debug("Running fsd_assist")
                self.set_focus_elite_window()
                fin = True
                # could be deep in call tree when user disables FSD, so need to trap that exception
                try:
                    fin = self.fsd_assist(self.scrReg)
                except EDAP_Interrupt:
                    logger.debug("Caught stop exception")
                except Exception as e:
                    print("Trapped generic:"+str(e))
                    traceback.print_exc()
                    
                self.fsd_assist_enabled = False
                self.ap_ckb('fsd_stop')
                
                # if fsd_assist returned false then we are not finished, meaning we have an in system target
                # defined.  So lets enable Supercruise assist to get us there
                # Note: this is tricky, in normal FSD jumps the target is pretty much on the other side of Sun
                #  when we arrive, but not so when we are in the final system
                if fin == False:
                    self.ap_ckb("sc_start")
                    
                # drop all out debug windows
                cv2.destroyAllWindows()
                cv2.waitKey(10)

            elif self.sc_assist_enabled == True:
                logger.debug("Running sc_assist")
                self.set_focus_elite_window()
                try:
                    self.sc_assist(self.scrReg)
                except EDAP_Interrupt:
                    logger.debug("Caught stop exception")
                except Exception as e:
                    print("Trapped generic:"+str(e))
                    traceback.print_exc()
                    
                self.sc_assist_enabled = False
                self.ap_ckb('sc_stop')
                
            elif self.afk_combat_assist_enabled == True:
                #self.afk_combat_assist_enabled = False
                #self.ap_ckb('<TOADD>')
                self.afk_combat_loop()
                pass

            sleep(1)





def main():

    #handle = win32gui.FindWindow(0, "Elite - Dangerous (CLIENT)")   
    #if handle != None:
    #    win32gui.SetForegroundWindow(handle)  # put the window in foreground

    ed_ap = EDAutopilot(False)
    ed_ap.cv_view = True
    ed_ap.cv_view_x = 4000
    ed_ap.cv_view_y = 100
    sleep(2)
    
    for x in range(10):
    #    target_align(scrReg)
        print("Calling nav_align")
        #ed_ap.nav_align(ed_ap.scrReg)
        ed_ap.fss_detect_elw(ed_ap.scrReg)
        
    #    loc = get_destination_offset(scrReg)
    #    print("get_dest: " +str(loc))
    #    loc = get_nav_offset(scrReg)
    #    print("get_nav: " +str(loc))
        cv2.waitKey(0)
        print("Done nav")
        sleep(8)

    ed_ap.overlay.overlay_quit()

if __name__ == "__main__":
    main()