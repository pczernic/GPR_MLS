import laspy
import numpy as np
import math as m


def createGPS(txt, nameDAT, nameGPS, pp, pk):
    read = open(txt, 'r')
    data = read.readlines()
    read.close()

    sep_data = []
    for i in range(len(data)):
        data[i] = data[i][:-1].replace('\t', ' ').split(' ')
        sep_data.append(data[i])

    x = {}
    y = {}
    h = {}

    for i in range(len(sep_data)):
        sep_data[i][1] = float(sep_data[i][1])
        sep_data[i][2] = float(sep_data[i][2])
        sep_data[i][3] = float(sep_data[i][3])
        x[sep_data[i][0]] = sep_data[i][1]
        y[sep_data[i][0]] = sep_data[i][2]
        h[sep_data[i][0]] = sep_data[i][3]

    _, _, dat_sep = wczytanieDAT(nameDAT)
    samples = int(dat_sep[-1][0])

    dx = (x[pk] - x[pp])/(samples-1)
    dy = (y[pk] - y[pp])/(samples-1)
    dh = (h[pk] - h[pp])/(samples-1)

    line_x = {}
    line_y = {}
    line_h = {}

    for i in range(samples):
        line_x[i] = round(x[pp]+i*dx, 3)
        line_y[i] = round(y[pp]+i*dy, 3)
        line_h[i] = round(h[pp]+i*dh, 3)

    with open(nameGPS, 'w') as file:
        file.write(f'Source File=xxx\n')
        file.write(f'################\n')
        file.write(f'Trace No= NMEI\n')
        for i in range(len(line_x)):
            file.write(f'{i},$GNGGA,0.0,{line_x[i]},N,{line_y[i]},E,4,0,0.0,{line_h[i]},M,0.000,M,0.0,0000*55\n'.format())


def wczytywanieGPS(nazwa):
    try:
        read = open(nazwa, 'r')
    except FileNotFoundError:
        return 'FileNotFound'

    dane = read.readlines()
    read.close()
    dane = dane[3::]
    rozdzielone = {}

    for i in range((len(dane))):
        dane[i] = dane[i][0:-1].replace('\t', ',').split(',')
        dane[i] = [int(dane[i][0]), str(dane[i][2]), float(dane[i][3]), float(dane[i][5]), int(dane[i][7]), int(dane[i][8]), float(dane[i][9]), float(dane[i][10]), float(dane[i][12])]
        #               trace       UTC of positon      Latitude        Longtitude        GPS Quality     number of satelites      HDOP             Ortometic H      Geoid separation
        # 	GPS Quality indicator:
        # 0: Fix not valid
        #
        # 1: GPS fix
        #
        # 2: Differential GPS fix, OmniSTAR VBS
        #
        # 4: Real-Time Kinematic, fixed integers
        #
        # 5: Real-Time Kinematic, float integers, OmniSTAR XP/HP or Location RTK
        if dane[i][4] == 4:     #wybieranie tylko fixów
            rozdzielone[dane[i][0]] = dane[i][1::]


    return rozdzielone


def wgs84(dictionary):
    pol0 = 21

    L0 = pol0 * m.pi / 180
    a = 6378137
    e2 = 0.00669438002290
    for i in dictionary.keys():
        Bdeg = int(str(dictionary[i][1])[0:2])
        Bmin = float(str(dictionary[i][1])[2::])
        Brad = Bdeg * m.pi / 180 + Bmin * m.pi / (180 * 60)

        Ldeg = int(str(dictionary[i][2])[0:2])
        Lmin = float(str(dictionary[i][2])[2::])
        Lrad = Ldeg * m.pi / 180 + Lmin * m.pi / (180 * 60)

        dL = Lrad - L0
        b2 = (a ** 2)*(1 - e2)
        ep2 = (a ** 2 - b2) / b2
        t = m.tan(Brad)
        eta2 = ep2 * m.cos(Brad) ** 2

        N = a / m.sqrt(1 - e2 * m.sin(Brad) ** 2)

        A0 = 1 - (e2 / 4) - (3*e2 ** 2 / 64) - (5*e2 ** 3 / 256)
        A2 = (3 / 8) *(e2 + (e2 ** 2 / 4) + ((15*e2 ** 3) / 128))
        A4 = 15 / 256 * (e2 ** 2 + (3 * e2 ** 3 / 4))
        A6 = 35 * e2 ** 3 / 3072

        sig = a*(A0*Brad - A2* m.sin(2* Brad)+A4*m.sin(4*Brad)-A6* m.sin(6*Brad))

        Xgk = sig + (dL ** 2 / 2)*N*m.sin(Brad)*m.cos(Brad)*(1 + (dL ** 2 / 12)*m.cos(Brad) ** 2*(5 - t ** 2 + 9*eta2 + 4*eta2 ** 2)+(dL ** 4 / 360)*m.cos(Brad) ** 4*(61 - 18*t ** 2 + t ** 4 + 270*eta2 - 330 * eta2 * t ** 2))
        Ygk = dL* N* m.cos(Brad)*(1 + dL ** 2 / 6 * m.cos(Brad) ** 2*(1 - t ** 2 + eta2) + dL ** 4 / 120 * m.cos(Brad) ** 4*(5 - 18*t ** 2 + t ** 4 + 14*eta2 - 58*eta2*t ** 2))

        m0 = 0.999923
        X2000 = m0 * Xgk
        Y2000 = m0 * Ygk + 500000 + 7 * 1000000


        dictionary[i].append(X2000)
        dictionary[i].append(Y2000)

    return dictionary


