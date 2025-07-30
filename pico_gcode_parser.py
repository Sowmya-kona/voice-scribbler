import machine
import utime
import ujson
import math

# Stepper motor pin connections
X_STEP_PIN = 3
X_DIR_PIN = 2
Y_STEP_PIN = 15
Y_DIR_PIN = 14

# Microstepping control pins
M1_PIN = 20
M2_PIN = 21
M3_PIN = 22

# Servo motor pin
SERVO_PIN = 1  # Replace with your actual servo pin

# Stepper motor settings
X_STEPS_PER_MM = 20  # Update according to the microstepping mode
Y_STEPS_PER_MM = 20  # Update according to the microstepping mode
MAX_SPEED = 1000  # steps per second
DELAY_US = 1000000 // MAX_SPEED
ACCELERATION = 500  # steps per second squared

# Initialize stepper motor pins
x_step_pin = machine.Pin(X_STEP_PIN, machine.Pin.OUT)
x_dir_pin = machine.Pin(X_DIR_PIN, machine.Pin.OUT)
y_step_pin = machine.Pin(Y_STEP_PIN, machine.Pin.OUT)
y_dir_pin = machine.Pin(Y_DIR_PIN, machine.Pin.OUT)

# Initialize microstepping control pins
m1_pin = machine.Pin(M1_PIN, machine.Pin.OUT)
m2_pin = machine.Pin(M2_PIN, machine.Pin.OUT)
m3_pin = machine.Pin(M3_PIN, machine.Pin.OUT)

# Set microstepping mode to half-step (example)
m1_pin.value(1)  # HIGH
m2_pin.value(0)  # LOW
m3_pin.value(0)  # LOW

# Initialize servo motor
servo = machine.PWM(machine.Pin(SERVO_PIN), freq=50)

# Current position (x, y)
current_x = 0
current_y = 0

# Initialize UART
uart = machine.UART(0, baudrate=115200)

def set_direction(pin, steps):
    if steps > 0:
        pin.value(1)  # Forward direction
    else:
        pin.value(0)  # Backward direction

def step(pin):
    pin.value(1)
    utime.sleep_us(DELAY_US)
    pin.value(0)
    utime.sleep_us(DELAY_US)
    

def rapid_move_to(x, y):
    # Implement rapid move logic here
    # Calculate the number of steps required to move to (x, y)
    x_steps = int(x * X_STEPS_PER_MM)
    y_steps = int(y * Y_STEPS_PER_MM)

    # Set direction pins
    set_direction_pin(x_dir_pin, x_steps)
    set_direction_pin(y_dir_pin, y_steps)

    # Calculate absolute steps
    abs_x_steps = abs(x_steps)
    abs_y_steps = abs(y_steps)

    # Bresenham's line algorithm
    dx = abs_x_steps
    dy = abs_y_steps
    sx = 1 if x_steps > 0 else -1
    sy = 1 if y_steps > 0 else -1

    if dx > dy:
        err = dx / 2.0
        while abs_x_steps > 0:
            step(x_step_pin)
            err -= dy
            if err < 0:
                step(y_step_pin)
                err += dx
            abs_x_steps -= 1
    else:
        err = dy / 2.0
        while abs_y_steps > 0:
            step(y_step_pin)
            err -= dx
            if err < 0:
                step(x_step_pin)
                err += dy
            abs_y_steps -= 1

    pass

