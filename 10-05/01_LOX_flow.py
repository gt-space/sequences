#After the tanks have been pressurized, and all systems are go
ftpt_target = 383*psi #in psig, target fuel tank pressure
#otpt_target = 385*psi #in psig, target lox tank pressure (not current)
ran = 5*psi #acceptable range in psi for bang bang algorithm
wait_timing = 5 #for loop check timing, ms
ignitor_lead = 3000 #how soon to start the igniter before fuel reaches tank
fire_time = 4000 #time in ms we are going to fire for




print('Fuel Flow Has Begun')

flow_time = round((fire_time)/wait_timing)



#checks to see if the ignitor sense wire is in tact
if Sense.read() < 3.5*V:
    print('The ignitor sense wire has failed')
    stop()


#open PRISO2, might move this to checks
PRISO2.open()


for t in range(round(ignitor_wait_time/wait_timing)):
#    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
#        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

#    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
#        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()

    if Sense.read() < 0.4*V:
         print('The ignitor sense wire has broken')
         break
    wait_for(wait_timing*ms)


#Keep Tanks Pressed
for t in range(omv_open_time):
    #Initiate bang bang sequence
#    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
#        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

#    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
#        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()

    wait_for(wait_timing*ms)
#Checks to make sure the ignitor has gone off


OMV.open()
#FMV.open()

for t in range(flow_time):
    #Keep bang bang sequence going
#    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
#        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

#    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
#        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()


    wait_for(wait_timing*ms)

#Close Lox and tank press
OMV.close()
#FMV.close()
#FBANG.close()
OBANG.close()
PRISO2.close()

wait_for(500*ms)

#FPV.close()
OPV.close()


print('Test Sequence Has Ended')