def interpolacja_trace(dictionary):
    interpolowane = {}
    keys = list(dictionary.keys())

    for i in range(len(keys)-1):
        b = keys[i + 1]
        a = keys[i]
        step = b - a
        if step == 1:
            continue
        else:
            dX = (dictionary[b][-2] - dictionary[a][-2])/step
            dY = (dictionary[b][-1] - dictionary[a][-1])/step
            dH = (dictionary[b][-4] - dictionary[a][-4] + dictionary[b][-3] - dictionary[a][-3])/step
            for z in range(step-1):
                z += 1
                interpolowane[a + z] = [dictionary[a][-2] + z * dX, dictionary[a][-1] + z * dY, (dictionary[a][-4] +  dictionary[a][-3])+ z * dH]

    return interpolowane


def same_xy_z_bazowego_slownika(dictionary):
    same_xyh = {}
    for i in list(dictionary.keys()):
        same_xyh[i] = [dictionary[i][1], dictionary[i][2], dictionary[i][-2]]
    return same_xyh


def wczytanieDAT(nazwa):
    read = open(nazwa, 'r')
    dane = read.readlines()
    read.close()
    try:
        # print('v1')
        depth = float(dane[5][13:-3].replace(',', '.'))     ## 16 dla starych, 13 nowe
        samples = int(dane[1][9::])     ## 7 dla starych , 9 nowe
        # print(depth, samples)
    except ValueError:
        # print('v2')
        depth = float(dane[5][16:-3].replace(',', '.'))  ## 16 dla starych, 13 nowe
        samples = int(dane[1][7::])  ## 7 dla starych , 9 nowe
        # print(depth, samples)

    dane = dane[7::]
    rozdzielone = []
    for i in range((len(dane))):
        dane[i] = dane[i][0:-1].replace('\t', ',').split(',')
        rozdzielone.append(dane[i])

    return samples, depth, rozdzielone


def wyznaczanie_wspolrzednych(name1, samples, depth, lista, slownik, file_name):
    last = int(list(slownik.keys())[-1])
    multiplayer = float(depth/samples)
    x_ostateczne = []
    y_ostateczne = []
    h_ostateczne = []
    amplitude = []
    for i in lista:
        temp = int(i[0])
        if temp > last:
            break

        try:
            h_ostateczne.append(slownik[temp][2] - int(i[1]) * multiplayer)

            x_ostateczne.append(slownik[temp][0])
            y_ostateczne.append(slownik[temp][1])
            amplitude.append(int(i[2]))

        except KeyError:
            continue
    # print(h_ostateczne)
    numeracja = list(slownik.keys())
    x_all = []
    y_all = []
    for i in numeracja:
        x_all.append(slownik[i][0])
        y_all.append(slownik[i][1])

    with open(name1 + '/Trajektorie/' + file_name + '.csv', 'w') as f:
        for i in range(len(x_all)):
            f.write("{},    {}\n".format(x_all[i], y_all[i]))

    return x_ostateczne, y_ostateczne, h_ostateczne, amplitude


def create_las(dir, file_name, x, y, h, a):
    name = dir + '/' + file_name + '.las'
    header = laspy.LasHeader(point_format=3, version="1.2")
    header.add_extra_dim(laspy.ExtraBytesParams(name="Amplitude", type=np.int32))
    las = laspy.LasData(header)

    allx = np.array(y)  # Four Points
    ally = np.array(x)
    allz = np.array(h)

    an = []
    for i in a:
        an.append(int(i))

    alla = np.array(an)

    try:
        xmin = np.floor(np.min(allx))
        ymin = np.floor(np.min(ally))
        zmin = np.floor(np.min(allz))
        amin = np.min(alla)

        header.offsets = [xmin, ymin, zmin, amin]      # , amin]
        header.scale = [0.001, 0.001, 0.001, 1]  # ,1]

        las.x = allx
        las.y = ally
        las.z = allz
        las.Amplitude = alla
    except ValueError:
        pass

    las.write(name)
    return name

