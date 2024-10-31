ftpt_target = 390*psi #in psig, target fuel tank pressure (not current)
otpt_target = 360*psi #in psig, target lox tank pressure (not current)
ftpt_max = 390
otpt_max = 360
ftpt_throttle = 365
otpt_throttle = 315
ran = 5*psi #acceptable range in psi for bang bang algorithm
wait_timing = 5
ignitor_lead = 3000 #how soon to start the igniter before fuel reaches tank
FMV_time = 600 #observed FMV actuation time in milliseconds (not current)
OMV_time = 480 #observed OMV actuation time in milliseconds (not current)
lox_lead = 200 #time in ms lox is in the chamber before fuel
#fire_time = 4500 #time in ms we are going to fire for
start_time = 2000 #T-0 to throttling begin
throttle_time = 1000 #nominal throttle time
down_time = 1500 #time to remain in throttled state
ramp_time = 2000 #time of start of rampiing to commanding main valves closed
lox_close_lead = 75 #time yo have OMV closed before fmv at end of sequence to avoid oxidizer rich combustion (not current)
ignitor_wait_time = 1500 #time allocated for sense wire to break
nichrome_lead = 500 #Time to start nichrome wire
vnt_time = 10000 #time to wait before opening vents
OMV_close_time = 420 # observed OMV closeing time
FMV_close_time = 300 # observed FMV closeing time
Purge_open_time = 130 #Purge Oxygen Open Time
Purge_lag_time = 180 #Time to lag purge after main valves command close, should be greater than purge open time
ramp_rate = 70 #in psi per second, do not exceed 75


omv_open_time = round((ignitor_lead-OMV_time)/wait_timing) #Calculates when to open OMV after the sequence has started
fmv_open_time = round(((ignitor_lead-FMV_time) - (ignitor_lead-lox_lead-OMV_time))/wait_timing) #Calculates when to open FMV, based on how recently OMV was opened
#firing_time = round((fire_time)/wait_timing)
starting_time = round((start_time+FMV_time)/wait_timing) #how many loops to stay in nominal
throttling_time = round((throttle_time)/wait_timing) #how many loops to be in throttling down mode
dropped_time = round(down_time/wait_timing) #how much time to stay throttled for
ramping_time = round(ramp_time/wait_timing) #how many loops after throttle to ramp for and burn to finish 
ignitor_window = round(ignitor_wait_time/wait_timing) #how many loops to stay in the ignitor window
close_lead = (OMV_close_time+lox_close_lead-FMV_close_time) #how many loops to wait before closing FMV after closing OMV
purge_time = (Purge_lag_time-Purge_open_time) #calculates in direct time when to open purge after commanding FMV closed


print('Throttle Fire Sequence Has Begun')



#checks to see if the ignitor sense wire is in tact
if Sense.read() < 3.5*V:
    print('The ignitor sense wire has failed')
    stop()


#open PRISO2, might move this to checks
PRISO2.open()


#Start Ignitor
Ignitor1.open() #Nichrome
wait_for(nichrome_lead*ms)

Ignitor2.open() # H Motor


#Dedicated window for sense wire to break in
for t in range(ignitor_window):
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()

    if Sense.read() < 0.4*V:
         print('The ignitor sense wire has broken')
         break
    wait_for(wait_timing*ms) 



#soft aborts if sense wire doesn't break
if Sense.read() > 3.5*V:
    print('The ignitor sense wire was not broken')
    FBANG.close()
    OBANG.close()
    PRISO2.close()
    Ignitor1.close()
    Ignitor2.close()
    stop()

#Keep Tanks Pressed until it is time to open OMV
for t in range(omv_open_time):
    #Initiate bang bang sequence
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()

    wait_for(wait_timing*ms) 


OMV.open()

#keep tanks pressed until it is time to open FMV
for t in range(fmv_open_time):
    #Initiate bang bang sequence
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()
   
    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()
    
    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()
      
    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()
        
    wait_for(wait_timing*ms) 

FMV.open()
Ignitor1.close()
Ignitor2.close()

#keep tanks pressed until time to throttle
for t in range(starting_time):
    #Keep bang bang sequence going
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()

    wait_for(wait_timing*ms) 
OVNT.open()
otpt_target = otpt_throttle*psi
ftpt_target = ftpt_throttle*psi

for t in range(throttling_time):
    #Keep bang bang sequence going
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()

    if OTPT.read() < otpt_target + 20*psi and OVNT.is_open():
        OVNT.close()
    wait_for(wait_timing*ms) 
OVNT.close()

for t in range(dropped_time):
    #Keep bang bang sequence going
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()

    wait_for(wait_timing*ms) 

otpt_target = otpt_max*psi
ftpt_target = ftpt_max*psi

for t in range(ramping_time):
    #Keep bang bang sequence going
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()

    wait_for(wait_timing*ms) 

OMV.close()
PRISO2.close()
FBANG.close()
OBANG.close()
#FSISO2.open()

wait_for(close_lead*ms)

#Close Main Valves, open Purge
FMV.close()

wait_for(purge_time*ms)
PUF.open()
PUO.open()
wait_for(500*ms)
FPV.close()
OPV.close()
wait_for((vnt_time-500)*ms)
#FSISO2.close()
#wait_for(500*ms)
FVNT.open()
OVNT.open()


print('Fire Sequence Has Ended')
