import time
import serial
from reading import Reading

# line has 117 bytes,
# payload has 80 bytes
# need to sleep 0.2 between readings

ser = serial.Serial()
ser.baudrate = 57600
ser.timeout = 3


ser.parity = serial.PARITY_EVEN

# freebsd:
ser.port = '/dev/cuaU0'

# linux:
# ser.port = '/dev/ttyU0'

# http://stackoverflow.com/questions/19317766/how-to-find-first-byte-of-a-serial-stream-with-python
# czytac do bufora a potem dalej rozbijac na linie

def process_line(line=None):
    if not line:
        return

    print('"{}"'.format(line))
    curr_time = line[0:8]
    curr_date = line[8:20].strip()
    curr_flow_raw = line[20:30].strip()
    curr_flow = curr_flow_raw.split('Wenty.=')[1]
    program_until = line[30:40].strip()
    displayed_temp = line[40:60].strip()
    curr_mode = line[60:80].strip()

    print('time:"{}"\ndate:"{}"\nflow_raw:"{}"\nflow:"{}"\nuntil:"{}"\ntemp:"{}"\nmode:"{}"'
          ''.format(curr_time,
                    curr_date, 
                    curr_flow_raw,
                    curr_flow,
                    program_until,
                    displayed_temp,
                    curr_mode))

try:
    x = ''
    cnt = 0
    ser.open()
    if ser.is_open:

        # prepare buffer
        while cnt < 3:
            x = ser.read(1)
            # print 'x=' + x
            if x == '<' or x == '(' or x == '>' or x == 'P':
                y = ser.read(117)
                cnt = cnt+1
        z = ser.read(12)

        # read actual lines
        while True:
            y = ser.read(117)
            print y
            line_stripped = y[5:-32]
            if len(line_stripped) < 80:
                continue
            process_line(line=line_stripped)
            time.sleep(0.2)

#        while True:
#            x = ser.read(117)
#            print x
#            time.sleep(0.2)

except Exception as ex:
    print('{}'.format(ex.message))
    ser.close()

except KeyboardInterrupt:
    print('Interrupt received, stopping')

finally:
    print('closing port')
    ser.close()
    print('Port is closed')


if ser.is_open:
    print('Port is still open - closing')
    ser.close()

