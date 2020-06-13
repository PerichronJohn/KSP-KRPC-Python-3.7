import krpc
import time
import math

conn = krpc.connect(name='Hop Guidance')
vessel = conn.space_center.active_vessel
obt_frame = vessel.orbit.body.non_rotating_reference_frame
srf_frame = vessel.orbit.body.reference_frame
vertical_velocity = vessel.flight(obt_frame).vertical_speed


target_altitude = 300
round_error = 2
target_heading = 90
target_pitch = 90
def telemetry():
    #current_q = round(vessel.flight().getAerodynamicForce(), round_error)
    #heading = vessel.flight().getHeading()
    #pitch = vessel.flight().getPitch()
    #v_speed = round(vessel.flight().getHorizontalSpeed(), round_error)
    #h_speed = round(vessel.flight().getVerticalSpeed(), round_error)
    current_g = round(vessel.flight().g_force, round_error)
    max_thrust = round(vessel.available_thrust, round_error)
    current_thrust = round(vessel.thrust, round_error)
    current_mass = round(vessel.mass, round_error)
    eq_thrust_kn = round(current_mass * current_g, round_error)
    eq_thrust = round(eq_thrust_kn / max_thrust, round_error)
    altitude = round(vessel.flight().surface_altitude, round_error)
    apoapsis_altitude = round(vessel.orbit.apoapsis_altitude, round_error)
    current_twr = round(current_mass / current_thrust * current_g)
    max_twr = round(max_thrust / current_mass * current_g, round_error)

def start_up():
    print("Startup")
    global engage

    if not engage:
        vessel.auto_pilot.target_pitch_and_heading(target_pitch, target_heading)
        vessel.auto_pilot.engage()
        vessel.control.activate_next_stage()
        engage = True
    vessel.control.throttle = .01

    time.sleep(3)
    started = True
    ascent_phase = True
    global start_up_phase
    start_up_phase = False

def ascent():
    print("Ascent")
    if altitude < target_altitude * .75:
        if v_speed < 10:
            vessel.control.throttle += .01
        if v_speed == 10:
            vessel.control.throttle == eq_thrust
        if v_speed > 10:
            vessel.control.throttle -= .01
    if altitude > target_altitude *.90:
        if v_speed < 5:
            vessel.control.throttle += .01
        if v_speed == 5:
            vessel.control.throttle == eq_thrust
        if v_speed > 5:
            vessel.control.throttle -= .01
    if altitude == target_altitude * .99:
        ascent_phase = False
        begin_hover = True

def hover():
    print("Hover")
    if v_speed < .5:
        vessel.control.throttle += .01
    if v_speed == 0:
        vessel.control.throttle = eq_thrust
    if v_speed > .5:
        vessel.control.throttle -= .01
    if v_speed > -2 and v_speed < 2:
        hovering = True
    if hover_timer >= 3:
        hover = False
        decent = True


def decent():
    print("Decent")
    if altitude > 50:
        if v_speed >= 10:
            vessel.control.throttle += .01
        if v_speed == 10:
            vessel.control.throttle = eq_thrust
        if v_speed <= 10:
            vessel.control.throttle -= .01
    if altitude < 50:
        if v_speed >= 5:
            vessel.control.throttle += .01
        if v_speed == 5:
            vessel.control.throttle = eq_thrust
        if v_speed <= 5:
            vessel.control.throttle -= .01

flight = True
started = False
start_up_phase = False
ascent_phase = False
hover_phase = False
decent_phase = False
hovering = False
hover_timer = 0
engage = False
ascent_start_time = 0
clock = -5
try:
    while flight:
        time.sleep(.1)
        clock += round(.1,1)

        clock_time = round(clock, 2)
        mission_timer = clock_time.is_integer()
        mission_time = int(round(clock,0))
        print(mission_time)

        if started:
            telemetry()
        if start_up_phase:
            start_up()
        if ascent_phase:
            ascent()
        if hover_timer >= 3:
            begin_hover = False
        if hover_phase:
            hover()
        if decent_phase:
            decent()
        if mission_time == -3:
            print("[Startup]")
            start_up_phase = True
        if mission_time == 0:
            start_up_phase = False
        if hovering:
            hover_timer += 1
    while mission_timer:
        print(mission_timer)
        mission_time += 1

except KeyboardInterrupt:
    print("[Ending]")
    gp.cleanup()
