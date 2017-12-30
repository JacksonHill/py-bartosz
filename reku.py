import serial
import time

# linia ma 117 bajtow, 
# sleep 0.2 miedzy odczytami

ser = serial.Serial()
ser.baudrate = 57600
ser.timeout = 3

#ser.inWaiting - bytes to read?

ser.parity = serial.PARITY_EVEN
ser.port = '/dev/cuaU0'
#ser.port = '/dev/ttyU0'
# http://stackoverflow.com/questions/19317766/how-to-find-first-byte-of-a-serial-stream-with-python
# czytac do bufora a potem dalej rozbijac na linie
try:
    x = ''
    cnt = 0
    ser.open()
    if ser.is_open:
        #while x != '<' or x != '('
        while cnt<3:
            x = ser.read(1)
            print 'x=' + x
            if x == '<' or x == '(' or x == '>' or x == 'P':
                y = ser.read(117)
                cnt = cnt+1
         #   time.sleep(0.2)
        z = ser.read(12)
        while True: 
            y = ser.read(117) 
            print 'y = ' + y
            time.sleep(0.2)

#        while True:
#            x = ser.read(117)
#            print x
#            time.sleep(0.2)

except Exception as ex:
	print ex.message
	ser.close()
except:
    print 'Port is closed'
    ser.close()

if ser.is_open:
    print 'Port is open - closing'
    ser.close()
