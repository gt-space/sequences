'Fire_sequence_interval' #After the tanks have been pressurized, and all systems are go
ftpt_target = fueltankpress * psi  # in psig, target fuel tank pressure 
otpt_target = loxtankpress * psi  # in psig, target lox tank pressure
ran = 5 * psi  # acceptable range in psi for bang bang algorithm
wait_timing = 5
ignitor_lead = 3000  # how soon to start the igniter before fuel reaches tank
FMV_time = 690  # observed FMV actuation time in milliseconds 
OMV_time = 500  # observed OMV actuation time in milliseconds
lox_lead = 180  # time in ms OMV should be completely open before fire
fire_time = 5000  # time in ms we are going to fire for
lox_close_lead = 75  # time you have OMV closed before FMV at end of sequence to avoid oxidizer rich combustion (not current)
ignitor_wait_time = 1500  # time allocated for sense wire to break
nichrome_lead = 500  # Time to start nichrome wire
fs_time = 10000  # time to run fire suppression for
OMV_close_time = 420  # observed OMV closing time
FMV_close_time = 300  # observed FMV closing time
Purge_open_time = 130  # Purge Oxygen Open Time
Purge_lag_time = 250  # Time to lag purge after main valves command close, should be greater than purge open time

if OMV_time + lox_lead > FMV_time:
    first_open_time = round((ignitor_lead-OMV_time-lox_lead)/wait_timing) #Calculates when to open the first valve after the sequence has started
    second_open_time = round(((ignitor_lead-FMV_time) - (ignitor_lead-lox_lead-OMV_time))/wait_timing) #Calculates when to open the second main valve, based on how recently the first was opened
    firing_time = round((FMV_time + fire_time)/wait_timing)
else:
    first_open_time = round((ignitor_lead-FMV_time)/wait_timing) #Calculates when to open the first valve after the sequence has started
    second_open_time = round((ignitor_lead-(OMV_time+lox_lead) - (ignitor_lead-FMV_time))/wait_timing) #Calculates when to open the second main valve, based on how recently the first was opened
    firing_time = round((OMV_time + fire_time)/wait_timing)

if (OMV_close_time+lox_close_lead)>FMV_close_time:
        first_close_time = OMV_close_time
        second_close_time = FMV_close_time
else:
    first_close_time = FMV_close_time
    second_close_time = OMV_close_time

ignitor_window = round(ignitor_wait_time/wait_timing)
close_lead = (first_close_time + lox_close_lead - second_close_time)
purge_time = (Purge_lag_time - Purge_open_time)
    
print('Fire Sequence Has Begun')

#check to ensure that the valve states are correct in the reference doc for what they should be THIS IS USEFUL UPDATE THIS
#if not fire_sequence_valve_states.check():
#   warn('Valve states do not match the reference doc for this sequence. Cancelling.')
#  stop()
#stop sequence if the valve states do not match

#checks to see if the ignitor sense wire is intact
if Sense.read() < 3.5*V:
    print('The ignitor sense wire has failed')
    stop()


#open PRISO2
PRISO2.open()

Ignitor1.open() #Nichrome
wait_for(nichrome_lead*ms)

Ignitor2.open() # SRM

for t in interval(ignitor_window, wait_timing*ms):
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
    
#Checks to make sure the ignitor has gone off
if Sense.read() > 3.5*V:
    print('The ignitor sense wire was not broken')
    FBANG.close()
    OBANG.close()
    PRISO2.close()
    Ignitor1.close()
    Ignitor2.close()
    stop()

#Keep Tanks Pressed
for t in interval(first_open_time, wait_timing*ms):
    #Initiate bang bang sequence
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()

if OMV_time + lox_lead > FMV_time:
    OMV.open()
else:
    FMV.open()

for t in interval(second_open_time, wait_timing*ms):
    #Initiate bang bang sequence
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()
        
if OMV_time + lox_lead > FMV_time:
    FMV.open()
else:
    OMV.open()
    
Ignitor1.close()
Ignitor2.close()

for t in interval(firing_time, wait_timing*ms):
    #Keep bang bang sequence going
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()

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
wait_for((fs_time-500)*ms)
FSISO2.close()
wait_for(500*ms)
FVNT.open()
OVNT.open()

print('Fire sequence has ended')
