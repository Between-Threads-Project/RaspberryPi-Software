import pigpio

from core.utils import initialize_servos, set_servos_to_zero

pi = pigpio.pi()

if not pi.connected:
    raise RuntimeError("pigpio daemon not running")

initialize_servos(pi)
set_servos_to_zero(pi)

pi.stop()
print("Clean exit")
