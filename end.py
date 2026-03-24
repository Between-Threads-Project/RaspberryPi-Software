import pigpio

import utils

pi = pigpio.pi()

if not pi.connected:
    raise RuntimeError("pigpio daemon not running")

utils.initialize_servos(pi)
utils.set_servos_to_full(pi)

pi.stop()
print("Servos initialized and set to 180°")
