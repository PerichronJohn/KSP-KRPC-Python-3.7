import krpc
import time
import math
import RPi.GPIO as gp

conn = krpc.connect(name='Vessel Datalink')
vessel = conn.space_center.active_vessel
obt_frame = vessel.orbit.body.non_rotating_reference_frame
srf_frame = vessel.orbit.body.reference_frame

target_altitude = 250000
turn_end_altitude = 150000
turn_start_altitude = 1000

stage1_location = 1
stage2_location = -1
srb_location = 3
stage1_liquid_prop = "Kerosene"
stage2_liquid_prop = "LqdHydrogen"
solid_prop = "HTPB"

stage1_sep = False
stage2_sep = False
srb_sep = False
fairing_sep = False
periapsis_raise = False
ascent = True

altitude = round(vessel.flight().surface_altitude, 2)
srb_fuel = vessel.resources.amount(solid_prop)
stage1_lf = round(vessel.resources_in_decouple_stage(stage1_location, cumulative = False).amount(stage1_liquid_prop))
stage2_lf = round(vessel.resources_in_decouple_stage(stage2_location, cumulative = False).amount(stage2_liquid_prop))
current_mass = round(vessel.mass, 2)
max_thrust = round(vessel.available_thrust, 2)
current_thrust = round(vessel.thrust, 2)
periapsis_alt = round(vessel.orbit.periapsis_altitude, 2)
apoapsis_altitude = round(vessel.orbit.apoapsis_altitude, 2)
time_to_apo = round(int(vessel.orbit.time_to_apoapsis), 2)
target_heading = 90
target_pitch = 90
vert_pitch = 90
vessel.auto_pilot.target_pitch_and_heading(target_pitch, target_heading)
vessel.auto_pilot.engage()

green = 17
yellow = 27
red = 22
yellow2 = 5
blue = 24
button1 = 23
button2 = 21

gp.setwarnings(False)
gp.setmode(gp.BCM)
gp.setup(green, gp.OUT)
gp.setup(yellow, gp.OUT)
gp.setup(red, gp.OUT)
gp.setup(yellow2, gp.OUT)
gp.setup(blue, gp.OUT)
gp.setup(button1, gp.OUT)
gp.setup(button2, gp.OUT)

def telemetry():
    global altitude
    global srb_fuel
    global stage1_lf
    global stage2_lf
    global current_mass
    global max_thrust
    global current_thrust
    global periapsis_alt
    global apoapsis_altitude
    global time_to_apo
    global target_pitch
    global target_heading

    altitude = round(vessel.flight().surface_altitude, 2)
    srb_fuel = round(vessel.resources.amount(solid_prop))
    stage1_lf = round(vessel.resources_in_decouple_stage(stage1_location, cumulative = False).amount(stage1_liquid_prop))
    stage2_lf = round(vessel.resources_in_decouple_stage(stage2_location, cumulative = False).amount(stage2_liquid_prop))
    current_mass = round(vessel.mass, 2)
    max_thrust = round(vessel.available_thrust, 2)
    current_thrust = round(vessel.thrust, 2)
    periapsis_alt = round(vessel.orbit.periapsis_altitude, 2)
    apoapsis_altitude = round(vessel.orbit.apoapsis_altitude, 2)
    time_to_apo = round(int(vessel.orbit.time_to_apoapsis), 2)
    vessel.auto_pilot.target_pitch_and_heading(target_pitch, target_heading)
    vessel.auto_pilot.engage()

class Stage_srb():
    def __init__(self, fuel):

        self.fuel = fuel

    def staging(self):
        if self.fuel <= 35:
            time.sleep(.5)
            vessel.control.activate_next_stage()
            print("[Solid Rocket Booster Seperation]")
            global srb_sep
            srb_sep = True

class Stage1():
    def __init__(self, fuel):

        self.fuel = fuel

    def staging(self):
        if self.fuel <= 250:
            print("[BECO]")
            time.sleep(1)
            vessel.control.throttle = 0
            vessel.control.activate_next_stage()
            print("[Stage 1 Seperation]")
            time.sleep(2)
            vessel.control.throttle = 1
            vessel.control.activate_next_stage()
            global stage1_sep
            stage1_sep = True

class Stage2():
    def __init__(self, fuel):

        self.fuel = fuel

    def staging(self):
        if self.fuel <= 250:
            time.sleep(.5)
            vessel.control.activate_next_stage()
            print("[Stage 2 Seperation]")
            global stage2_sep
            stage2_sep = True

class Stage_Fairing():
    def __init__(self,altitude):

        self.altitude = altitude

    def staging(self):
        if self.altitude > 60000:
            vessel.control.activate_next_stage()
            print("[Payload Fairing Seperation]")
            global fairing_sep
            fairing_sep = True

class Periapsis_Raise:

    def __init__(self, altitude, periapsis_alt):

        self.altitude = altitude
        self.periapsis_alt = periapsis_alt

    def circularize():
        global target_altitude
        global time_to_apo
        global target_pitch

        if time_to_apo < 10 and periapsis_alt < target_altitude*.5 and time_to_apo > 20:
            target_pitch = 0
            vessel.control.throttle = 1
        if time_to_apo < 15 and time_to_apo > 11:
            target_pitch = 1
        if time_to_apo < 11 and time_to_apo > 8:
            target_pitch = 3
        if time_to_apo < 8 and time_to_apo > 5:
            target_pitch = 5
        if time_to_apo < 5 and time_to_apo > 2:
            target_pitch = 8
        if time_to_apo < 2 and time_to_apo > 1:
            target_pitch = 10
        if time_to_apo > 20 and time_to_apo < 25:
            target_pitch = 358
        if time_to_apo > 25 and time_to_apo < 30:
            target_pitch = 355
        if time_to_apo > 30 and time_to_apo < 35:
            target_pitch = 350
        if altitude > target_altitude and periapsis_alt > -target_altitude*2 and periapsis_alt < target_altitude:
            vessel.control.throttle = .3
        if periapsis_alt >= target_altitude:
            vessel.control.throttle = 0
            global periapsis_raise
            periapsis_raise = True

