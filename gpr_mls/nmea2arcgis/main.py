import pynmea2


def readNMEA(nmea):
    file = open(nmea, 'r')
    messages = []

    for line in file.readlines():
        try:
            messages.append(pynmea2.parse(line))
        except pynmea2.ParseError as e:
            print('Parse error: {}'.format(e))
            continue

    return messages


path = r'D:\GPR_stuff\300622_testy_nach\10deg\trimble\przejazd_10stopni.txt'

nmea = readNMEA(path)
print(nmea)

new_path = path.split('\\')[-1][:-4] + '_ArcGIS.txt'

new_file = open(new_path, 'w')
for msg in nmea:
    # lat, long, NH, GPS_quality
    new_file.write('{},{},{},{}'.format(msg.latitude, msg.longitude, msg.altitude + float(msg.geo_sep), msg.gps_qual))
    new_file.write('\n')
    pass
