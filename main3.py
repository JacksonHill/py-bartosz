import time
import serial
from reading import Reading
import config

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

def process_line(line=None):
    if not line:
        return None

    #print("'{}'".format(line))
    raw_reading = {
        'curr_time': line[0:8],
        'curr_date': line[8:20].strip(),
        'curr_flow_raw': line[20:30].strip(),
        'curr_flow': line[20:30].strip().split('Wenty.=')[1],
        'program_until': line[30:40].strip(),
        'displayed_temp': line[40:60].strip(),
        'curr_mode': line[60:80].strip()
        }

    return raw_reading

try:
    x = ''
    cnt = 0
    ser.open()
    if ser.is_open:
        reading = Reading()

        # prepare buffer
        while cnt < 3:
            x = ser.read(1)
            #print (f'prep: {x}')
            #if x == b'<' or x == b'(' or x == b'>' or x == b'P':
            if x in (b'<', b'(', b'>', b'P'):
                y = ser.read(117)
                cnt = cnt+1
        z = ser.read(12)

        # read actual lines
        while True:
            y = ser.read(117)
            #print(y)
            line_stripped = y[5:-32]
            #print (f"line stripped: \n{line_stripped}")
            line_stripped = line_stripped.decode('iso8859-2')

            if len(line_stripped) < 80:
                continue
            raw = process_line(line=line_stripped)
            reading.fill_fields(**raw)
            if reading.is_complete():
                print("in: {} out: {} ext: {} time: {} flow: {}"
                      "".format(reading.inlet_temp,
                                reading.outlet_temp,
                                reading.external_temp,
                                reading.curr_time,
                                reading.curr_flow))
                print(reading.save(url=config.INFLUX_WRITE_URL))
                reading.clean()

            time.sleep(0.2)

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