def ascent_guidance():
    """Direct the rocket during ascent"""
    global target_pitch
    frac = (
            (altitude - turn_start_altitude) /
            (turn_end_altitude - turn_start_altitude)
            )
    new_turn_angle = round(frac * 90, 4)
    if altitude < turn_start_altitude:
        target_pitch = 90
    if altitude > turn_start_altitude and altitude < turn_end_altitude:
        target_pitch = (vert_pitch - new_turn_angle)
    if altitude > turn_end_altitude and time_to_apo > 120:
        target_pitch = 0
    if altitude > turn_end_altitude and time_to_apo < 110 and time_to_apo > 100:
        target_pitch = 5
    if altitude > turn_end_altitude and time_to_apo < 100 and time_to_apo > 90:
        target_pitch = 10
    if altitude > turn_end_altitude and time_to_apo < 90 and time_to_apo > 80:
        target_pitch = 15
    if altitude > turn_end_altitude and time_to_apo < 80 and time_to_apo > 70:
        target_pitch = 25
    if altitude > turn_end_altitude and time_to_apo < 70 and time_to_apo > 50:
        target_pitch = 35
    if altitude > turn_end_altitude and time_to_apo < 45 and time_to_apo > 25:
        target_pitch = 45

    apoapsis_altitude = round(vessel.orbit.apoapsis_altitude, 2)
    if (target_altitude*.8) < apoapsis_altitude:
        slowdown_frac = ((target_altitude - apoapsis_altitude) / 10000)
        throttle_down = round(slowdown_frac, 3)
        if throttle_down < .1:
            throttle_down = .1
        vessel.control.throttle = throttle_down
    if apoapsis_altitude >= target_altitude:
        vessel.control.throttle = 0
        target_pitch = 0
        global ascent
        ascent = False

startup = False
startup_flash = 0
if not startup:
    if gp.input(botton1):
        gp.output(green, True)
        time.sleep(.1)
        gp.output(green, False)
        gp.output(yellow, True)
        time.sleep(.1)
        gp.output(yellow, False)
        gp.output(red, True)
        time.sleep(.1)
        gp.output(red, False)
        gp.output(yellow2, True)
        time.sleep(.1)
        gp.output(yellow2, False)
        gp.output(blue, True)
        time.sleep(.1)
        gp.output(blue, False)
    if not gp.input(botton1) and start_up =< 3:
        gp.output(green, True)
        gp.output(yellow, True)
        gp.output(red, True)
        gp.output(yellow2, True)
        gp.output(blue, True)
        time.sleep(.5)
        gp.output(green, False)
        gp.output(yellow, False)
        gp.output(red, False)
        gp.output(yellow2, False)
        gp.output(blue, False)
        time.sleep(.5)
        startup_flash +=1
    if startup_flash = 3:
        startup = True
        flight = True
        print("[Flight Start-up]")

if not gp.input(botton2):
    print("[Ending]")
    gp.cleanup()
    break

flight = False
clock = -18
mission_time = -17
while flight:

    time.sleep(.1)
    clock += .1
    clock_time = round(clock, 2)
    mission_timer = clock_time.is_integer()
    mission_time = int(round(clock))

    telemetry()

    if ascent:
        ascent_guidance()

    stage1 = Stage1(stage1_lf)
    stage2 = Stage2(stage2_lf)
    solids = Stage_srb(srb_fuel)
    fairing = Stage_Fairing(altitude)
    p_raise = Periapsis_Raise(altitude, periapsis_alt)

    if not srb_sep:
        solids.staging()
    if not stage1_sep:
        stage1.staging()
    if not stage2_sep:
        stage2.staging()
    if not fairing_sep:
        fairing.staging()
    if not periapsis_raise:
        if altitude > target_altitude*.95:
            Periapsis_Raise.circularize()
    if abs(apoapsis_altitude - periapsis_alt) < 2000 and altitude > target_altitude*.9:
        print("Target Orbit Achieved")
        break

    gp.output(blue, True)
    if mission_timer:
        print(mission_time)
        gp.output(blue, False)
        if ascent:
            print("ascent : Running")
        if mission_time == -17:
            print("[Flight Running]")
            vessel.auto_pilot.target_pitch_and_heading(target_pitch, target_heading)
            vessel.auto_pilot.engage()
        if mission_time == -15:
            print("[T",mission_time,"]")
            current_throttle = 1
        if mission_time == -3:
            vessel.control.throttle = 1
        if mission_time == -2:
            vessel.control.activate_next_stage()
            print("[Ignition]")
        if mission_time == 0:
            vessel.control.activate_next_stage()
            print("[Liftoff]")
        if not srb_sep:
            #print("solids.staging : Running")
            print("srb_fuel: ", srb_fuel)
        if not stage1_sep:
            #print("stage1.staging : Running")
            print("stage1_lf: ", stage1_lf)
        if not stage2_sep:
            #print("stage2.staging : Running")
            print("stage2_lf: ", stage2_lf)
        if not fairing_sep:
            pass
            #print("Fairing.staging : Running")
        if not periapsis_raise:
            #print("P_raise.circularize : Running")
            print("altitude: ", altitude)