def linear_move_to(x, y):
    global current_x, current_y

    # Calculate the distance to move
    dx = x - current_x
    dy = y - current_y

    # Calculate the number of steps required
    x_steps = int(dx * X_STEPS_PER_MM)
    y_steps = int(dy * Y_STEPS_PER_MM)

    # Set the direction pins
    set_direction(x_dir_pin, x_steps)
    set_direction(y_dir_pin, y_steps)

    # Calculate total steps and the dominant axis
    abs_x_steps = abs(x_steps)
    abs_y_steps = abs(y_steps)
    total_steps = max(abs_x_steps, abs_y_steps)
    dominant_axis = abs_x_steps if abs_x_steps > abs_y_steps else abs_y_steps

    # Calculate acceleration and deceleration phases
    acceleration_steps = (dominant_axis // 2)
    deceleration_steps = dominant_axis - acceleration_steps

    # Initial delay for acceleration
    initial_delay = 1.0 / math.sqrt(2 * ACCELERATION)
    
    current_delay = initial_delay

    def get_speed_factor(step):
        if step < acceleration_steps:
            return (step / acceleration_steps)
        elif step >= (total_steps - deceleration_steps):
            return ((total_steps - step) / deceleration_steps)
        else:
            return 1.0

    x_counter = 0
    y_counter = 0

    for step in range(total_steps):
        speed_factor = get_speed_factor(step)
        delay = current_delay / speed_factor

        if x_counter >= (dominant_axis / abs_x_steps):
            step(x_step_pin)
            x_counter = 0
        if y_counter >= (dominant_axis / abs_y_steps):
            step(y_step_pin)
            y_counter = 0

        x_counter += abs_x_steps
        y_counter += abs_y_steps

        utime.sleep_us(int(delay * 1000000))

    # Update the current position
    current_x = x
    current_y = y

    pass

def clockwise_arc(x, y, radius, angle):
    # Implement clockwise arc logic here
    global current_x, current_y

    # Calculate the center of the arc
    center_x = current_x + radius * math.cos(math.radians(angle / 2))
    center_y = current_y + radius * math.sin(math.radians(angle / 2))

    # Calculate the number of steps required for the arc
    num_steps = int((angle / 360) * 2 * math.pi * radius * X_STEPS_PER_MM)

    # Initialize variables for the step counters
    x_counter = 0
    y_counter = 0

    for i in range(num_steps):
        theta = (angle / num_steps) * i
        x_pos = center_x + radius * math.cos(math.radians(theta + angle / 2))
        y_pos = center_y + radius * math.sin(math.radians(theta + angle / 2))

        # Calculate the number of steps required to move to the current position
        x_steps = int((x_pos - current_x) * X_STEPS_PER_MM)
        y_steps = int((y_pos - current_y) * Y_STEPS_PER_MM)

        # Set direction pins
        set_direction(x_dir_pin, x_steps)
        set_direction(y_dir_pin, y_steps)

        abs_x_steps = abs(x_steps)
        abs_y_steps = abs(y_steps)

        # Move the stepper motors
        while abs_x_steps > 0 or abs_y_steps > 0:
            if abs_x_steps > 0:
                step(x_step_pin)
                abs_x_steps -= 1
                x_counter += 1
            if abs_y_steps > 0:
                step(y_step_pin)
                abs_y_steps -= 1
                y_counter += 1

            # Delay to maintain speed
            utime.sleep_us(1000000 // MAX_SPEED)

        # Update the current position
        current_x = x_pos
        current_y = y_pos

    # Final position adjustment
    x_steps = int((x - current_x) * X_STEPS_PER_MM)
    y_steps = int((y - current_y) * Y_STEPS_PER_MM)

    set_direction(x_dir_pin, x_steps)
    set_direction(y_dir_pin, y_steps)

    abs_x_steps = abs(x_steps)
    abs_y_steps = abs(y_steps)

    while abs_x_steps > 0 or abs_y_steps > 0:
        if abs_x_steps > 0:
            step(x_step_pin)
            abs_x_steps -= 1
        if abs_y_steps > 0:
            step(y_step_pin)
            abs_y_steps -= 1

        # Delay to maintain speed
        utime.sleep_us(1000000 // MAX_SPEED)

    # Update the current position
    current_x = x
    current_y = y

    pass

def counter_clockwise_arc(x, y, radius, angle):
    global current_x, current_y

    # Calculate the center of the arc
    center_x = current_x - radius * math.cos(math.radians(angle / 2))
    center_y = current_y - radius * math.sin(math.radians(angle / 2))

    # Calculate the number of steps required for the arc
    num_steps = int((angle / 360) * 2 * math.pi * radius * X_STEPS_PER_MM)

    # Initialize variables for the step counters
    x_counter = 0
    y_counter = 0

    for i in range(num_steps):
        theta = (angle / num_steps) * i
        x_pos = center_x + radius * math.cos(math.radians(theta - angle / 2))
        y_pos = center_y + radius * math.sin(math.radians(theta - angle / 2))

        # Calculate the number of steps required to move to the current position
        x_steps = int((x_pos - current_x) * X_STEPS_PER_MM)
        y_steps = int((y_pos - current_y) * Y_STEPS_PER_MM)

        # Set direction pins
        set_direction(x_dir_pin, x_steps)
        set_direction(y_dir_pin, y_steps)

        abs_x_steps = abs(x_steps)
        abs_y_steps = abs(y_steps)

        # Move the stepper motors
        while abs_x_steps > 0 or abs_y_steps > 0:
            if abs_x_steps > 0:
                step(x_step_pin)
                abs_x_steps -= 1
                x_counter += 1
            if abs_y_steps > 0:
                step(y_step_pin)
                abs_y_steps -= 1
                y_counter += 1

            # Delay to maintain speed
            utime.sleep_us(1000000 // MAX_SPEED)

        # Update the current position
        current_x = x_pos
        current_y = y_pos

    # Final position adjustment
    x_steps = int((x - current_x) * X_STEPS_PER_MM)
    y_steps = int((y - current_y) * Y_STEPS_PER_MM)

    set_direction(x_dir_pin, x_steps)
    set_direction(y_dir_pin, y_steps)

    abs_x_steps = abs(x_steps)
    abs_y_steps = abs(y_steps)

    while abs_x_steps > 0 or abs_y_steps > 0:
        if abs_x_steps > 0:
            step(x_step_pin)
            abs_x_steps -= 1
        if abs_y_steps > 0:
            step(y_step_pin)
            abs_y_steps -= 1

        # Delay to maintain speed
        utime.sleep_us(1000000 // MAX_SPEED)

    # Update the current position
    current_x = x
    current_y = y

def pen_up():
    servo.duty(10)  # Adjust duty cycle for your servo to lift the pen up
    utime.sleep_ms(500)  # Adjust delay as needed

def pen_down():
    servo.duty(100)  # Adjust duty cycle for your servo to lower the pen down
    utime.sleep_ms(500)  # Adjust delay as needed

def dwell(p):
    utime.sleep_ms(p)

# G-code command dictionary
gcode_commands = {
    'G0': lambda params: rapid_move_to(float(params[0][1:]), float(params[1][1:])),  # Rapid move to (x, y)
    'G1': lambda params: linear_move_to(float(params[0][1:]), float(params[1][1:])),  # Linear move to (x, y)
    'G2': lambda params: clockwise_arc(float(params[0][1:]), float(params[1][1:])),  # Clockwise arc to (x, y)
    'G3': lambda params: counter_clockwise_arc(float(params[0][1:]), float(params[1][1:])),  # Counter-clockwise arc to (x, y)
    'M03': lambda params: pen_down(),  # Pen down
    'M05': lambda params: pen_up(),  # Pen up
    'G4': lambda params: dwell(int(params[0][1:]))  # Dwell for p milliseconds
}

# Read G-code from Universal G-code Sender
def read_gcode():
    gcode_input = uart.readline()
    if gcode_input:
        return gcode_input.decode('utf-8').strip()
    return None

# Execute G-code command
def execute_gcode_command(command, params):
    if command in gcode_commands:
        gcode_commands[command](params)
    else:
        print(f"Unknown command: {command}")

# Main G-code interpreter loop
while True:
    gcode_input = read_gcode()
    if gcode_input:
        parts = gcode_input.split()
        command = parts[0]
        params = parts[1:]
        execute_gcode_command(command, params)
