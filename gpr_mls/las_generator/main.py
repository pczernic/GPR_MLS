import functions
import os
import filters
# from tqdm import tqdm
# from time import sleep

for i in range(5, 6):
    for j in range(1, 5):
        try:
            print(i, j)
            object_no = 'p'+str(i)+'.txt'
            profile_no = int(j)
            file_name = '2022_1_22_plyta' + str(object_no[1]) + str(profile_no) + ' velocity 130'

            las_name = object_no[0:-4] + str(profile_no)

            if profile_no == 1:
                pp = str(1)
                pk = str(6)
            elif profile_no == 2:
                pp = str(16)
                pk = str(7)
            elif profile_no == 3:
                pp = str(15)
                pk = str(8)
            elif profile_no == 4:
                pp = str(14)
                pk = str(9)
            elif profile_no == 5:
                pp = str(1)
                pk = str(14)
            elif profile_no == 6:
                pp = str(2)
                pk = str(13)
            elif profile_no == 7:
                pp = str(3)
                pk = str(12)
            elif profile_no == 8:
                pp = str(4)
                pk = str(11)
            elif profile_no == 9:
                pp = str(5)
                pk = str(10)
            elif profile_no == 10:
                pp = str(6)
                pk = str(9)
            else:
                print('Nie ma takiego profilu!')

            name1 = 'PointClouds'

            try:
                os.mkdir(name1)
                print("Directory ", name1, " Created ")
            except FileExistsError:
                print("Directory ", name1, " already exists")

            try:
                os.mkdir(name1+"/Trajektorie")
                print("Directory Trajektorie Created ")
            except FileExistsError:
                print("Directory Trajektorie already exists")

            nameGPS = file_name + '.gps'
            nameDAT = file_name + '.dat'

            functions.createGPS(object_no, nameDAT, nameGPS, pp, pk)

            dane = functions.wczytywanieGPS(nameGPS)

            wsp_all = functions.same_xy_z_bazowego_slownika(dane)

            samples, depth, rows = functions.wczytanieDAT(nameDAT)

            x, y, h, amp = functions.wyznaczanie_wspolrzednych(name1, samples, depth, rows, wsp_all, file_name)

            name = functions.create_las(name1, las_name, x, y, h, amp)

            filters.depth_limit(name, 0.2)

            filters.rectifier(name, 'pos')

            filters.threshold(name, 5000)

            # filters.display_inlier_outlier(name, 5)

        except FileNotFoundError:
            print(f"################### NIe ma profilu {i} {j} ###################")
