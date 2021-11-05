import time
import matplotlib.pyplot as plt
from simple_pid import PID


import traceback
import logging
from lib.temperaturesensor_MAXIM import temperaturesensor_MAXIM as Tsensor


# heater class (dummy):
class heaterblock:

	def __init__(self, PSU_port, PSU_type, TSENS_port, resistance, KP, KI, KD):
	
		# connect / configure PSU:
		try:
			print('Trying to configure PSU...')
			
		except Exception as e:
			logging.error(traceback.format_exc())
		
		# connect / configure T sensor:
		try:
			print('Trying to configure T sensor...')
			self._TSENS = Tsensor(TSENS_port , romcode = '')
			print('Bingo!')

		except Exception as e:
			logging.error(traceback.format_exc())
		
		# set heater resistance:
		self._heater_R = resistance
		
		# set PID parameters:
		self._KP = KP
		self._KI = KI
		self._KD = KD
				

	def read_temp(self):
		# read T sensor and return result

		temp,unit = self._TSENS.temperature()
		if unit is not 'deg.C':
			raise ValueError('T value has wrong unit (' + unit + ').')
		return temp
        

	def update(self, power, dt):
	
		## dt = 10 * dt # speed up time (for dummy purposes)

		# read T sensor:
		T = self.read_temp()

		# heat loss due to cooling:
		T -= 0.5 * (T-self.temp_amb) * dt / self.C_heat

		# heat input:
		if power > 0:
			T += power * dt / self.C_heat

		# set new T value (dummy):
		self.temp = T

		return T



### MAIN



print ('**** SHOULD READ CONFIG FILE HERE... ****')



T0       = 25		# Initial temperature of the heater (°C)
T_target = 30		# Target temperature of the heater (°C)
P_max    = 36*12	# Max heating power (Watt)

# init heaterblock object:
heater = heaterblock( PSU_port = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0010-if00-port0',
                      PSU_type = 'VOLTCRAFT',
                      TSENS_port =  '/dev/serial/by-id/usb-FTDI_TTL232R-3V3_FTBZLSUL-if00-port0',	
                      resistance = 3,
                      KP = 20000,
                      KI = 0.4,
                      KD = 0.0 )

# init PID controller:
## pid = PID(Kp=1, Ki=0.01, Kd=0.1)



# THIS SHOULD GO INTO THE HEATERBLOCK OBJECT/CLASS:
# Determine the PID paramters: https://en.wikipedia.org/wiki/PID_controller#Manual_tuning
pid = PID(Kp=20000, Ki=0.35, Kd=0.0)


pid.output_limits = (0, P_max)
pid.setpoint = T_target

# time parameters
start_time = time.time()
last_time  = start_time

# data for plotting:
setpoint, y, x = [], [], []

T = T0

while time.time() - start_time < 30: 
       	
	#Setting the time variable dt
	current_time = time.time()
	dt = (current_time - last_time)

	# determine heating power for next step:
	power = pid(T)
        
	print(power)
	print(T-pid.setpoint)
	print("\n")
        
	# update heater block (set power, get temperature):
	T = heater.update(power, dt)
        
	#Visualize Output Results
	x += [current_time - start_time]
	y += [T]
	setpoint += [pid.setpoint]
	
	#Used for initial value assignment of variable temp
        #if current_time - start_time > 0:
        #    pid.setpoint = 100

	last_time = current_time


# Visualization of Output Results
plt.plot(x, setpoint, label='target')
plt.plot(x, y, label='PID')
plt.xlabel('time')
plt.ylabel('temperature')
plt.legend()
plt.show()
