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


def process_line(line=None):
    if not line:
        return None
    if len(line) < 80:
        return None

    #print(f"\n'{line}'\n")

    curr_time = line[0:8]
    curr_date = line[8:20].strip()
    curr_flow_raw =  line[20:30].strip()
    curr_flow_splitted = curr_flow_raw.split('Wenty.=')
    if len(curr_flow_splitted) > 1:
        curr_flow = curr_flow_splitted[1]
    else:
        return None
    program_until = line[30:40].strip()
    displayed_temp = line[40:60].strip()
    curr_mode = line[60:80].strip()

    raw_reading = {
        'curr_time': curr_time,
        'curr_date': curr_date,
        'curr_flow_raw': curr_flow_raw,
        'curr_flow': curr_flow,
        'program_until': program_until,
        'displayed_temp': displayed_temp,
        'curr_mode': curr_mode
    }

    return raw_reading

try:
    x = ''
    cnt = 0
    ser.open()
    buff = []
    if ser.is_open:
        reading = Reading()

        while True:
            x = ser.read(1)
            #print(f"{x}\n)"
            if x == b'\xff':
                cnt +=1
            else:
                if cnt > 3:
                    buff.append(x.decode('iso8859-2'))
                    time.sleep(0.01)
                    # possible optimalisation - read whole line instead of one char at a time
                    #buff.append(ser.read(81).decode('iso8859-2'))

            if len(buff) > 81:
                linebuff = "".join(buff)
                #print(linebuff)
                if 'Wenty.=' in linebuff and 'Temp' in linebuff and 'Tryb' in linebuff:
                    raw = process_line(linebuff)
                    #print(raw)
                    if not raw:
                        buff = []
                        cnt = 0
                        continue
                    reading.fill_fields(**raw)
                    if reading.is_complete():
                        print("in: {} out: {} ext: {} time: {} flow: {}"
                              "".format(reading.inlet_temp,
                                        reading.outlet_temp,
                                        reading.external_temp,
                                        reading.curr_time,
                                        reading.curr_flow))
                        influx_status = reading.save(url=config.INFLUX_WRITE_URL)
                        print(f'Point saved: {influx_status}')
                        reading.clean()
            #       #print("BUFF END")
                    buff = []
                    cnt = 0
            continue

            #time.sleep(0.2)

except AttributeError:
    pass

except Exception as ex:
    print(f'{ex} {ex.message}')
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
