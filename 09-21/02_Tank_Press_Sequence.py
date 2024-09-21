#For setting the initial tank pressure, separate from fire sequence
ftpt_target = 390 * psi # target fuel tank pressure (NEED)
otpt_target = 360 * psi # target lox tank pressure
wait_timing = 5 #for loop check timing, ms
press_time = 10000 #time to run press sequence for


PRISO2.open()
FBANG.open()
OBANG.open()

for t in range(round(press_time/wait_timing)): #match to format to run for 10000 ms, unsure of exact command
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()


PRISO2.close()
FBANG.close()
OBANG.close()

print("Tank press completed")