import pynmea2
import datetime as dt
import statistics

import tqdm


def readTimestamp(tmstp_file):
    file = open(tmstp_file, 'r')
    timestamps = []

    for line in file.readlines():
        line = (line.replace(':', ''))
        timestamps.append(line[-10:-1])
    timestamps = timestamps[5:]

    final = []
    for i in range(len(timestamps)):
        hh = int(timestamps[i][0:2])
        mm = int(timestamps[i][2:4])
        ss = int(timestamps[i][4:6])
        dd = round(int(timestamps[i][6:]) * 1000, -4)
        stamp = dt.time(hh, mm, ss, dd)
        final.append(stamp)

    return final


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

#### interpolacja
def interpolation(timestamp, nmea):
    prev = -1
    for i in range(len(nmea)):
        if timestamp > nmea[i].timestamp:
            prev += 1
        else:
            break
    prev = prev
    next = prev + 1

    # print('####' * 10)
    # print('Previous NMEA: {}'.format(nmea[prev]))
    # print('Timestamp: {}'.format(timestamp))
    # print('Next NMEA: {}'.format(nmea[next]))
    # print('####' * 10)

    prev_nmea = nmea[prev]
    next_nmea = nmea[next]

    def time2ms(time):
        tms = time.microsecond / 1000000 + time.second + time.minute * 60 + time.hour * 60 * 60
        return tms

    time_delta = time2ms(timestamp) - time2ms(prev_nmea.timestamp)
    time_delta_base = time2ms(next_nmea.timestamp) - time2ms(prev_nmea.timestamp)
    # latitude
    lat = float(prev_nmea.lat) + ((float(next_nmea.lat) - float(prev_nmea.lat)) / time_delta_base) * time_delta
    lat = round(lat, 8)

    # latitude dir
    if prev_nmea.lat_dir == next_nmea.lat_dir:
        lat_dir = prev_nmea.lat_dir
    else:
        lat_dir = 'error'

    # longitude
    lon = float(prev_nmea.lon) + ((float(next_nmea.lon) - float(prev_nmea.lon)) / time_delta_base) * time_delta
    lon = round(lon, 8)

    # longitude dir
    if prev_nmea.lon_dir == next_nmea.lon_dir:
        lon_dir = prev_nmea.lon_dir
    else:
        lon_dir = 'error'

    # gps quality
    if prev_nmea.gps_qual == '4' and next_nmea.gps_qual == '4':
        gps_qual = 4
    else:
        gps_qual = 0

    # number of satelite
    num_sats = int(statistics.mean([int(prev_nmea.num_sats), int(next_nmea.num_sats)]))
    num_sats = str(round(num_sats, 0))

    # HDOP
    horizontal_dil = statistics.mean([float(prev_nmea.horizontal_dil), float(next_nmea.horizontal_dil)])
    horizontal_dil = round(horizontal_dil, 1)

    # altitude
    altitude = statistics.mean([float(prev_nmea.altitude), float(next_nmea.altitude)])

    # altitude units
    if prev_nmea.altitude_units == next_nmea.altitude_units:
        altitude_units = prev_nmea.altitude_units
    else:
        altitude_units = 'error'

    # geoid separation
    geo_sep = statistics.mean([float(prev_nmea.geo_sep), float(next_nmea.geo_sep)])

    # geoid separation units
    if prev_nmea.geo_sep_units == next_nmea.geo_sep_units:
        geo_sep_units = prev_nmea.geo_sep_units
    else:
        geo_sep_units = 'error'

    # age of gps data
    age_gps_data = float(prev_nmea.age_gps_data) + time_delta

    # station reference id
    if prev_nmea.ref_station_id == next_nmea.ref_station_id:
        ref_station_id = prev_nmea.ref_station_id
    else:
        ref_station_id = '0000'

    return lat, lat_dir, lon, lon_dir, gps_qual, num_sats, horizontal_dil, altitude, altitude_units, geo_sep, geo_sep_units, age_gps_data, ref_station_id


def writeNMEA(timestamps, nmea, new_file_name):
    file = open(new_file_name, 'w')

    ts_nmea = []
    for msg in nmea:
        ts_nmea.append(msg.timestamp)

    for timestamp in timestamps:

        if timestamp in ts_nmea:
            for msg in nmea:
                if timestamp == msg.timestamp:
                    file.write(str(msg) + '\n')
        else:
            file.write('$GNGGA,')
            hhmmss = str(timestamp.hour).zfill(2) + str(timestamp.minute).zfill(2) + str(timestamp.second).zfill(2)
            hhmmss_ss = round(int(hhmmss) + timestamp.microsecond / 1000000, 2)
            hhmmss_ss = '{:.2f}'.format(hhmmss_ss)
            file.write(hhmmss_ss.zfill(9) + ',')
            lat, lat_dir, lon, lon_dir, gps_qual, num_sats, horizontal_dil, altitude, altitude_units, geo_sep, geo_sep_units, age_gps_data, ref_station_id = interpolation(timestamp, nmea)
            file.write('{:.8f},{},'.format(lat, lat_dir))
            lon = '{:.8f}'.format(lon)
            lon = lon.zfill(14)
            file.write('{},{},'.format(lon, lon_dir))
            file.write('{},{},{},'.format(gps_qual, num_sats.zfill(2), horizontal_dil))
            file.write('{:.3f},{},{:.3f},{},'.format(round(altitude, 3), altitude_units, round(geo_sep, 3), geo_sep_units))
            file.write('{},{}*XD'.format(round(age_gps_data, 1), ref_station_id))
            file.write('\n')
