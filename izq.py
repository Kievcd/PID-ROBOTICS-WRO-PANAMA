import RPi.GPIO as GPIO
import time
import threading

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Configuración de los pines GPIO para el módulo MD08A
pin_in1 = 16
pin_in2 = 18
pin_pwma = 32
pin_stby = 37

# Configuración del pin GPIO para el servo
PIN_SERVO = 12
GPIO.setup(PIN_SERVO, GPIO.OUT)
servo = GPIO.PWM(PIN_SERVO, 50)  # Frecuencia de 50 Hz para la mayoría de los servos

# Configuración de los pines GPIO para el primer sensor ultrasónico
PIN_TRIGGER1 = 11
PIN_ECHO1 = 13
GPIO.setup(PIN_TRIGGER1, GPIO.OUT)
GPIO.setup(PIN_ECHO1, GPIO.IN)

# Configuración de los pines GPIO para el segundo sensor ultrasónico
PIN_TRIGGER2 = 29
PIN_ECHO2 = 31
GPIO.setup(PIN_TRIGGER2, GPIO.OUT)
GPIO.setup(PIN_ECHO2, GPIO.IN)

def set_servo_angle(angle):
    # Limitar el rango del ángulo entre 0 y 180 grados
    angle = max(0, min(180, angle))
    
    # Función para configurar el ángulo del servo
    duty = 2.5 + (angle / 180) * 10
    GPIO.output(PIN_SERVO, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.2)  # Permite tiempo para que el servo alcance la posición
    GPIO.output(PIN_SERVO, False)
    servo.ChangeDutyCycle(0)

def stop_motor():
    GPIO.output(pin_in1, GPIO.LOW)
    GPIO.output(pin_in2, GPIO.LOW)

def forward(duration_giro):
    # Función para girar el motor hacia adelante durante una duración específica
    GPIO.setup(pin_in1, GPIO.OUT)
    GPIO.setup(pin_in2, GPIO.OUT)
    GPIO.output(pin_in1, GPIO.HIGH)
    GPIO.output(pin_in2, GPIO.LOW)
    pwm.start(100)
    time.sleep(duration_giro)
    pwm.stop()

def get_distance(trigger_pin, echo_pin):
    # Función para obtener la distancia del sensor ultrasónico
    GPIO.output(trigger_pin, True)
    time.sleep(0.000001)
    GPIO.output(trigger_pin, False)
    
    pulse_start = time.time()
    pulse_end = time.time()
    
    while GPIO.input(echo_pin) == 0:
        pulse_start = time.time()
        
    while GPIO.input(echo_pin) == 1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 1)
    
    return distance

try:
    # Configura los pines GPIO como salidas para el módulo MD08A
    GPIO.setup(pin_in1, GPIO.OUT)
    GPIO.setup(pin_in2, GPIO.OUT)
    GPIO.setup(pin_pwma, GPIO.OUT)
    GPIO.setup(pin_stby, GPIO.OUT)

    # Crea un objeto PWM para controlar el pin PWMA (para el motor)
    pwm = GPIO.PWM(pin_pwma, 1000)  # 1000 Hz como frecuencia PWM

    # Activa el STBY para activar los motores
    GPIO.output(pin_stby, GPIO.HIGH)

    servo.start(0)  # Inicializa el servo en posición 0 grados (inicio)
    set_servo_angle(115)  # Mueve el servo a 90 grados (posición inicial en el centro)
    time.sleep(1)  # Espera 2 segundos antes de continuar
    

    def motor_thread():
        while True:
            forward(45)

    def sensor_thread():
        deten = 0
        while deten <=12:
            dist_right = get_distance(PIN_TRIGGER2, PIN_ECHO2)  # Obtiene la distancia del primer sensor
            dist_left = get_distance(PIN_TRIGGER1, PIN_ECHO1)  # Obtiene la distancia del segundo sensor
            
            print("Distancia izquierda: {} cm, Distancia derecha: {} cm".format(dist_left, dist_right))
            print("contador: ",deten)
            #if dist_right < 40 or dist_left < 40:  # Si cualquiera de los sensores detecta una distancia menor a 40 cm
                #set_servo_angle(0)  # Gira a la izquierda (ángulo de 0 grados)
                #print("izq")
                
            if dist_left > 90:
                set_servo_angle(0)
                time.sleep(0.4)
                set_servo_angle(115)
                time.sleep(2.5)
                deten = deten + 1
                
            elif dist_left < 10.5:
                set_servo_angle(175)
                time.sleep(.3)
                set_servo_angle(115)
                time.sleep(.5)
                
            elif dist_right < 10.5:
                set_servo_angle(0)
                time.sleep(.3)
                set_servo_angle(115)
                time.sleep(.5)
                
            elif deten == 12:
                forward(.5)
                stop_motor()
                servo.stop()
                GPIO.cleanup()
            else:
                set_servo_angle(115)  # Vuelve al centro (ángulo de 90 grados)
            
            time.sleep(.1)  # Espera 0.3 segundos antes de tomar otra lectura del sensor
            #stop_motor()

    motor_thread = threading.Thread(target=motor_thread)
    sensor_thread = threading.Thread(target=sensor_thread)

    motor_thread.start()
    sensor_thread.start()

    #while True:
        #time.sleep(1)  # Espera para mantener el programa ejecutándose

except KeyboardInterrupt:
    # Detener el servo y limpiar los pines GPIO al presionar Ctrl + C
    servo.stop()
    GPIO.cleanup()
