import functions as f


nmea_file = r'C:\Users\admin1\Desktop\GPR_MLS\NMEA_to_Prism2\NMEA.txt'
timestamp_file = r'C:\Users\admin1\Desktop\GPR_MLS\NMEA_to_Prism2\testtimestamp.txt'

timestamps = f.readTimestamp(timestamp_file)

nmea = f.readNMEA(nmea_file)

f.writeNMEA(timestamps, nmea, 'newNMEA.txt')




