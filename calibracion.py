import RPi.GPIO as GPIO
import time

# Configuración del pin GPIO para el servo
PIN_SERVO = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_SERVO, GPIO.OUT)
servo = GPIO.PWM(PIN_SERVO, 50)  # Frecuencia de 50 Hz para la mayoría de los servos

# Función para mover el servo a un ángulo específico (0 a 180 grados)
def set_servo_angle(angle):
    angle = max(0, min(180, angle))
    duty = 2.5 + (angle / 90) * 10
    GPIO.output(PIN_SERVO, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.5)  # Permite tiempo para que el servo alcance la posición
    GPIO.output(PIN_SERVO, False)
    servo.ChangeDutyCycle(0)  # Detiene el servo

# Función de calibración del servo
def calibration():
    # Mover el servo de 0 a 180 grados para calibrar
    for angle in range(30, 90, 10):
        set_servo_angle(angle)
    
    # Dejar el servo centrado (ángulo de 90 grados)
    set_servo_angle(10)

try:
    # Iniciar el objeto PWM del servo
    servo.start(0)
    
    calibration()  # Realizar la calibración al encender el programa

    # Aquí podrías agregar el código principal para que el robot funcione de acuerdo a tus necesidades

except KeyboardInterrupt:
    # Detener el servo y liberar los pines GPIO en caso de interrupción (Ctrl+C)
    servo.stop()
    GPIO.cleanup()
