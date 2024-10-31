'Fire_sequence_interval' #After the tanks have been pressurized, and all systems are go
ftpt_target = 300*psi #in psig, target fuel tank pressure (not current)
otpt_target = 600*psi #in psig, target lox tank pressure (not current)
ran = 5*psi #acceptable range in psi for bang bang algorithm
wait_timing = 5 #Defines logic timing
ignitor_lead = 3000 #how soon to start the igniter before fuel reaches tank
FMV_time = 585 #observed FMV actuation time in milliseconds (not current)
OMV_time = 437 #observed OMV actuation time in milliseconds (not current)
lox_lead = 200 #time in ms OMV should be completely open before fire
fire_time = 4000 #time in ms we are going to fire for
lox_close_lead = 150 #time command is sent to close omv before fmv at end of sequence to avoid oxidizer rich combustion (not current)
purge_time = 10000 #time to run purge for
fs_time = 8000 # time to automatically run fire supression for at the end of the sequence
ignitor_wait_time = 1500 #time allocated for sense wire to break
OMV_close_time = 484 # observed OMV closing time
FMV_close_time = 390 # observed FMV closing time

if OMV_time + lox_lead > FMV_time:
    first_open_time = round((ignitor_lead-OMV_time-lox_lead)/wait_timing) #Calculates when to open the first valve after the sequence has started
    second_open_time = round(((ignitor_lead-FMV_time) - (ignitor_lead-lox_lead-OMV_time))/wait_timing) #Calculates when to open the second main valve, based on how recently the first was opened
    firing_time = round((FMV_time + fire_time)/wait_timing)
    if (OMV_close_time+lox_close_lead)>FMV_close_time:
        first_close_time = OMV_close_time
        second_close_time = FMV_close_time


    ignitor_window = round(ignitor_wait_time/wait_timing)
else:
    first_open_time = round((ignitor_lead-FMV_time)/wait_timing) #Calculates when to open the first valve after the sequence has started
    second_open_time = round((ignitor_lead-(OMV_time+lox_lead) - (ignitor_lead-FMV_time))/wait_timing) #Calculates when to open the second main valve, based on how recently the first was opened
    firing_time = round((OMV_time + fire_time)/wait_timing)
    ignitor_window = round(ignitor_wait_time/wait_timing)

    


#check to ensure that the valve states are correct in the reference doc for what they should be
#if not fire_sequence_valve_states.check():
#   warn('Valve states do not match the reference doc for this sequence. Cancelling.')
#  stop()
#stop sequence if the valve states do not match

#checks to see if the ignitor sense wire is in tact
if Sense.read() < 3.5*V:
    print('The ignitor sense wire has failed')
    stop()


#open PRISO2
PRISO2.open()

#Start Ignitor
Ignitor1.open()
Ignitor2.open()

for t in interval(ignitor_window, wait_timing*ms):
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()
       # OBANG_state = False


    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()
        #FBANG_state = True


    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()
        #OBANG_state = True

    if Sense.read() < 0.4*V:
         print('The ignitor sense wire has broken')
         break
    wait_for(wait_timing*ms) 




if Sense.read() > 3.5*V:
    print('The ignitor sense wire was not broken')
    FBANG.close()
    OBANG.close()
    PRISO2.close()
    Ignitor1.close()
    Ignitor2.close()
    stop()

#Keep Tanks Pressed
for t in range(first_open_time):
    #Initiate bang bang sequence
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()
        #FBANG_state = False


    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()
       # OBANG_state = False


    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()
        #FBANG_state = True


    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()
        #OBANG_state = True


    wait_for(wait_timing*ms) 
#Checks to make sure the ignitor has gone off

if OMV_time + lox_lead > FMV_time:
    OMV.open()
else:
    FMV.open()


for t in range(second_open_time):
    #Initiate bang bang sequence
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()
        #FBANG_state = False


    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()
       # OBANG_state = False


    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()
        #FBANG_state = True


    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()
        #OBANG_state = True

    wait_for(wait_timing*ms)
if OMV_time + lox_lead > FMV_time:
    FMV.open()
else:
    OMV.open()
    
Ignitor1.close()
Ignitor2.close()

for t in range(firing_time):
    #Keep bang bang sequence going
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()
        #FBANG_state = False


    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()
       # OBANG_state = False


    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()
        #FBANG_state = True


    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()
        #OBANG_state = True

    wait_for(wait_timing*ms) 


OMV.close()

wait_for(lox_close_lead*ms)

#Close Main Valves
FMV.close()
FBANG.close()
OBANG.close()
PRISO2.close()

wait_for(500*ms)
FPV.close()
OPV.close()
wait_for(500*ms)


#Begin Purge
PUF.open()
PUO.open()
FSISO2.open()
wait_for(fs_time*ms)
wait_for((purge_time-fs_time)*ms)
FSISO2.close()

print('Fire sequence has ended')
