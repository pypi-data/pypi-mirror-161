import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import warnings

# ---------------------------------Platonic Solid Model--------------------------------------


def distance(a: float, b: float):
    # a seperated function for calculating the distance between two coordinates
    n = 15
    return round(((a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2)**0.5, n)


def mid_pt(a: float, b: float):
    # this is a seperate function for calculating mid point of two coords
    n = 15
    return [round((a[0]+b[0])/2, n), round((a[1]+b[1])/2, n), round((a[2]+b[2])/2, n)]


def angle_cal(COM1: float, leg1: float, COM2: float, leg2: float):
    n = 8
    c1 = np.array(COM1)
    p1 = np.array(leg1)
    c2 = np.array(COM2)
    p2 = np.array(leg2)
    v1 = p1 - c1
    v2 = p2 - c2
    sig1 = p1 - p2
    sig2 = -sig1
    theta1 = round(math.acos(np.dot(v1, sig1) /
                   (np.linalg.norm(v1)*np.linalg.norm(sig1))), n)
    theta2 = round(math.acos(np.dot(v2, sig2) /
                   (np.linalg.norm(v2)*np.linalg.norm(sig2))), n)
    t1 = np.cross(v1, sig1)
    t2 = np.cross(v1, c1)  # n1 = c1 here
    t1_hat = t1/np.linalg.norm(t1)
    t2_hat = t2/np.linalg.norm(t2)
    phi1 = round(math.acos(np.around(np.dot(t1_hat, t2_hat), n)), n)
    t3 = np.cross(v2, sig2)
    t4 = np.cross(v2, c2)  # n2 = c2 here
    t3_hat = t3/np.linalg.norm(t3)
    t4_hat = t4/np.linalg.norm(t4)
    phi2 = round(math.acos(np.around(np.dot(t3_hat, t4_hat), n)), n)
    t1_ = np.cross(sig1, v1)
    t2_ = np.cross(sig1, v2)
    t1__hat = t1_/np.linalg.norm(t1_)
    t2__hat = t2_/np.linalg.norm(t2_)
    omega = round(math.acos(np.around(np.dot(t1__hat, t2__hat), n)), n)
    return theta1, theta2, phi1, phi2, omega


# DODECAHEDEON FACE AS COM

def dode_face_dodecahedron_coord(radius: float):
    # Setup coordinates of 20 verticies when scaler = 1
    scaler = radius/(3**0.5)
    m = (1+5**(0.5))/2
    V1 = [0, m, 1/m]
    V2 = [0, m, -1/m]
    V3 = [0, -m, 1/m]
    V4 = [0, -m, -1/m]
    V5 = [1/m, 0, m]
    V6 = [1/m, 0, -m]
    V7 = [-1/m, 0, m]
    V8 = [-1/m, 0, -m]
    V9 = [m, 1/m, 0]
    V10 = [m, -1/m, 0]
    V11 = [-m, 1/m, 0]
    V12 = [-m, -1/m, 0]
    V13 = [1, 1, 1]
    V14 = [1, 1, -1]
    V15 = [1, -1, 1]
    V16 = [1, -1, -1]
    V17 = [-1, 1, 1]
    V18 = [-1, 1, -1]
    V19 = [-1, -1, 1]
    V20 = [-1, -1, -1]
    coord = [V1, V2, V3, V4, V5, V6, V7, V8, V9, V10,
             V11, V12, V13, V14, V15, V16, V17, V18, V19, V20]
    # calculate coordinates according to the scaler as coord_ (list)
    coord_ = []
    for i in coord:
        temp_list = []
        for j in i:
            temp = j*scaler
            temp_list.append(temp)
        coord_.append(temp_list)
    return coord_


def dode_face_COM_coor(a: float, b: float, c: float, d: float, e: float):
    # calculate the center of mass(COM) according to 5 coords on the same face
    n = 10
    mid_a = mid_pt(c, d)
    mid_b = mid_pt(d, e)
    mid_c = mid_pt(a, e)
    COM_a = []
    COM_b = []
    COM_c = []
    # calculate 3 COM here and check if they are overlapped
    for i in range(0, 3):
        COM_a.append(round(a[i] + (mid_a[i] - a[i]) /
                     (1+math.sin(0.3*math.pi)), 14))
        COM_b.append(round(b[i] + (mid_b[i] - b[i]) /
                     (1+math.sin(0.3*math.pi)), 14))
        COM_c.append(round(c[i] + (mid_c[i] - c[i]) /
                     (1+math.sin(0.3*math.pi)), 14))
    # checking overlap
    if round(COM_a[0], n) == round(COM_b[0], n) and round(COM_b[0], n) == round(COM_c[0], n) and \
        round(COM_a[1], n) == round(COM_b[1], n) and round(COM_b[1], n) == round(COM_c[1], n) and \
            round(COM_a[2], n) == round(COM_b[2], n) and round(COM_b[2], n) == round(COM_c[2], n):
        return COM_a
    else:
        return COM_a


def dode_face_COM_list_gen(radius: float):
    # generate the list of COM of all 12 faces
    coord = dode_face_dodecahedron_coord(radius)
    COM_list = []
    COM_list.append(dode_face_COM_coor(
        coord[6], coord[18], coord[2], coord[14], coord[4]))
    COM_list.append(dode_face_COM_coor(
        coord[6], coord[4], coord[12], coord[0], coord[16]))
    COM_list.append(dode_face_COM_coor(
        coord[4], coord[14], coord[9], coord[8], coord[12]))
    COM_list.append(dode_face_COM_coor(
        coord[6], coord[18], coord[11], coord[10], coord[16]))
    COM_list.append(dode_face_COM_coor(
        coord[14], coord[2], coord[3], coord[15], coord[9]))
    COM_list.append(dode_face_COM_coor(
        coord[18], coord[11], coord[19], coord[3], coord[2]))
    COM_list.append(dode_face_COM_coor(
        coord[16], coord[10], coord[17], coord[1], coord[0]))
    COM_list.append(dode_face_COM_coor(
        coord[12], coord[0], coord[1], coord[13], coord[8]))
    COM_list.append(dode_face_COM_coor(
        coord[7], coord[17], coord[10], coord[11], coord[19]))
    COM_list.append(dode_face_COM_coor(
        coord[5], coord[13], coord[8], coord[9], coord[15]))
    COM_list.append(dode_face_COM_coor(
        coord[3], coord[19], coord[7], coord[5], coord[15]))
    COM_list.append(dode_face_COM_coor(
        coord[1], coord[17], coord[7], coord[5], coord[13]))
    return COM_list


def dode_face_COM_leg_coor(a: float, b: float, c: float, d: float, e: float):
    # calculate COM and 5 legs of one protein, 6 coords in total [COM, lg1, lg2, lg3, lg4, lg5]
    COM_leg = []
    COM_leg.append(dode_face_COM_coor(a, b, c, d, e))
    COM_leg.append(mid_pt(a, b))
    COM_leg.append(mid_pt(b, c))
    COM_leg.append(mid_pt(c, d))
    COM_leg.append(mid_pt(d, e))
    COM_leg.append(mid_pt(e, a))
    return COM_leg


def dode_face_COM_leg_list_gen(radius: float):
    # generate all COM and leg coords of 12 faces as a large list
    coord = dode_face_dodecahedron_coord(radius)
    COM_leg_list = []
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[6], coord[18], coord[2], coord[14], coord[4]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[6], coord[4], coord[12], coord[0], coord[16]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[4], coord[14], coord[9], coord[8], coord[12]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[6], coord[18], coord[11], coord[10], coord[16]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[14], coord[2], coord[3], coord[15], coord[9]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[18], coord[11], coord[19], coord[3], coord[2]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[16], coord[10], coord[17], coord[1], coord[0]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[12], coord[0], coord[1], coord[13], coord[8]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[7], coord[17], coord[10], coord[11], coord[19]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[5], coord[13], coord[8], coord[9], coord[15]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[3], coord[19], coord[7], coord[5], coord[15]))
    COM_leg_list.append(dode_face_COM_leg_coor(
        coord[1], coord[17], coord[7], coord[5], coord[13]))
    return COM_leg_list


def dode_face_leg_reduce(COM: float, leg: float, sigma: float):
    # calculate the recuced length when considering the sigma value
    n = 14
    m = (1+5**(0.5))/2
    angle = 2*math.atan(m)
    red_len = sigma/(2*math.sin(angle/2))
    ratio = 1 - red_len/distance(COM, leg)
    leg_red = []
    for i in range(0, 3):
        leg_red.append(round((leg[i] - COM[i])*ratio + COM[i], n))
    return leg_red


def dode_face_leg_reduce_coor_gen(radius: float, sigma: float):
    # Generating all the coords of COM and legs when sigma exists
    COM_leg_list = dode_face_COM_leg_list_gen(radius)
    COM_leg_red_list = []
    for elements in COM_leg_list:
        temp_list = []
        temp_list.append(elements[0])
        i = 1
        while i <= 5:
            temp_list.append(dode_face_leg_reduce(
                elements[0], elements[i], sigma))
            i += 1
        COM_leg_red_list.append(temp_list)
    return COM_leg_red_list


def dode_face_input_coord(radius: float, sigma: float):
    coor = dode_face_leg_reduce_coor_gen(radius, sigma)
    coor_ = np.array(coor[0])
    COM = coor_[0] - coor_[0]
    lg1 = coor_[1] - coor_[0]
    lg2 = coor_[2] - coor_[0]
    lg3 = coor_[3] - coor_[0]
    lg4 = coor_[4] - coor_[0]
    lg5 = coor_[5] - coor_[0]
    n = -coor_[0]
    return COM, lg1, lg2, lg3, lg4, lg5, n


def dode_face_write(radius: float, sigma: float):
    COM, lg1, lg2, lg3, lg4, lg5, n = dode_face_input_coord(radius, sigma)
    coord = dode_face_leg_reduce_coor_gen(radius, sigma)
    theta1, theta2, phi1, phi2, omega = angle_cal(
        coord[0][0], coord[0][3], coord[4][0], coord[4][1])

    f = open('parm.inp', 'w')
    f.write(' # Input file (dodecahedron face-centered)\n\n')
    f.write('start parameters\n')
    f.write('    nItr = 10000000 #iterations\n')
    f.write('    timeStep = 0.1\n')
    f.write('    timeWrite = 10000\n')
    f.write('    pdbWrite = 10000\n')
    f.write('    trajWrite = 10000\n')
    f.write('    restartWrite = 50000\n')
    f.write('    checkPoint = 1000000\n')
    f.write('    overlapSepLimit = 7.0\n')
    f.write('end parameters\n\n')
    f.write('start boundaries\n')
    f.write('    WaterBox = [500,500,500]\n')
    f.write('end boundaries\n\n')
    f.write('start molecules\n')
    f.write('    dode : 200\n')
    f.write('end molecules\n\n')
    f.write('start reactions\n')
    f.write('    dode(lg1) + dode(lg1) <-> dode(lg1!1).dode(lg1!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg2) + dode(lg2) <-> dode(lg2!1).dode(lg2!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg3) + dode(lg3) <-> dode(lg3!1).dode(lg3!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg4) + dode(lg4) <-> dode(lg4!1).dode(lg4!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg5) + dode(lg5) <-> dode(lg5!1).dode(lg5!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg1) + dode(lg2) <-> dode(lg1!1).dode(lg2!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg1) + dode(lg3) <-> dode(lg1!1).dode(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg1) + dode(lg4) <-> dode(lg1!1).dode(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg1) + dode(lg5) <-> dode(lg1!1).dode(lg5!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg2) + dode(lg3) <-> dode(lg2!1).dode(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg2) + dode(lg4) <-> dode(lg2!1).dode(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg2) + dode(lg5) <-> dode(lg2!1).dode(lg5!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg3) + dode(lg4) <-> dode(lg3!1).dode(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg3) + dode(lg5) <-> dode(lg3!1).dode(lg5!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg4) + dode(lg5) <-> dode(lg4!1).dode(lg5!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('end reactions\n')

    f = open('dode.mol', 'w')
    f.write('##\n')
    f.write('# Dodecahedron (face-centered) information file.\n')
    f.write('##\n\n')
    f.write('Name = dode\n')
    f.write('checkOverlap = true\n\n')
    f.write('# translational diffusion constants\n')
    f.write('D = [13.0, 13.0, 13.0]\n\n')
    f.write('# rotational diffusion constants\n')
    f.write('Dr = [0.03, 0.03, 0.03]\n\n')
    f.write('# Coordinates\n')
    f.write('COM   ' + str(round(COM[0], 8)) + '   ' +
            str(round(COM[1], 8)) + '   ' + str(round(COM[2], 8)) + '\n')
    f.write('lg1   ' + str(round(lg1[0], 8)) + '   ' +
            str(round(lg1[1], 8)) + '   ' + str(round(lg1[2], 8)) + '\n')
    f.write('lg2   ' + str(round(lg2[0], 8)) + '   ' +
            str(round(lg2[1], 8)) + '   ' + str(round(lg2[2], 8)) + '\n')
    f.write('lg3   ' + str(round(lg3[0], 8)) + '   ' +
            str(round(lg3[1], 8)) + '   ' + str(round(lg3[2], 8)) + '\n')
    f.write('lg4   ' + str(round(lg4[0], 8)) + '   ' +
            str(round(lg4[1], 8)) + '   ' + str(round(lg4[2], 8)) + '\n')
    f.write('lg5   ' + str(round(lg5[0], 8)) + '   ' +
            str(round(lg5[1], 8)) + '   ' + str(round(lg5[2], 8)) + '\n')
    f.write('\n')
    f.write('# bonds\n')
    f.write('bonds = 5\n')
    f.write('com lg1\n')
    f.write('com lg2\n')
    f.write('com lg3\n')
    f.write('com lg4\n')
    f.write('com lg5\n')
    f.write('\n')


# DODECAHEDEON VERTEX AS COM

def dode_vert_coord(radius: float):
    scaler = radius/(3**0.5)
    m = (1+5**(0.5))/2
    V0 = [0, m, 1/m]
    V1 = [0, m, -1/m]
    V2 = [0, -m, 1/m]
    V3 = [0, -m, -1/m]
    V4 = [1/m, 0, m]
    V5 = [1/m, 0, -m]
    V6 = [-1/m, 0, m]
    V7 = [-1/m, 0, -m]
    V8 = [m, 1/m, 0]
    V9 = [m, -1/m, 0]
    V10 = [-m, 1/m, 0]
    V11 = [-m, -1/m, 0]
    V12 = [1, 1, 1]
    V13 = [1, 1, -1]
    V14 = [1, -1, 1]
    V15 = [1, -1, -1]
    V16 = [-1, 1, 1]
    V17 = [-1, 1, -1]
    V18 = [-1, -1, 1]
    V19 = [-1, -1, -1]
    coord = [V0, V1, V2, V3, V4, V5, V6, V7, V8, V9,
             V10, V11, V12, V13, V14, V15, V16, V17, V18, V19]
    coord_ = []
    for i in coord:
        temp_list = []
        for j in i:
            temp = j*scaler
            temp_list.append(temp)
        coord_.append(temp_list)
    return coord_


def dode_vert_COM_leg(COM: float, a: float, b: float, c: float):
    lega = mid_pt(COM, a)
    legb = mid_pt(COM, b)
    legc = mid_pt(COM, c)
    return [np.around(COM, 10), np.around(lega, 10), np.around(legb, 10), np.around(legc, 10)]


def dode_vert_COM_leg_gen(radius: float):
    coord = dode_vert_coord(radius)
    COM_leg_list = []
    COM_leg_list.append(dode_vert_COM_leg(
        coord[0], coord[1], coord[12], coord[16]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[1], coord[0], coord[13], coord[17]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[2], coord[3], coord[14], coord[18]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[3], coord[2], coord[15], coord[19]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[4], coord[6], coord[12], coord[14]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[5], coord[7], coord[13], coord[15]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[6], coord[4], coord[16], coord[18]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[7], coord[5], coord[17], coord[19]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[8], coord[9], coord[12], coord[13]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[9], coord[8], coord[14], coord[15]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[10], coord[11], coord[16], coord[17]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[11], coord[10], coord[18], coord[19]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[12], coord[0], coord[4], coord[8]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[13], coord[1], coord[5], coord[8]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[14], coord[2], coord[4], coord[9]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[15], coord[3], coord[5], coord[9]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[16], coord[0], coord[6], coord[10]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[17], coord[1], coord[7], coord[10]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[18], coord[2], coord[6], coord[11]))
    COM_leg_list.append(dode_vert_COM_leg(
        coord[19], coord[3], coord[7], coord[11]))
    return COM_leg_list


def dode_vert_leg_reduce(COM: float, leg: float, sigma: float):
    red_len = sigma/2
    ratio = 1 - red_len/distance(COM, leg)
    leg_red = []
    for i in range(0, 3):
        leg_red.append(round((leg[i] - COM[i])*ratio + COM[i], 8))
    return leg_red


def dode_vert_leg_reduce_coor_gen(radius: float, sigma: float):
    COM_leg_list = dode_vert_COM_leg_gen(radius)
    COM_leg_red_list = []
    for elements in COM_leg_list:
        temp_list = []
        temp_list.append(elements[0])
        i = 1
        while i <= 3:
            temp_list.append(dode_vert_leg_reduce(
                elements[0], elements[i], sigma))
            i += 1
        COM_leg_red_list.append(temp_list)
    return COM_leg_red_list


def dode_vert_input_coord(radius: float, sigma: float):
    coor = dode_vert_leg_reduce_coor_gen(radius, sigma)
    coor_ = np.array(coor[0])
    COM = np.around(coor_[0] - coor_[0], 12)
    lg1 = np.around(coor_[1] - coor_[0], 12)
    lg2 = np.around(coor_[2] - coor_[0], 12)
    lg3 = np.around(coor_[3] - coor_[0], 12)
    n = np.around(coor_[0]/np.linalg.norm(coor_[0]), 12)
    return COM, lg1, lg2, lg3, n


def dode_vert_norm_input(radius: float, sigma: float):
    COM, lg1, lg2, lg3, n = dode_vert_input_coord(radius, sigma)
    length = distance(lg1, lg2)
    dis1 = ((-length/2)**2+(-((length/2)*(3**0.5))/3)**2)**0.5
    dis2 = distance(COM, lg1)
    height = (dis2**2-dis1**2)**0.5
    lg1_ = np.array([-length/2, -((length/2)*(3**0.5))/3, -height])
    lg2_ = np.array([length/2, -((length/2)*(3**0.5))/3, -height])
    lg3_ = np.array([0, ((length/2)*(3**0.5))/3*2, -height])
    COM_ = np.array([0, 0, 0])
    n_ = np.array([0, 0, 1])
    return COM_, lg1_, lg2_, lg3_, n_


def dode_vert_write(radius: float, sigma: float):
    COM, lg1, lg2, lg3, n = dode_vert_norm_input(radius, sigma)
    f = open('parm.inp', 'w')
    f.write(' # Input file (dodecahedron vertex-centered)\n\n')
    f.write('start parameters\n')
    f.write('    nItr = 10000000 #iterations\n')
    f.write('    timeStep = 0.1\n')
    f.write('    timeWrite = 10000\n')
    f.write('    pdbWrite = 10000\n')
    f.write('    trajWrite = 10000\n')
    f.write('    restartWrite = 50000\n')
    f.write('    checkPoint = 1000000\n')
    f.write('    overlapSepLimit = 7.0\n')
    f.write('end parameters\n\n')
    f.write('start boundaries\n')
    f.write('    WaterBox = [500,500,500]\n')
    f.write('end boundaries\n\n')
    f.write('start molecules\n')
    f.write('    dode : 200\n')
    f.write('end molecules\n\n')
    f.write('start reactions\n')
    f.write('    dode(lg1) + dode(lg1) <-> dode(lg1!1).dode(lg1!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg2) + dode(lg2) <-> dode(lg2!1).dode(lg2!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg3) + dode(lg3) <-> dode(lg3!1).dode(lg3!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg1) + dode(lg2) <-> dode(lg1!1).dode(lg2!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg1) + dode(lg3) <-> dode(lg1!1).dode(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    dode(lg2) + dode(lg3) <-> dode(lg2!1).dode(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('end reactions\n')

    f = open('dode.mol', 'w')
    f.write('##\n')
    f.write('# Dodecahedron (vertex-centered) information file.\n')
    f.write('##\n\n')
    f.write('Name = dode\n')
    f.write('checkOverlap = true\n\n')
    f.write('# translational diffusion constants\n')
    f.write('D = [13.0, 13.0, 13.0]\n\n')
    f.write('# rotational diffusion constants\n')
    f.write('Dr = [0.03, 0.03, 0.03]\n\n')
    f.write('# Coordinates\n')
    f.write('COM   ' + str(round(COM[0], 8)) + '   ' +
            str(round(COM[1], 8)) + '   ' + str(round(COM[2], 8)) + '\n')
    f.write('lg1   ' + str(round(lg1[0], 8)) + '   ' +
            str(round(lg1[1], 8)) + '   ' + str(round(lg1[2], 8)) + '\n')
    f.write('lg2   ' + str(round(lg2[0], 8)) + '   ' +
            str(round(lg2[1], 8)) + '   ' + str(round(lg2[2], 8)) + '\n')
    f.write('lg3   ' + str(round(lg3[0], 8)) + '   ' +
            str(round(lg3[1], 8)) + '   ' + str(round(lg3[2], 8)) + '\n')
    f.write('\n')
    f.write('# bonds\n')
    f.write('bonds = 3\n')
    f.write('com lg1\n')
    f.write('com lg2\n')
    f.write('com lg3\n')
    f.write('\n')


# ICOSAHEDRON FACE AS COM

def icos_face_vert_coord(radius: float):
    scaler = radius/(2*math.sin(2*math.pi/5))
    m = (1+5**0.5)/2
    v0 = [0, 1, m]
    v1 = [0, 1, -m]
    v2 = [0, -1, m]
    v3 = [0, -1, -m]
    v4 = [1, m, 0]
    v5 = [1, -m, 0]
    v6 = [-1, m, 0]
    v7 = [-1, -m, 0]
    v8 = [m, 0, 1]
    v9 = [m, 0, -1]
    v10 = [-m, 0, 1]
    v11 = [-m, 0, -1]
    VertCoord = [v0, v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11]
    VertCoord_ = []
    for i in VertCoord:
        temp_list = []
        for j in i:
            temp = j*scaler
            temp_list.append(temp)
        VertCoord_.append(temp_list)
    return VertCoord_


def icos_face_COM_coord(a: float, b: float, c: float):
    mid_a = mid_pt(b, c)
    mid_b = mid_pt(a, c)
    mid_c = mid_pt(a, b)
    COM_a = []
    COM_b = []
    COM_c = []
    for i in range(0, 3):
        COM_a.append(round(a[i] + (mid_a[i] - a[i]) /
                     (1+math.sin(30/180*math.pi)), 12))
        COM_b.append(round(b[i] + (mid_b[i] - b[i]) /
                     (1+math.sin(30/180*math.pi)), 12))
        COM_c.append(round(c[i] + (mid_c[i] - c[i]) /
                     (1+math.sin(30/180*math.pi)), 12))
    if COM_a == COM_b and COM_b == COM_c:
        return COM_a
    else:
        return COM_a


def icos_face_COM_list_gen(radius: float):
    coord = icos_face_vert_coord(radius)
    COM_list = []
    COM_list.append(icos_face_COM_coord(coord[0], coord[2], coord[8]))
    COM_list.append(icos_face_COM_coord(coord[0], coord[8], coord[4]))
    COM_list.append(icos_face_COM_coord(coord[0], coord[4], coord[6]))
    COM_list.append(icos_face_COM_coord(coord[0], coord[6], coord[10]))
    COM_list.append(icos_face_COM_coord(coord[0], coord[10], coord[2]))
    COM_list.append(icos_face_COM_coord(coord[3], coord[7], coord[5]))
    COM_list.append(icos_face_COM_coord(coord[3], coord[5], coord[9]))
    COM_list.append(icos_face_COM_coord(coord[3], coord[9], coord[1]))
    COM_list.append(icos_face_COM_coord(coord[3], coord[1], coord[11]))
    COM_list.append(icos_face_COM_coord(coord[3], coord[11], coord[7]))
    COM_list.append(icos_face_COM_coord(coord[7], coord[2], coord[5]))
    COM_list.append(icos_face_COM_coord(coord[2], coord[5], coord[8]))
    COM_list.append(icos_face_COM_coord(coord[5], coord[8], coord[9]))
    COM_list.append(icos_face_COM_coord(coord[8], coord[9], coord[4]))
    COM_list.append(icos_face_COM_coord(coord[9], coord[4], coord[1]))
    COM_list.append(icos_face_COM_coord(coord[4], coord[1], coord[6]))
    COM_list.append(icos_face_COM_coord(coord[1], coord[6], coord[11]))
    COM_list.append(icos_face_COM_coord(coord[6], coord[11], coord[10]))
    COM_list.append(icos_face_COM_coord(coord[11], coord[10], coord[7]))
    COM_list.append(icos_face_COM_coord(coord[10], coord[7], coord[2]))
    return COM_list


def icos_face_COM_leg_coord(a: float, b: float, c: float):
    COM_leg = []
    COM_leg.append(icos_face_COM_coord(a, b, c))
    COM_leg.append(mid_pt(a, b))
    COM_leg.append(mid_pt(b, c))
    COM_leg.append(mid_pt(c, a))
    return COM_leg


def COM_leg_list_gen(radius: float):
    coord = icos_face_vert_coord(radius)
    COM_leg_list = []
    COM_leg_list.append(icos_face_COM_leg_coord(coord[0], coord[2], coord[8]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[0], coord[8], coord[4]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[0], coord[4], coord[6]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[0], coord[6], coord[10]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[0], coord[10], coord[2]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[3], coord[7], coord[5]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[3], coord[5], coord[9]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[3], coord[9], coord[1]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[3], coord[1], coord[11]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[3], coord[11], coord[7]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[7], coord[2], coord[5]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[2], coord[5], coord[8]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[5], coord[8], coord[9]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[8], coord[9], coord[4]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[9], coord[4], coord[1]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[4], coord[1], coord[6]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[1], coord[6], coord[11]))
    COM_leg_list.append(icos_face_COM_leg_coord(
        coord[6], coord[11], coord[10]))
    COM_leg_list.append(icos_face_COM_leg_coord(
        coord[11], coord[10], coord[7]))
    COM_leg_list.append(icos_face_COM_leg_coord(coord[10], coord[7], coord[2]))
    return COM_leg_list


def icos_face_leg_reduce(COM: float, leg: float, sigma: float):
    n = 12
    angle = math.acos(-5**0.5/3)
    red_len = sigma/(2*math.sin(angle/2))
    ratio = 1 - red_len/distance(COM, leg)
    leg_red = []
    for i in range(0, 3):
        leg_red.append(round((leg[i] - COM[i])*ratio + COM[i], n))
    return leg_red


def icos_face_leg_reduce_coord_gen(radius: float, sigma: float):
    COM_leg_list = COM_leg_list_gen(radius)
    COM_leg_red_list = []
    for elements in COM_leg_list:
        temp_list = []
        temp_list.append(elements[0])
        i = 1
        while i <= 3:
            temp_list.append(icos_face_leg_reduce(
                elements[0], elements[i], sigma))
            i += 1
        COM_leg_red_list.append(temp_list)
    return COM_leg_red_list


def icos_face_input_coord(radius: float, sigma: float):
    coor = icos_face_leg_reduce_coord_gen(radius, sigma)
    coor_ = np.array(coor[0])
    COM = coor_[0] - coor_[0]
    lg1 = coor_[1] - coor_[0]
    lg2 = coor_[2] - coor_[0]
    lg3 = coor_[3] - coor_[0]
    n = -coor_[0]
    return [COM, lg1, lg2, lg3, n]


def icos_face_write(radius: float, sigma: float):
    COM, lg1, lg2, lg3, n = icos_face_input_coord(radius, sigma)
    coord = icos_face_leg_reduce_coord_gen(radius, sigma)
    theta1, theta2, phi1, phi2, omega = angle_cal(
        coord[0][0], coord[0][2], coord[11][0], coord[11][3])

    f = open('parm.inp', 'w')
    f.write(' # Input file (icosahedron face-centered)\n\n')
    f.write('start parameters\n')
    f.write('    nItr = 10000000 #iterations\n')
    f.write('    timeStep = 0.1\n')
    f.write('    timeWrite = 10000\n')
    f.write('    pdbWrite = 10000\n')
    f.write('    trajWrite = 10000\n')
    f.write('    restartWrite = 50000\n')
    f.write('    checkPoint = 1000000\n')
    f.write('    overlapSepLimit = 7.0\n')
    f.write('end parameters\n\n')
    f.write('start boundaries\n')
    f.write('    WaterBox = [500,500,500]\n')
    f.write('end boundaries\n\n')
    f.write('start molecules\n')
    f.write('    dode : 200\n')
    f.write('end molecules\n\n')
    f.write('start reactions\n')
    f.write('    icos(lg1) + icos(lg1) <-> icos(lg1!1).icos(lg1!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg2) + icos(lg2) <-> icos(lg2!1).icos(lg2!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg3) + icos(lg3) <-> icos(lg3!1).icos(lg3!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg1) + icos(lg2) <-> icos(lg1!1).icos(lg2!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg1) + icos(lg3) <-> icos(lg1!1).icos(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg2) + icos(lg3) <-> icos(lg2!1).icos(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('end reactions\n')

    f = open('icos.mol', 'w')
    f.write('##\n')
    f.write('# Icosahehedron (face-centered) information file.\n')
    f.write('##\n\n')
    f.write('Name = icos\n')
    f.write('checkOverlap = true\n\n')
    f.write('# translational diffusion constants\n')
    f.write('D = [13.0, 13.0, 13.0]\n\n')
    f.write('# rotational diffusion constants\n')
    f.write('Dr = [0.03, 0.03, 0.03]\n\n')
    f.write('# Coordinates\n')
    f.write('COM   ' + str(round(COM[0], 8)) + '   ' +
            str(round(COM[1], 8)) + '   ' + str(round(COM[2], 8)) + '\n')
    f.write('lg1   ' + str(round(lg1[0], 8)) + '   ' +
            str(round(lg1[1], 8)) + '   ' + str(round(lg1[2], 8)) + '\n')
    f.write('lg2   ' + str(round(lg2[0], 8)) + '   ' +
            str(round(lg2[1], 8)) + '   ' + str(round(lg2[2], 8)) + '\n')
    f.write('lg3   ' + str(round(lg3[0], 8)) + '   ' +
            str(round(lg3[1], 8)) + '   ' + str(round(lg3[2], 8)) + '\n')
    f.write('\n')
    f.write('# bonds\n')
    f.write('bonds = 3\n')
    f.write('com lg1\n')
    f.write('com lg2\n')
    f.write('com lg3\n')
    f.write('\n')


# ICOSAHEDRON VERTEX AS COM

def icos_vert_coord(radius: float):
    scaler = radius/(2*math.sin(2*math.pi/5))
    m = (1+5**0.5)/2
    v0 = [0, 1, m]
    v1 = [0, 1, -m]
    v2 = [0, -1, m]
    v3 = [0, -1, -m]
    v4 = [1, m, 0]
    v5 = [1, -m, 0]
    v6 = [-1, m, 0]
    v7 = [-1, -m, 0]
    v8 = [m, 0, 1]
    v9 = [m, 0, -1]
    v10 = [-m, 0, 1]
    v11 = [-m, 0, -1]
    VertCoord = [v0, v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11]
    VertCoord_ = []
    for i in VertCoord:
        temp_list = []
        for j in i:
            temp = j*scaler
            temp_list.append(temp)
        VertCoord_.append(temp_list)
    return VertCoord_


def icos_vert_COM_leg(COM: float, a: float, b: float, c: float, d: float, e: float):
    lega = mid_pt(COM, a)
    legb = mid_pt(COM, b)
    legc = mid_pt(COM, c)
    legd = mid_pt(COM, d)
    lege = mid_pt(COM, e)
    result = [np.around(COM, 10), np.around(lega, 10), np.around(
        legb, 10), np. around(legc, 10), np.around(legd, 10), np.around(lege, 10)]
    return result


def icos_vert_COM_leg_gen(radius: float):
    coord = icos_vert_coord(radius)
    COM_leg_list = []
    COM_leg_list.append(icos_vert_COM_leg(
        coord[0], coord[2], coord[8], coord[4], coord[6], coord[10]))
    COM_leg_list.append(icos_vert_COM_leg(
        coord[1], coord[4], coord[6], coord[11], coord[3], coord[9]))
    COM_leg_list.append(icos_vert_COM_leg(
        coord[2], coord[0], coord[10], coord[7], coord[5], coord[8]))
    COM_leg_list.append(icos_vert_COM_leg(
        coord[3], coord[1], coord[11], coord[7], coord[5], coord[9]))
    COM_leg_list.append(icos_vert_COM_leg(
        coord[4], coord[0], coord[6], coord[1], coord[9], coord[8]))
    COM_leg_list.append(icos_vert_COM_leg(
        coord[5], coord[2], coord[8], coord[7], coord[3], coord[9]))
    COM_leg_list.append(icos_vert_COM_leg(
        coord[6], coord[0], coord[10], coord[11], coord[1], coord[4]))
    COM_leg_list.append(icos_vert_COM_leg(
        coord[7], coord[3], coord[11], coord[10], coord[2], coord[5]))
    COM_leg_list.append(icos_vert_COM_leg(
        coord[8], coord[0], coord[2], coord[5], coord[9], coord[4]))
    COM_leg_list.append(icos_vert_COM_leg(
        coord[9], coord[8], coord[4], coord[1], coord[3], coord[5]))
    COM_leg_list.append(icos_vert_COM_leg(
        coord[10], coord[0], coord[2], coord[7], coord[11], coord[6]))
    COM_leg_list.append(icos_vert_COM_leg(
        coord[11], coord[10], coord[7], coord[3], coord[1], coord[6]))
    return COM_leg_list


def icos_vert_leg_reduce(COM: float, leg: float, sigma: float):
    red_len = sigma/2
    ratio = 1 - red_len/distance(COM, leg)
    leg_red = []
    for i in range(0, 3):
        leg_red.append(round((leg[i] - COM[i])*ratio + COM[i], 8))
    return leg_red


def icos_vert_leg_reduce_coor_gen(radius: float, sigma: float):
    COM_leg_list = icos_vert_COM_leg_gen(radius)
    COM_leg_red_list = []
    for elements in COM_leg_list:
        temp_list = []
        temp_list.append(elements[0])
        i = 1
        while i <= 5:
            temp_list.append(icos_vert_leg_reduce(
                elements[0], elements[i], sigma))
            i += 1
        COM_leg_red_list.append(temp_list)
    return COM_leg_red_list


def icos_vert_input_coord(radius: float, sigma: float):
    coor = icos_vert_leg_reduce_coor_gen(radius, sigma)
    coor_ = np.array(coor[0])
    COM = np.around(coor_[0] - coor_[0], 12)
    lg1 = np.around(coor_[1] - coor_[0], 12)
    lg2 = np.around(coor_[2] - coor_[0], 12)
    lg3 = np.around(coor_[3] - coor_[0], 12)
    lg4 = np.around(coor_[4] - coor_[0], 12)
    lg5 = np.around(coor_[5] - coor_[0], 12)
    n = np.around(coor_[0]/np.linalg.norm(coor_[0]), 12)
    return COM, lg1, lg2, lg3, lg4, lg5, n


def icos_vert_center_coor(a: float, b: float, c: float, d: float, e: float):
    n = 8
    mid_a = mid_pt(c, d)
    mid_b = mid_pt(d, e)
    mid_c = mid_pt(a, e)
    COM_a = []
    COM_b = []
    COM_c = []
    for i in range(0, 3):
        COM_a.append(round(a[i] + (mid_a[i] - a[i]) /
                     (1+math.sin(0.3*math.pi)), 14))
        COM_b.append(round(b[i] + (mid_b[i] - b[i]) /
                     (1+math.sin(0.3*math.pi)), 14))
        COM_c.append(round(c[i] + (mid_c[i] - c[i]) /
                     (1+math.sin(0.3*math.pi)), 14))
    if round(COM_a[0], n) == round(COM_b[0], n) and round(COM_b[0], n) == round(COM_c[0], n) and \
        round(COM_a[1], n) == round(COM_b[1], n) and round(COM_b[1], n) == round(COM_c[1], n) and \
            round(COM_a[2], n) == round(COM_b[2], n) and round(COM_b[2], n) == round(COM_c[2], n):
        return COM_a
    else:
        return COM_a


def icos_vert_check_dis(cen: float, COM: float, lg1: float, lg2: float, lg3: float, lg4: float, lg5: float):
    dis1 = round(distance(cen, lg1), 8)
    dis2 = round(distance(cen, lg2), 8)
    dis3 = round(distance(cen, lg3), 8)
    dis4 = round(distance(cen, lg4), 8)
    dis5 = round(distance(cen, lg5), 8)
    dis_ = round(distance(COM, cen), 8)
    if dis1 == dis2 and dis1 == dis3 and dis1 == dis4 and dis1 == dis5:
        return dis1, dis_
    else:
        return dis1, dis_


def icos_vert_norm_input(scaler: float, dis_: float):
    c1 = math.cos(2*math.pi/5)
    c2 = math.cos(math.pi/5)
    s1 = math.sin(2*math.pi/5)
    s2 = math.sin(4*math.pi/5)
    v0 = scaler*np.array([0, 1])
    v1 = scaler*np.array([-s1, c1])
    v2 = scaler*np.array([-s2, -c2])
    v3 = scaler*np.array([s2, -c2])
    v4 = scaler*np.array([s1, c1])
    lg1 = np.array([v0[0], v0[1], -dis_])
    lg2 = np.array([v1[0], v1[1], -dis_])
    lg3 = np.array([v2[0], v2[1], -dis_])
    lg4 = np.array([v3[0], v3[1], -dis_])
    lg5 = np.array([v4[0], v4[1], -dis_])
    COM = np.array([0, 0, 0])
    n = np.array([0, 0, 1])
    return COM, lg1, lg2, lg3, lg4, lg5, n


def icos_vert_write(radius: float, sigma: float):
    COM_, lg1_, lg2_, lg3_, lg4_, lg5_, n_ = icos_vert_input_coord(
        radius, sigma)
    cen_ = icos_vert_center_coor(lg1_, lg2_, lg3_, lg4_, lg5_)
    scaler, dis_ = icos_vert_check_dis(
        cen_, COM_, lg1_, lg2_, lg3_, lg4_, lg5_)
    COM, lg1, lg2, lg3, lg4, lg5, n = icos_vert_norm_input(scaler, dis_)

    f = open('parm.inp', 'w')
    f.write(' # Input file (icosahedron vertex-centered)\n\n')
    f.write('start parameters\n')
    f.write('    nItr = 10000000 #iterations\n')
    f.write('    timeStep = 0.1\n')
    f.write('    timeWrite = 10000\n')
    f.write('    pdbWrite = 10000\n')
    f.write('    trajWrite = 10000\n')
    f.write('    restartWrite = 50000\n')
    f.write('    checkPoint = 1000000\n')
    f.write('    overlapSepLimit = 7.0\n')
    f.write('end parameters\n\n')
    f.write('start boundaries\n')
    f.write('    WaterBox = [500,500,500]\n')
    f.write('end boundaries\n\n')
    f.write('start molecules\n')
    f.write('    icos : 200\n')
    f.write('end molecules\n\n')
    f.write('start reactions\n')
    f.write('    icos(lg1) + icos(lg1) <-> icos(lg1!1).icos(lg1!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg2) + icos(lg2) <-> icos(lg2!1).icos(lg2!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg3) + icos(lg3) <-> icos(lg3!1).icos(lg3!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg4) + icos(lg4) <-> icos(lg4!1).icos(lg4!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg5) + icos(lg5) <-> icos(lg5!1).icos(lg5!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg1) + icos(lg2) <-> icos(lg1!1).icos(lg2!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg1) + icos(lg3) <-> icos(lg1!1).icos(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg1) + icos(lg4) <-> icos(lg1!1).icos(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg1) + icos(lg5) <-> icos(lg1!1).icos(lg5!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg2) + icos(lg3) <-> icos(lg2!1).icos(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg2) + icos(lg4) <-> icos(lg2!1).icos(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg2) + icos(lg5) <-> icos(lg2!1).icos(lg5!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg3) + icos(lg4) <-> icos(lg3!1).icos(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg3) + icos(lg5) <-> icos(lg3!1).icos(lg5!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    icos(lg4) + icos(lg5) <-> icos(lg4!1).icos(lg5!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('end reactions\n')

    f = open('icos.mol', 'w')
    f.write('##\n')
    f.write('# Icosahedron (vertex-centered) information file.\n')
    f.write('##\n\n')
    f.write('Name = icos\n')
    f.write('checkOverlap = true\n\n')
    f.write('# translational diffusion constants\n')
    f.write('D = [13.0, 13.0, 13.0]\n\n')
    f.write('# rotational diffusion constants\n')
    f.write('Dr = [0.03, 0.03, 0.03]\n\n')
    f.write('# Coordinates\n')
    f.write('COM   ' + str(round(COM[0], 8)) + '   ' +
            str(round(COM[1], 8)) + '   ' + str(round(COM[2], 8)) + '\n')
    f.write('lg1   ' + str(round(lg1[0], 8)) + '   ' +
            str(round(lg1[1], 8)) + '   ' + str(round(lg1[2], 8)) + '\n')
    f.write('lg2   ' + str(round(lg2[0], 8)) + '   ' +
            str(round(lg2[1], 8)) + '   ' + str(round(lg2[2], 8)) + '\n')
    f.write('lg3   ' + str(round(lg3[0], 8)) + '   ' +
            str(round(lg3[1], 8)) + '   ' + str(round(lg3[2], 8)) + '\n')
    f.write('lg4   ' + str(round(lg4[0], 8)) + '   ' +
            str(round(lg4[1], 8)) + '   ' + str(round(lg4[2], 8)) + '\n')
    f.write('lg5   ' + str(round(lg5[0], 8)) + '   ' +
            str(round(lg5[1], 8)) + '   ' + str(round(lg5[2], 8)) + '\n')
    f.write('\n')
    f.write('# bonds\n')
    f.write('bonds = 5\n')
    f.write('com lg1\n')
    f.write('com lg2\n')
    f.write('com lg3\n')
    f.write('com lg4\n')
    f.write('com lg5\n')
    f.write('\n')


# OCTAHEDRON FACE AS COM

def octa_face_vert_coord(radius: float):
    scaler = radius
    v0 = [1, 0, 0]
    v1 = [-1, 0, 0]
    v2 = [0, 1, 0]
    v3 = [0, -1, 0]
    v4 = [0, 0, 1]
    v5 = [0, 0, -1]
    VertCoord = [v0, v1, v2, v3, v4, v5]
    VertCoord_ = []
    for i in VertCoord:
        temp_list = []
        for j in i:
            temp = j*scaler
            temp_list.append(temp)
        VertCoord_.append(temp_list)
    return VertCoord_


def octa_face_COM_coord(a: float, b: float, c: float):
    mid_a = mid_pt(b, c)
    mid_b = mid_pt(a, c)
    mid_c = mid_pt(a, b)
    COM_a = []
    COM_b = []
    COM_c = []
    for i in range(0, 3):
        COM_a.append(round(a[i] + (mid_a[i] - a[i]) /
                     (1+math.sin(30/180*math.pi)), 12))
        COM_b.append(round(b[i] + (mid_b[i] - b[i]) /
                     (1+math.sin(30/180*math.pi)), 12))
        COM_c.append(round(c[i] + (mid_c[i] - c[i]) /
                     (1+math.sin(30/180*math.pi)), 12))
    if COM_a == COM_b and COM_b == COM_c:
        return COM_a
    else:
        return COM_a


def octa_face_COM_list_gen(radius: float):
    coord = octa_face_vert_coord(radius)
    COM_list = []
    COM_list.append(octa_face_COM_coord(coord[0], coord[2], coord[4]))
    COM_list.append(octa_face_COM_coord(coord[0], coord[3], coord[4]))
    COM_list.append(octa_face_COM_coord(coord[0], coord[3], coord[5]))
    COM_list.append(octa_face_COM_coord(coord[0], coord[2], coord[5]))
    COM_list.append(octa_face_COM_coord(coord[1], coord[2], coord[4]))
    COM_list.append(octa_face_COM_coord(coord[1], coord[3], coord[4]))
    COM_list.append(octa_face_COM_coord(coord[1], coord[3], coord[5]))
    COM_list.append(octa_face_COM_coord(coord[1], coord[2], coord[5]))
    return COM_list


def octa_face_COM_leg_coord(a: float, b: float, c: float):
    COM_leg = []
    COM_leg.append(octa_face_COM_coord(a, b, c))
    COM_leg.append(mid_pt(a, b))
    COM_leg.append(mid_pt(b, c))
    COM_leg.append(mid_pt(c, a))
    return COM_leg


def octa_face_COM_leg_list_gen(radius: float):
    coord = octa_face_vert_coord(radius)
    COM_leg_list = []

    COM_leg_list.append(octa_face_COM_leg_coord(coord[0], coord[2], coord[4]))
    COM_leg_list.append(octa_face_COM_leg_coord(coord[0], coord[3], coord[4]))
    COM_leg_list.append(octa_face_COM_leg_coord(coord[0], coord[3], coord[5]))
    COM_leg_list.append(octa_face_COM_leg_coord(coord[0], coord[2], coord[5]))
    COM_leg_list.append(octa_face_COM_leg_coord(coord[1], coord[2], coord[4]))
    COM_leg_list.append(octa_face_COM_leg_coord(coord[1], coord[3], coord[4]))
    COM_leg_list.append(octa_face_COM_leg_coord(coord[1], coord[3], coord[5]))
    COM_leg_list.append(octa_face_COM_leg_coord(coord[1], coord[2], coord[5]))
    return COM_leg_list


def octa_face_leg_reduce(COM: float, leg: float, sigma: float):
    n = 12
    angle = math.acos(-1/3)
    red_len = sigma/(2*math.sin(angle/2))
    ratio = 1 - red_len/distance(COM, leg)
    leg_red = []
    for i in range(0, 3):
        leg_red.append(round((leg[i] - COM[i])*ratio + COM[i], n))
    return leg_red


def octa_face_leg_reduce_coord_gen(radius: float, sigma: float):
    COM_leg_list = octa_face_COM_leg_list_gen(radius)
    COM_leg_red_list = []
    for elements in COM_leg_list:
        temp_list = []
        temp_list.append(elements[0])
        i = 1
        while i <= 3:
            temp_list.append(octa_face_leg_reduce(
                elements[0], elements[i], sigma))
            i += 1
        COM_leg_red_list.append(temp_list)
    return COM_leg_red_list


def octa_face_input_coord(radius: float, sigma: float):
    coor = octa_face_leg_reduce_coord_gen(radius, sigma)
    coor_ = np.array(coor[0])
    COM = coor_[0] - coor_[0]
    lg1 = coor_[1] - coor_[0]
    lg2 = coor_[2] - coor_[0]
    lg3 = coor_[3] - coor_[0]
    n = -coor_[0]
    return [COM, lg1, lg2, lg3, n]


def octa_face_write(radius: float, sigma: float):
    COM, lg1, lg2, lg3, n = octa_face_input_coord(radius, sigma)
    coord = octa_face_leg_reduce_coord_gen(radius, sigma)
    theta1, theta2, phi1, phi2, omega = angle_cal(
        coord[0][0], coord[0][3], coord[1][0], coord[1][3])

    f = open('parm.inp', 'w')
    f.write(' # Input file (octahedron face-centered)\n\n')
    f.write('start parameters\n')
    f.write('    nItr = 10000000 #iterations\n')
    f.write('    timeStep = 0.1\n')
    f.write('    timeWrite = 10000\n')
    f.write('    pdbWrite = 10000\n')
    f.write('    trajWrite = 10000\n')
    f.write('    restartWrite = 50000\n')
    f.write('    checkPoint = 1000000\n')
    f.write('    overlapSepLimit = 7.0\n')
    f.write('end parameters\n\n')
    f.write('start boundaries\n')
    f.write('    WaterBox = [500,500,500]\n')
    f.write('end boundaries\n\n')
    f.write('start molecules\n')
    f.write('    octa : 200\n')
    f.write('end molecules\n\n')
    f.write('start reactions\n')
    f.write('    octa(lg1) + octa(lg1) <-> octa(lg1!1).octa(lg1!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    octa(lg2) + octa(lg2) <-> octa(lg2!1).octa(lg2!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    octa(lg3) + octa(lg3) <-> octa(lg3!1).octa(lg3!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    octa(lg1) + octa(lg2) <-> octa(lg1!1).octa(lg2!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    octa(lg1) + octa(lg3) <-> octa(lg1!1).octa(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    octa(lg2) + octa(lg3) <-> octa(lg2!1).octa(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('end reactions\n')

    f = open('octa.mol', 'w')
    f.write('##\n')
    f.write('# Octahehedron (face-centered) information file.\n')
    f.write('##\n\n')
    f.write('Name = octa\n')
    f.write('checkOverlap = true\n\n')
    f.write('# translational diffusion constants\n')
    f.write('D = [13.0, 13.0, 13.0]\n\n')
    f.write('# rotational diffusion constants\n')
    f.write('Dr = [0.03, 0.03, 0.03]\n\n')
    f.write('# Coordinates\n')
    f.write('COM   ' + str(round(COM[0], 8)) + '   ' +
            str(round(COM[1], 8)) + '   ' + str(round(COM[2], 8)) + '\n')
    f.write('lg1   ' + str(round(lg1[0], 8)) + '   ' +
            str(round(lg1[1], 8)) + '   ' + str(round(lg1[2], 8)) + '\n')
    f.write('lg2   ' + str(round(lg2[0], 8)) + '   ' +
            str(round(lg2[1], 8)) + '   ' + str(round(lg2[2], 8)) + '\n')
    f.write('lg3   ' + str(round(lg3[0], 8)) + '   ' +
            str(round(lg3[1], 8)) + '   ' + str(round(lg3[2], 8)) + '\n')
    f.write('# bonds\n')
    f.write('bonds = 3\n')
    f.write('com lg1\n')
    f.write('com lg2\n')
    f.write('com lg3\n')
    f.write('\n')


# OCTAHEDRON VERTEX AS COM

def octa_vert_coord(radius: float):
    scaler = radius
    v0 = [1, 0, 0]
    v1 = [-1, 0, 0]
    v2 = [0, 1, 0]
    v3 = [0, -1, 0]
    v4 = [0, 0, 1]
    v5 = [0, 0, -1]
    VertCoord = [v0, v1, v2, v3, v4, v5]
    VertCoord_ = []
    for i in VertCoord:
        temp_list = []
        for j in i:
            temp = j*scaler
            temp_list.append(temp)
        VertCoord_.append(temp_list)
    return VertCoord_


def octa_vert_COM_leg(COM: float, a: float, b: float, c: float, d: float):
    lega = mid_pt(COM, a)
    legb = mid_pt(COM, b)
    legc = mid_pt(COM, c)
    legd = mid_pt(COM, d)
    return [np.around(COM, 10), np.around(lega, 10), np.around(legb, 10), np.around(legc, 10), np.around(legd, 10)]


def octa_vert_COM_leg_gen(radius: float):
    coord = octa_vert_coord(radius)
    COM_leg_list = []
    COM_leg_list.append(octa_vert_COM_leg(
        coord[0], coord[2], coord[4], coord[3], coord[5]))
    COM_leg_list.append(octa_vert_COM_leg(
        coord[1], coord[2], coord[4], coord[3], coord[5]))
    COM_leg_list.append(octa_vert_COM_leg(
        coord[2], coord[1], coord[5], coord[0], coord[4]))
    COM_leg_list.append(octa_vert_COM_leg(
        coord[3], coord[1], coord[5], coord[0], coord[4]))
    COM_leg_list.append(octa_vert_COM_leg(
        coord[4], coord[1], coord[2], coord[0], coord[3]))
    COM_leg_list.append(octa_vert_COM_leg(
        coord[5], coord[1], coord[2], coord[0], coord[3]))
    return COM_leg_list


def octa_vert_leg_reduce(COM: float, leg: float, sigma: float):
    red_len = sigma/2
    ratio = 1 - red_len/distance(COM, leg)
    leg_red = []
    for i in range(0, 3):
        leg_red.append(round((leg[i] - COM[i])*ratio + COM[i], 8))
    return leg_red


def octa_vert_leg_reduce_coor_gen(radius: float, sigma: float):
    COM_leg_list = octa_vert_COM_leg_gen(radius)
    COM_leg_red_list = []
    for elements in COM_leg_list:
        temp_list = []
        temp_list.append(elements[0])
        i = 1
        while i <= 4:
            temp_list.append(octa_vert_leg_reduce(
                elements[0], elements[i], sigma))
            i += 1
        COM_leg_red_list.append(temp_list)
    return COM_leg_red_list


def octa_vert_input_coord(radius: float, sigma: float):
    coor = octa_vert_leg_reduce_coor_gen(radius, sigma)
    coor_ = np.array(coor[4])
    COM = np.around(coor_[0] - coor_[0], 8)
    lg1 = np.around(coor_[1] - coor_[0], 8)
    lg2 = np.around(coor_[2] - coor_[0], 8)
    lg3 = np.around(coor_[3] - coor_[0], 8)
    lg4 = np.around(coor_[4] - coor_[0], 8)
    n = np.around(coor_[0]/np.linalg.norm(coor_[0]), 8)
    return COM, lg1, lg2, lg3, lg4, n


def octa_vert_write(radius: float, sigma: float):
    COM, lg1, lg2, lg3, lg4, n = octa_vert_input_coord(radius, sigma)
    f = open('parm.inp', 'w')
    f.write(' # Input file (octahedron vertex-centered)\n\n')
    f.write('start parameters\n')
    f.write('    nItr = 10000000 #iterations\n')
    f.write('    timeStep = 0.1\n')
    f.write('    timeWrite = 10000\n')
    f.write('    pdbWrite = 10000\n')
    f.write('    trajWrite = 10000\n')
    f.write('    restartWrite = 50000\n')
    f.write('    checkPoint = 1000000\n')
    f.write('    overlapSepLimit = 7.0\n')
    f.write('end parameters\n\n')
    f.write('start boundaries\n')
    f.write('    WaterBox = [500,500,500]\n')
    f.write('end boundaries\n\n')
    f.write('start molecules\n')
    f.write('    octa : 200\n')
    f.write('end molecules\n\n')
    f.write('start reactions\n')
    f.write('    otca(lg1) + octa(lg1) <-> octa(lg1!1).octa(lg1!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    otca(lg2) + octa(lg2) <-> octa(lg2!1).octa(lg2!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    otca(lg3) + octa(lg3) <-> octa(lg3!1).octa(lg3!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    otca(lg4) + octa(lg4) <-> octa(lg4!1).octa(lg4!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    otca(lg1) + octa(lg2) <-> octa(lg1!1).octa(lg2!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    otca(lg1) + octa(lg3) <-> octa(lg1!1).octa(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    otca(lg1) + octa(lg4) <-> octa(lg1!1).octa(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    otca(lg2) + octa(lg3) <-> octa(lg2!1).octa(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    otca(lg2) + octa(lg4) <-> octa(lg2!1).octa(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    otca(lg3) + octa(lg4) <-> octa(lg3!1).octa(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('end reactions\n')

    f = open('octa.mol', 'w')
    f.write('##\n')
    f.write('# Octahedron (vertex-centered) information file.\n')
    f.write('##\n\n')
    f.write('Name = octa\n')
    f.write('checkOverlap = true\n\n')
    f.write('# translational diffusion constants\n')
    f.write('D = [13.0, 13.0, 13.0]\n\n')
    f.write('# rotational diffusion constants\n')
    f.write('Dr = [0.03, 0.03, 0.03]\n\n')
    f.write('# Coordinates\n')
    f.write('COM   ' + str(round(COM[0], 8)) + '   ' +
            str(round(COM[1], 8)) + '   ' + str(round(COM[2], 8)) + '\n')
    f.write('lg1   ' + str(round(lg1[0], 8)) + '   ' +
            str(round(lg1[1], 8)) + '   ' + str(round(lg1[2], 8)) + '\n')
    f.write('lg2   ' + str(round(lg2[0], 8)) + '   ' +
            str(round(lg2[1], 8)) + '   ' + str(round(lg2[2], 8)) + '\n')
    f.write('lg3   ' + str(round(lg3[0], 8)) + '   ' +
            str(round(lg3[1], 8)) + '   ' + str(round(lg3[2], 8)) + '\n')
    f.write('lg4   ' + str(round(lg4[0], 8)) + '   ' +
            str(round(lg4[1], 8)) + '   ' + str(round(lg4[2], 8)) + '\n')
    f.write('\n')
    f.write('# bonds\n')
    f.write('bonds = 4\n')
    f.write('com lg1\n')
    f.write('com lg2\n')
    f.write('com lg3\n')
    f.write('com lg4\n')
    f.write('\n')


# CUBE FACE AS COM

def cube_face_vert_coord(radius: float):
    scaler = radius/3**0.5
    v0 = [1, 1, 1]
    v1 = [-1, 1, 1]
    v2 = [1, -1, 1]
    v3 = [1, 1, -1]
    v4 = [-1, -1, 1]
    v5 = [1, -1, -1]
    v6 = [-1, 1, -1]
    v7 = [-1, -1, -1]
    VertCoord = [v0, v1, v2, v3, v4, v5, v6, v7]
    VertCoord_ = []
    for i in VertCoord:
        temp_list = []
        for j in i:
            temp = j*scaler
            temp_list.append(temp)
        VertCoord_.append(temp_list)
    return VertCoord_


def cube_face_COM_coord(a: float, b: float, c: float, d: float):
    mid_a = mid_pt(a, b)
    mid_b = mid_pt(b, c)
    mid_c = mid_pt(c, d)
    mid_d = mid_pt(d, a)
    COM_a = mid_pt(mid_a, mid_c)
    COM_b = mid_pt(mid_b, mid_d)
    if COM_a == COM_b:
        return COM_a
    else:
        return COM_a


def cube_face_COM_list_gen(radius: float):
    coord = cube_face_vert_coord(radius)
    COM_list = []
    COM_list.append(cube_face_COM_coord(
        coord[0], coord[3], coord[5], coord[2]))
    COM_list.append(cube_face_COM_coord(
        coord[0], coord[3], coord[6], coord[1]))
    COM_list.append(cube_face_COM_coord(
        coord[0], coord[1], coord[4], coord[2]))
    COM_list.append(cube_face_COM_coord(
        coord[7], coord[4], coord[1], coord[6]))
    COM_list.append(cube_face_COM_coord(
        coord[7], coord[4], coord[2], coord[5]))
    COM_list.append(cube_face_COM_coord(
        coord[7], coord[6], coord[3], coord[5]))
    return COM_list


def cube_face_COM_leg_coord(a: float, b: float, c: float, d: float):
    COM_leg = []
    COM_leg.append(cube_face_COM_coord(a, b, c, d))
    COM_leg.append(mid_pt(a, b))
    COM_leg.append(mid_pt(b, c))
    COM_leg.append(mid_pt(c, d))
    COM_leg.append(mid_pt(d, a))
    return COM_leg


def cube_face_COM_leg_list_gen(radius: float):
    coord = cube_face_vert_coord(radius)
    COM_leg_list = []
    COM_leg_list.append(cube_face_COM_leg_coord(
        coord[0], coord[3], coord[5], coord[2]))
    COM_leg_list.append(cube_face_COM_leg_coord(
        coord[0], coord[3], coord[6], coord[1]))
    COM_leg_list.append(cube_face_COM_leg_coord(
        coord[0], coord[1], coord[4], coord[2]))
    COM_leg_list.append(cube_face_COM_leg_coord(
        coord[7], coord[4], coord[1], coord[6]))
    COM_leg_list.append(cube_face_COM_leg_coord(
        coord[7], coord[4], coord[2], coord[5]))
    COM_leg_list.append(cube_face_COM_leg_coord(
        coord[7], coord[6], coord[3], coord[5]))
    return COM_leg_list


def cube_face_leg_reduce(COM: float, leg: float, sigma: float):
    n = 12
    angle = math.acos(0)
    red_len = sigma/(2*math.sin(angle/2))
    ratio = 1 - red_len/distance(COM, leg)
    leg_red = []
    for i in range(0, 3):
        leg_red.append(round((leg[i] - COM[i])*ratio + COM[i], n))
    return leg_red


def cube_face_leg_reduce_coord_gen(radius: float, sigma: float):
    COM_leg_list = cube_face_COM_leg_list_gen(radius)
    COM_leg_red_list = []
    for elements in COM_leg_list:
        temp_list = []
        temp_list.append(np.around(elements[0], 8))
        i = 1
        while i <= 4:
            temp_list.append(np.around(cube_face_leg_reduce(
                elements[0], elements[i], sigma), 8))
            i += 1
        COM_leg_red_list.append(temp_list)
    return COM_leg_red_list


def cube_face_input_coord(radius: float, sigma: float):
    coor = cube_face_leg_reduce_coord_gen(radius, sigma)
    coor_ = np.array(coor[0])
    COM = np.around(coor_[0] - coor_[0], 7)
    lg1 = coor_[1] - coor_[0]
    lg2 = coor_[2] - coor_[0]
    lg3 = coor_[3] - coor_[0]
    lg4 = coor_[4] - coor_[0]
    n = -coor_[0]
    return [COM, lg1, lg2, lg3, lg4, n]


def cube_face_write(radius: float, sigma: float):
    COM, lg1, lg2, lg3, lg4, n = cube_face_input_coord(radius, sigma)
    coord = cube_face_leg_reduce_coord_gen(radius, sigma)
    theta1, theta2, phi1, phi2, omega = angle_cal(
        coord[0][0], coord[0][1], coord[1][0], coord[1][1])

    f = open('parm.inp', 'w')
    f.write(' # Input file (cube face-centered)\n\n')
    f.write('start parameters\n')
    f.write('    nItr = 10000000 #iterations\n')
    f.write('    timeStep = 0.1\n')
    f.write('    timeWrite = 10000\n')
    f.write('    pdbWrite = 10000\n')
    f.write('    trajWrite = 10000\n')
    f.write('    restartWrite = 50000\n')
    f.write('    checkPoint = 1000000\n')
    f.write('    overlapSepLimit = 7.0\n')
    f.write('end parameters\n\n')
    f.write('start boundaries\n')
    f.write('    WaterBox = [500,500,500]\n')
    f.write('end boundaries\n\n')
    f.write('start molecules\n')
    f.write('    cube : 200\n')
    f.write('end molecules\n\n')
    f.write('start reactions\n')
    f.write('    cube(lg1) + cube(lg1) <-> cube(lg1!1).cube(lg1!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg2) + cube(lg2) <-> cube(lg2!1).cube(lg2!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg3) + cube(lg3) <-> cube(lg3!1).cube(lg3!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg4) + cube(lg4) <-> cube(lg4!1).cube(lg4!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg1) + cube(lg2) <-> cube(lg1!1).cube(lg2!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg1) + cube(lg3) <-> cube(lg1!1).cube(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg1) + cube(lg4) <-> cube(lg1!1).cube(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg2) + cube(lg3) <-> cube(lg2!1).cube(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg2) + cube(lg4) <-> cube(lg2!1).cube(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg3) + cube(lg4) <-> cube(lg3!1).cube(lg4!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('end reactions\n')

    f = open('cube.mol', 'w')
    f.write('##\n')
    f.write('# Cube (face-centered) information file.\n')
    f.write('##\n\n')
    f.write('Name = cube\n')
    f.write('checkOverlap = true\n\n')
    f.write('# translational diffusion constants\n')
    f.write('D = [13.0, 13.0, 13.0]\n\n')
    f.write('# rotational diffusion constants\n')
    f.write('Dr = [0.03, 0.03, 0.03]\n\n')
    f.write('# Coordinates\n')
    f.write('COM   ' + str(round(COM[0], 8)) + '   ' +
            str(round(COM[1], 8)) + '   ' + str(round(COM[2], 8)) + '\n')
    f.write('lg1   ' + str(round(lg1[0], 8)) + '   ' +
            str(round(lg1[1], 8)) + '   ' + str(round(lg1[2], 8)) + '\n')
    f.write('lg2   ' + str(round(lg2[0], 8)) + '   ' +
            str(round(lg2[1], 8)) + '   ' + str(round(lg2[2], 8)) + '\n')
    f.write('lg3   ' + str(round(lg3[0], 8)) + '   ' +
            str(round(lg3[1], 8)) + '   ' + str(round(lg3[2], 8)) + '\n')
    f.write('lg4   ' + str(round(lg4[0], 8)) + '   ' +
            str(round(lg4[1], 8)) + '   ' + str(round(lg4[2], 8)) + '\n')
    f.write('\n')
    f.write('# bonds\n')
    f.write('bonds = 4\n')
    f.write('com lg1\n')
    f.write('com lg2\n')
    f.write('com lg3\n')
    f.write('com lg4\n')
    f.write('\n')


# CUBE VERTEX AS COM

def cube_vert_coord(radius: float):
    scaler = radius/3**0.5
    v0 = [1, 1, 1]
    v1 = [-1, 1, 1]
    v2 = [1, -1, 1]
    v3 = [1, 1, -1]
    v4 = [-1, -1, 1]
    v5 = [1, -1, -1]
    v6 = [-1, 1, -1]
    v7 = [-1, -1, -1]
    VertCoord = [v0, v1, v2, v3, v4, v5, v6, v7]
    VertCoord_ = []
    for i in VertCoord:
        temp_list = []
        for j in i:
            temp = j*scaler
            temp_list.append(temp)
        VertCoord_.append(temp_list)
    return VertCoord_


def cube_vert_COM_leg(COM: float, a: float, b: float, c: float):
    lega = mid_pt(COM, a)
    legb = mid_pt(COM, b)
    legc = mid_pt(COM, c)
    return [np.around(COM, 10), np.around(lega, 10), np.around(legb, 10), np.around(legc, 10)]


def cube_vert_COM_leg_gen(radius: float):
    coord = cube_vert_coord(radius)
    COM_leg_list = []
    COM_leg_list.append(cube_vert_COM_leg(
        coord[0], coord[1], coord[2], coord[3]))
    COM_leg_list.append(cube_vert_COM_leg(
        coord[1], coord[0], coord[4], coord[6]))
    COM_leg_list.append(cube_vert_COM_leg(
        coord[2], coord[0], coord[4], coord[5]))
    COM_leg_list.append(cube_vert_COM_leg(
        coord[3], coord[0], coord[5], coord[6]))
    COM_leg_list.append(cube_vert_COM_leg(
        coord[4], coord[1], coord[2], coord[7]))
    COM_leg_list.append(cube_vert_COM_leg(
        coord[5], coord[2], coord[3], coord[7]))
    COM_leg_list.append(cube_vert_COM_leg(
        coord[6], coord[1], coord[3], coord[7]))
    COM_leg_list.append(cube_vert_COM_leg(
        coord[7], coord[4], coord[5], coord[6]))
    return COM_leg_list


def cube_vert_leg_reduce(COM: float, leg: float, sigma: float):
    red_len = sigma/2
    ratio = 1 - red_len/distance(COM, leg)
    leg_red = []
    for i in range(0, 3):
        leg_red.append(round((leg[i] - COM[i])*ratio + COM[i], 8))
    return leg_red


def cube_vert_leg_reduce_coor_gen(radius: float, sigma: float):
    COM_leg_list = cube_vert_COM_leg_gen(radius)
    COM_leg_red_list = []
    for elements in COM_leg_list:
        temp_list = []
        temp_list.append(elements[0])
        i = 1
        while i <= 3:
            temp_list.append(cube_vert_leg_reduce(
                elements[0], elements[i], sigma))
            i += 1
        COM_leg_red_list.append(temp_list)
    return COM_leg_red_list


def cube_vert_input_coord(radius: float, sigma: float):
    coor = cube_vert_leg_reduce_coor_gen(radius, sigma)
    coor_ = np.array(coor[0])
    COM = np.around(coor_[0] - coor_[0], 8)
    lg1 = np.around(coor_[1] - coor_[0], 8)
    lg2 = np.around(coor_[2] - coor_[0], 8)
    lg3 = np.around(coor_[3] - coor_[0], 8)
    n = np.around(coor_[0]/np.linalg.norm(coor_[0]), 8)
    return COM, lg1, lg2, lg3, n


def cube_vert_norm_input(radius: float, sigma: float):
    COM, lg1, lg2, lg3, n = cube_vert_input_coord(radius, sigma)
    length = distance(lg1, lg2)
    dis1 = ((-length/2)**2+(-((length/2)*(3**0.5))/3)**2)**0.5
    dis2 = distance(COM, lg1)
    height = (dis2**2-dis1**2)**0.5
    lg1_ = np.array([-length/2, -((length/2)*(3**0.5))/3, -height])
    lg2_ = np.array([length/2, -((length/2)*(3**0.5))/3, -height])
    lg3_ = np.array([0, ((length/2)*(3**0.5))/3*2, -height])
    COM_ = np.array([0, 0, 0])
    n_ = np.array([0, 0, 1])
    return COM_, lg1_, lg2_, lg3_, n_


def cube_vert_write(radius: float, sigma: float):
    COM, lg1, lg2, lg3, n = cube_vert_norm_input(radius, sigma)
    f = open('parm.inp', 'w')
    f.write(' # Input file (cube vertex-centered)\n\n')
    f.write('start parameters\n')
    f.write('    nItr = 10000000 #iterations\n')
    f.write('    timeStep = 0.1\n')
    f.write('    timeWrite = 10000\n')
    f.write('    pdbWrite = 10000\n')
    f.write('    trajWrite = 10000\n')
    f.write('    restartWrite = 50000\n')
    f.write('    checkPoint = 1000000\n')
    f.write('    overlapSepLimit = 7.0\n')
    f.write('end parameters\n\n')
    f.write('start boundaries\n')
    f.write('    WaterBox = [500,500,500]\n')
    f.write('end boundaries\n\n')
    f.write('start molecules\n')
    f.write('    cube : 200\n')
    f.write('end molecules\n\n')
    f.write('start reactions\n')
    f.write('    cube(lg1) + cube(lg1) <-> cube(lg1!1).cube(lg1!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg2) + cube(lg2) <-> cube(lg2!1).cube(lg2!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg3) + cube(lg3) <-> cube(lg3!1).cube(lg3!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg1) + cube(lg2) <-> cube(lg1!1).cube(lg2!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg1) + cube(lg3) <-> cube(lg1!1).cube(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    cube(lg2) + cube(lg3) <-> cube(lg2!1).cube(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('end reactions\n')

    f = open('cube.mol', 'w')
    f.write('##\n')
    f.write('# Cube (vertex-centered) information file.\n')
    f.write('##\n\n')
    f.write('Name = cube\n')
    f.write('checkOverlap = true\n\n')
    f.write('# translational diffusion constants\n')
    f.write('D = [13.0, 13.0, 13.0]\n\n')
    f.write('# rotational diffusion constants\n')
    f.write('Dr = [0.03, 0.03, 0.03]\n\n')
    f.write('# Coordinates\n')
    f.write('COM   ' + str(round(COM[0], 8)) + '   ' +
            str(round(COM[1], 8)) + '   ' + str(round(COM[2], 8)) + '\n')
    f.write('lg1   ' + str(round(lg1[0], 8)) + '   ' +
            str(round(lg1[1], 8)) + '   ' + str(round(lg1[2], 8)) + '\n')
    f.write('lg2   ' + str(round(lg2[0], 8)) + '   ' +
            str(round(lg2[1], 8)) + '   ' + str(round(lg2[2], 8)) + '\n')
    f.write('lg3   ' + str(round(lg3[0], 8)) + '   ' +
            str(round(lg3[1], 8)) + '   ' + str(round(lg3[2], 8)) + '\n')
    f.write('\n')
    f.write('# bonds\n')
    f.write('bonds = 3\n')
    f.write('com lg1\n')
    f.write('com lg2\n')
    f.write('com lg3\n')
    f.write('\n')


# TETRAHETRON FACE AS COM

def tetr_face_coord(radius: float):
    scaler = radius/(3/8)**0.5/2
    v0 = [1, 0, -1/2**0.5]
    v1 = [-1, 0, -1/2**0.5]
    v2 = [0, 1, 1/2**0.5]
    v3 = [0, -1, 1/2**0.5]
    VertCoord = [v0, v1, v2, v3]
    VertCoord_ = []
    for i in VertCoord:
        temp_list = []
        for j in i:
            temp = j*scaler
            temp_list.append(temp)
        VertCoord_.append(temp_list)
    return VertCoord_


def tetr_face_COM_coord(a: float, b: float, c: float):
    n = 10
    mid_a = mid_pt(b, c)
    mid_b = mid_pt(a, c)
    mid_c = mid_pt(a, b)
    COM_a = []
    COM_b = []
    COM_c = []
    for i in range(0, 3):
        COM_a.append(round(a[i] + (mid_a[i] - a[i]) /
                     (1+math.sin(30/180*math.pi)), 12))
        COM_b.append(round(b[i] + (mid_b[i] - b[i]) /
                     (1+math.sin(30/180*math.pi)), 12))
        COM_c.append(round(c[i] + (mid_c[i] - c[i]) /
                     (1+math.sin(30/180*math.pi)), 12))

    if COM_a == COM_b and COM_b == COM_c:
        return COM_a
    else:
        return COM_a


def tetr_face_COM_list_gen(radius: float):
    coord = tetr_face_coord(radius)
    COM_list = []
    COM_list.append(tetr_face_COM_coord(coord[0], coord[1], coord[2]))
    COM_list.append(tetr_face_COM_coord(coord[0], coord[2], coord[3]))
    COM_list.append(tetr_face_COM_coord(coord[0], coord[1], coord[3]))
    COM_list.append(tetr_face_COM_coord(coord[1], coord[2], coord[3]))
    return COM_list


def tetr_face_COM_leg_coord(a: float, b: float, c: float):
    COM_leg = []
    COM_leg.append(tetr_face_COM_coord(a, b, c))
    COM_leg.append(mid_pt(a, b))
    COM_leg.append(mid_pt(b, c))
    COM_leg.append(mid_pt(c, a))
    return COM_leg


def tetr_face_COM_leg_list_gen(radius: float):
    coord = tetr_face_coord(radius)
    COM_leg_list = []
    COM_leg_list.append(tetr_face_COM_leg_coord(coord[0], coord[1], coord[2]))
    COM_leg_list.append(tetr_face_COM_leg_coord(coord[0], coord[2], coord[3]))
    COM_leg_list.append(tetr_face_COM_leg_coord(coord[0], coord[1], coord[3]))
    COM_leg_list.append(tetr_face_COM_leg_coord(coord[1], coord[2], coord[3]))
    return COM_leg_list


def tetr_face_leg_reduce(COM: float, leg: float, sigma: float):
    n = 12
    angle = math.acos(1/3)
    red_len = sigma/(2*math.sin(angle/2))
    ratio = 1 - red_len/distance(COM, leg)
    leg_red = []
    for i in range(0, 3):
        leg_red.append(round((leg[i] - COM[i])*ratio + COM[i], n))
    return leg_red


def tetr_face_leg_reduce_coord_gen(radius: float, sigma: float):
    COM_leg_list = tetr_face_COM_leg_list_gen(radius)
    COM_leg_red_list = []
    for elements in COM_leg_list:
        temp_list = []
        temp_list.append(elements[0])
        i = 1
        while i <= 3:
            temp_list.append(tetr_face_leg_reduce(
                elements[0], elements[i], sigma))
            i += 1
        COM_leg_red_list.append(temp_list)
    return COM_leg_red_list


def tetr_face_input_coord(radius: float, sigma: float):
    coor = tetr_face_leg_reduce_coord_gen(radius, sigma)
    coor_ = np.array(coor[0])
    COM = coor_[0] - coor_[0]
    lg1 = coor_[1] - coor_[0]
    lg2 = coor_[2] - coor_[0]
    lg3 = coor_[3] - coor_[0]
    n = -coor_[0]
    return [COM, lg1, lg2, lg3, n]


def tetr_face_write(radius: float, sigma: float):
    COM, lg1, lg2, lg3, n = tetr_face_input_coord(radius, sigma)
    coord = tetr_face_leg_reduce_coord_gen(radius, sigma)
    theta1, theta2, phi1, phi2, omega = angle_cal(
        coord[0][0], coord[0][1], coord[2][0], coord[2][1])

    f = open('parm.inp', 'w')
    f.write(' # Input file (tetrahedron face-centered)\n\n')
    f.write('start parameters\n')
    f.write('    nItr = 10000000 #iterations\n')
    f.write('    timeStep = 0.1\n')
    f.write('    timeWrite = 10000\n')
    f.write('    pdbWrite = 10000\n')
    f.write('    trajWrite = 10000\n')
    f.write('    restartWrite = 50000\n')
    f.write('    checkPoint = 1000000\n')
    f.write('    overlapSepLimit = 7.0\n')
    f.write('end parameters\n\n')
    f.write('start boundaries\n')
    f.write('    WaterBox = [500,500,500]\n')
    f.write('end boundaries\n\n')
    f.write('start molecules\n')
    f.write('    tetr : 200\n')
    f.write('end molecules\n\n')
    f.write('start reactions\n')
    f.write('    tetr(lg1) + tetr(lg1) <-> tetr(lg1!1).tetr(lg1!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    tetr(lg2) + tetr(lg2) <-> tetr(lg2!1).tetr(lg2!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    tetr(lg3) + tetr(lg3) <-> tetr(lg3!1).tetr(lg3!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    tetr(lg1) + tetr(lg2) <-> tetr(lg1!1).tetr(lg2!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    tetr(lg1) + tetr(lg3) <-> tetr(lg1!1).tetr(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    tetr(lg2) + tetr(lg3) <-> tetr(lg2!1).tetr(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [' + str(theta1) + ', ' + str(theta2) +
            ', ' + str(phi1) + ', ' + str(phi2) + ', ' + str(omega) + ']\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('end reactions\n')

    f = open('tetr.mol', 'w')
    f.write('##\n')
    f.write('# Tetrahedron (face-centered) information file.\n')
    f.write('##\n\n')
    f.write('Name = tetr\n')
    f.write('checkOverlap = true\n\n')
    f.write('# translational diffusion constants\n')
    f.write('D = [13.0, 13.0, 13.0]\n\n')
    f.write('# rotational diffusion constants\n')
    f.write('Dr = [0.03, 0.03, 0.03]\n\n')
    f.write('# Coordinates\n')
    f.write('COM   ' + str(round(COM[0], 8)) + '   ' +
            str(round(COM[1], 8)) + '   ' + str(round(COM[2], 8)) + '\n')
    f.write('lg1   ' + str(round(lg1[0], 8)) + '   ' +
            str(round(lg1[1], 8)) + '   ' + str(round(lg1[2], 8)) + '\n')
    f.write('lg2   ' + str(round(lg2[0], 8)) + '   ' +
            str(round(lg2[1], 8)) + '   ' + str(round(lg2[2], 8)) + '\n')
    f.write('lg3   ' + str(round(lg3[0], 8)) + '   ' +
            str(round(lg3[1], 8)) + '   ' + str(round(lg3[2], 8)) + '\n')
    f.write('\n')
    f.write('# bonds\n')
    f.write('bonds = 3\n')
    f.write('com lg1\n')
    f.write('com lg2\n')
    f.write('com lg3\n')
    f.write('\n')


# TETRAHEDRON VERTEX AS COM

def tetr_vert_coord(radius: float):
    scaler = radius/(3/8)**0.5/2
    v0 = [1, 0, -1/2**0.5]
    v1 = [-1, 0, -1/2**0.5]
    v2 = [0, 1, 1/2**0.5]
    v3 = [0, -1, 1/2**0.5]
    VertCoord = [v0, v1, v2, v3]
    VertCoord_ = []
    for i in VertCoord:
        temp_list = []
        for j in i:
            temp = j*scaler
            temp_list.append(temp)
        VertCoord_.append(temp_list)
    return VertCoord_


def tetr_vert_COM_leg(COM: float, a: float, b: float, c: float):
    lega = mid_pt(COM, a)
    legb = mid_pt(COM, b)
    legc = mid_pt(COM, c)
    return [np.around(COM, 10), np.around(lega, 10), np.around(legb, 10), np.around(legc, 10)]


def tetr_vert_COM_leg_gen(radius: float):
    coord = tetr_vert_coord(radius)
    COM_leg_list = []
    COM_leg_list.append(tetr_vert_COM_leg(
        coord[0], coord[1], coord[2], coord[3]))
    COM_leg_list.append(tetr_vert_COM_leg(
        coord[1], coord[2], coord[3], coord[0]))
    COM_leg_list.append(tetr_vert_COM_leg(
        coord[2], coord[3], coord[0], coord[1]))
    COM_leg_list.append(tetr_vert_COM_leg(
        coord[3], coord[0], coord[1], coord[2]))
    return COM_leg_list


def tetr_vert_leg_reduce(COM: float, leg: float, sigma: float):
    red_len = sigma/2
    ratio = 1 - red_len/distance(COM, leg)
    leg_red = []
    for i in range(0, 3):
        leg_red.append(round((leg[i] - COM[i])*ratio + COM[i], 8))
    return leg_red


def tetr_vert_leg_reduce_coor_gen(radius: float, sigma: float):
    # Generating all the coords of COM and legs when sigma exists
    COM_leg_list = tetr_vert_COM_leg_gen(radius)
    COM_leg_red_list = []
    for elements in COM_leg_list:
        temp_list = []
        temp_list.append(elements[0])
        i = 1
        while i <= 3:
            temp_list.append(tetr_vert_leg_reduce(
                elements[0], elements[i], sigma))
            i += 1
        COM_leg_red_list.append(temp_list)
    return COM_leg_red_list


def tetr_vert_input_coord(radius: float, sigma: float):
    coor = tetr_vert_leg_reduce_coor_gen(radius, sigma)
    coor_ = np.array(coor[0])
    COM = np.around(coor_[0] - coor_[0], 8)
    lg1 = np.around(coor_[1] - coor_[0], 8)
    lg2 = np.around(coor_[2] - coor_[0], 8)
    lg3 = np.around(coor_[3] - coor_[0], 8)
    n = np.around(coor_[0]/np.linalg.norm(coor_[0]), 8)
    return COM, lg1, lg2, lg3, n


def tetr_vert_norm_input(radius: float, sigma: float):
    COM, lg1, lg2, lg3, n = tetr_vert_input_coord(radius, sigma)
    length = distance(lg1, lg2)
    dis1 = ((-length/2)**2+(-((length/2)*(3**0.5))/3)**2)**0.5
    dis2 = distance(COM, lg1)
    height = (dis2**2-dis1**2)**0.5
    lg1_ = np.array([-length/2, -((length/2)*(3**0.5))/3, -height])
    lg2_ = np.array([length/2, -((length/2)*(3**0.5))/3, -height])
    lg3_ = np.array([0, ((length/2)*(3**0.5))/3*2, -height])
    COM_ = np.array([0, 0, 0])
    n_ = np.array([0, 0, 1])
    return COM_, lg1_, lg2_, lg3_, n_


def tetr_vert_write(radius: float, sigma: float):
    COM, lg1, lg2, lg3, n = tetr_vert_norm_input(radius, sigma)
    f = open('parm.inp', 'w')
    f.write(' # Input file (tetrahedron vertex-centered)\n\n')
    f.write('start parameters\n')
    f.write('    nItr = 10000000 #iterations\n')
    f.write('    timeStep = 0.1\n')
    f.write('    timeWrite = 10000\n')
    f.write('    pdbWrite = 10000\n')
    f.write('    trajWrite = 10000\n')
    f.write('    restartWrite = 50000\n')
    f.write('    checkPoint = 1000000\n')
    f.write('    overlapSepLimit = 7.0\n')
    f.write('end parameters\n\n')
    f.write('start boundaries\n')
    f.write('    WaterBox = [500,500,500]\n')
    f.write('end boundaries\n\n')
    f.write('start molecules\n')
    f.write('    tetr : 200\n')
    f.write('end molecules\n\n')
    f.write('start reactions\n')
    f.write('    tetr(lg1) + tetr(lg1) <-> tetr(lg1!1).tetr(lg1!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    tetr(lg2) + tetr(lg2) <-> tetr(lg2!1).tetr(lg2!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    tetr(lg3) + tetr(lg3) <-> tetr(lg3!1).tetr(lg3!1)\n')
    f.write('    onRate3Dka = 2\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    tetr(lg1) + tetr(lg2) <-> tetr(lg1!1).tetr(lg2!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    tetr(lg1) + tetr(lg3) <-> tetr(lg1!1).tetr(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('    tetr(lg2) + tetr(lg3) <-> tetr(lg2!1).tetr(lg3!1)\n')
    f.write('    onRate3Dka = 4\n')
    f.write('    offRatekb = 2\n')
    f.write('    norm1 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    norm2 = [' + str(n[0]) + ', ' +
            str(n[1]) + ', ' + str(n[2]) + ']\n')
    f.write('    sigma = ' + str(float(sigma)) + '\n')
    f.write('    assocAngles = [M_PI, M_PI, nan, nan, 0]\n')
    f.write('    observeLabel = leg\n')
    f.write('    bindRadSameCom = 5.0\n')
    f.write('\n')
    f.write('end reactions\n')

    f = open('tetr.mol', 'w')
    f.write('##\n')
    f.write('# Tetrahedron (vertex-centered) information file.\n')
    f.write('##\n\n')
    f.write('Name = tetr\n')
    f.write('checkOverlap = true\n\n')
    f.write('# translational diffusion constants\n')
    f.write('D = [13.0, 13.0, 13.0]\n\n')
    f.write('# rotational diffusion constants\n')
    f.write('Dr = [0.03, 0.03, 0.03]\n\n')
    f.write('# Coordinates\n')
    f.write('COM   ' + str(round(COM[0], 8)) + '   ' +
            str(round(COM[1], 8)) + '   ' + str(round(COM[2], 8)) + '\n')
    f.write('lg1   ' + str(round(lg1[0], 8)) + '   ' +
            str(round(lg1[1], 8)) + '   ' + str(round(lg1[2], 8)) + '\n')
    f.write('lg2   ' + str(round(lg2[0], 8)) + '   ' +
            str(round(lg2[1], 8)) + '   ' + str(round(lg2[2], 8)) + '\n')
    f.write('lg3   ' + str(round(lg3[0], 8)) + '   ' +
            str(round(lg3[1], 8)) + '   ' + str(round(lg3[2], 8)) + '\n')
    f.write('\n')
    f.write('# bonds\n')
    f.write('bonds = 3\n')
    f.write('com lg1\n')
    f.write('com lg2\n')
    f.write('com lg3\n')
    f.write('\n')


def tetr_face(radius: float, sigma: float):
    tetr_face_write(radius, sigma)
    print('File writing complete!')
    return 0


def cube_face(radius: float, sigma: float):
    cube_face_write(radius, sigma)
    print('File writing complete!')
    return 0


def octa_face(radius: float, sigma: float):
    octa_face_write(radius, sigma)
    print('File writing complete!')
    return 0


def dode_face(radius: float, sigma: float):
    dode_face_write(radius, sigma)
    print('File writing complete!')
    return 0


def icos_face(radius: float, sigma: float):
    icos_face_write(radius, sigma)
    print('File writing complete!')
    return 0


def tetr_vert(radius: float, sigma: float):
    tetr_vert_write(radius, sigma)
    print('File writing complete!')
    return 0


def cube_vert(radius: float, sigma: float):
    cube_vert_write(radius, sigma)
    print('File writing complete!')
    return 0


def octa_vert(radius: float, sigma: float):
    octa_vert_write(radius, sigma)
    print('File writing complete!')
    return 0


def dode_vert(radius: float, sigma: float):
    dode_vert_write(radius, sigma)
    print('File writing complete!')
    return 0


def icos_vert(radius: float, sigma: float):
    icos_vert_write(radius, sigma)
    print('File writing complete!')
    return 0

# -----------------------------------Data Visualization------------------------------

# Analysis tools for 'histogram_complexes_time.dat' file


def read_file(FileName: str, SpeciesName: str):
    hist = []
    hist_temp = []
    hist_conv = []
    hist_count = []
    with open(FileName, 'r') as file:
        for line in file.readlines():
            if line[0:4] == 'Time':
                if hist_count != [] and hist_conv != []:
                    hist_temp.append(hist_count)
                    hist_temp.append(hist_conv)
                    hist.append(hist_temp)
                hist_count = []
                hist_conv = []
                hist_temp = []
                hist_temp.append(float(line.strip('Time (s): ')))
            else:
                string = '	' + str(SpeciesName) + ': '
                line = line.strip('. \n').split(string)
                if len(line) != 2:
                    print('Wrong species name!')
                    return 0
                else:
                    hist_count.append(int(line[0]))
                    hist_conv.append(int(line[1]))
            hist_temp.append(hist_count)
            hist_temp.append(hist_conv)
            hist.append(hist_temp)
        return hist


def time_valid(FileName: str, InitialTime: float, FinalTime: float, SpeciesName: str):
    hist = read_file(FileName, SpeciesName)
    min_time = hist[0][0]
    max_time = hist[-1][0]
    if InitialTime == -1 and FinalTime == -1:
        return min_time, max_time
    elif min_time <= InitialTime <= max_time and InitialTime <= FinalTime <= max_time:
        return InitialTime, FinalTime
    else:
        print('Wrong input time period!')
        return -1.0, -1.0


def hist(FileName: str, InitialTime: float, FinalTime: float, SpeciesName: str, SaveFig: bool = False):
    t_i, t_f = time_valid(FileName, InitialTime, FinalTime, SpeciesName)
    if t_i != -1 and t_f != -1:
        hist = read_file(FileName, SpeciesName)
        plot_count = []
        plot_conv = []
        tot = 0
        for i in hist:
            if t_i <= i[0] <= t_f:
                tot += 1
                for j in i[2]:
                    if j not in plot_conv:
                        plot_conv.append(j)
                        plot_count.append(i[1][i[2].index(j)])
                    else:
                        index = plot_conv.index(j)
                        plot_count[index] += i[1][i[2].index(j)]
        plot_count_mean = []
        for i in plot_count:
            plot_count_mean.append(i/tot)
        print('Start time(s): ', t_i)
        print('End time(s): ', t_f)
        plt.bar(plot_conv, plot_count_mean)
        plt.title('Histogram of ' + str(SpeciesName))
        plt.xlabel('# of ' + SpeciesName + ' in sigle complex')
        plt.ylabel('Count')
        if SaveFig:
            plt.savefig('Histogram.png', dpi=500)
        plt.show()
        return 0
    else:
        return 0


def max_complex(FileName: str, InitialTime: float, FinalTime: float, SpeciesName: str, SaveFig: bool = False):
    t_i, t_f = time_valid(FileName, InitialTime, FinalTime, SpeciesName)
    if t_i != -1 and t_f != -1:
        hist = read_file(FileName, SpeciesName)
        plot_time = []
        plot_conv = []
        for i in hist:
            if t_i <= i[0] <= t_f:
                plot_time.append(i[0])
                plot_conv.append(max(i[2]))
        print('Start time(s): ', t_i)
        print('End time(s): ', t_f)
        plt.plot(plot_time, plot_conv)
        plt.title('Maximum Number of ' +
                  str(SpeciesName) + ' in Single Complex')
        plt.xlabel('Time')
        plt.ylabel('Maximum Number of ' + str(SpeciesName))
        if SaveFig:
            plt.savefig('max_complex.png', dpi=500)
        plt.show()
        return 0
    else:
        return 0


def mean_complex(FileName: str, InitialTime: float, FinalTime: float, SpeciesName: str, ExcludeNum: int = 0, SaveFig: bool = False):
    t_i, t_f = time_valid(FileName, InitialTime, FinalTime, SpeciesName)
    if t_i != -1 and t_f != -1:
        hist = read_file(FileName, SpeciesName)
        plot_time = []
        plot_conv = []
        if ExcludeNum == 0:
            for i in hist:
                if t_i <= i[0] <= t_f:
                    plot_time.append(i[0])
                    plot_conv.append(np.mean(i[2]))
        elif ExcludeNum > 0:
            for i in hist:
                if t_i <= i[0] <= t_f:
                    count = 1
                    N = 0
                    temp_sum = 0
                    plot_time.append(i[0])
                    while count <= len(i[1]):
                        if i[2][count-1] >= ExcludeNum:
                            temp_sum += i[2][count-1]
                            N += 1
                        if count == len(i[1]):
                            if N != 0:
                                plot_conv.append(temp_sum/N)
                            else:
                                plot_conv.append(0)
                        count += 1
        else:
            print('ExcludeNum cannot smaller than 0!')
            return 0
        print('Start time(s): ', t_i)
        print('End time(s): ', t_f)
        print('Exclude Number: ', ExcludeNum)
        plt.plot(plot_time, plot_conv)
        plt.title('Average Number of ' +
                  str(SpeciesName) + ' in Single Complex')
        plt.xlabel('Time (s)')
        plt.ylabel('Average Number of ' + str(SpeciesName))
        if SaveFig:
            plt.savefig('mean_complex.png', dpi=500)
        plt.show()
        return 0
    else:
        return 0


def single_hist_to_csv(FileName: str):
    name_list = ['Time (s)']
    with open(FileName, 'r') as file:
        for line in file.readlines():
            if line[0:9] != 'Time (s):':
                name = line.split('	')[1].strip(' \n')
                name_num = int(line.split('	')[1].split(' ')[1].strip('.'))
                if name_list != ['Time (s)']:
                    last_num = int(name_list[-1].split(' ')[1].strip('.'))
                else:
                    last_num = 0
                if name not in name_list:
                    if name_num-last_num == 1:
                        name_list.append(name)
                    else:
                        fill = range(last_num+1, name_num)
                        for i in fill:
                            name = str(line.split('	')[1].split(
                                ' ')[0]) + ' ' + str(i) + '.'
                            name_list.append(name)
    file.close()
    with open(FileName, 'r') as read_file, open('histogram.csv', 'w') as write_file:
        head = ''
        for i in name_list:
            head += i
            if i != name_list[-1]:
                head += ','
            else:
                head += '\n'
        write_file.write(head)
        stat = np.zeros(len(name_list))
        for line in read_file.readlines():
            if line[0:9] == 'Time (s):':
                if line != 'Time (s): 0\n':
                    write_line = ''
                    for i in range(len(stat)):
                        write_line += str(stat[i])
                        if i != len(stat)-1:
                            write_line += ','
                        else:
                            write_line += '\n'
                    write_file.write(write_line)
                stat = np.zeros(len(name_list))
                write_line = ''
                info = float(line.split(' ')[-1])
                stat[0] += info
            else:
                name = line.split('	')[-1].strip(' \n')
                num = float(line.split('	')[0])
                index = name_list.index(name)
                stat[index] += num
        for i in range(len(stat)):
            write_line += str(stat[i])
            if i != len(stat)-1:
                write_line += ','
            else:
                write_line += '\n'
        write_file.write(write_line)
    read_file.close()
    write_file.close()
    print('CSV writing completed!')
    return 0


def single_hist_to_df(FileName: str, SaveCsv: bool = True):
    single_hist_to_csv(FileName)
    df = pd.read_csv('histogram.csv')
    if not SaveCsv:
        os.remove('histogram.csv')
        print('CSV deleted!')
    return df


def multi_hist_to_csv(FileName: str):
    name_list = ['Time (s)']
    with open(FileName, 'r') as file:
        for line in file.readlines():
            if line[0:9] != 'Time (s):':
                name = line.split('	')[1].strip(' \n')
                if name not in name_list:
                    name_list.append(name)
    file.close()
    with open(FileName, 'r') as read_file, open('histogram.csv', 'w') as write_file:
        head = ''
        for i in name_list:
            head += i
            if i != name_list[-1]:
                head += ','
            else:
                head += '\n'
        write_file.write(head)
        stat = np.zeros(len(name_list))
        for line in read_file.readlines():
            if line[0:9] == 'Time (s):':
                if line != 'Time (s): 0\n':
                    write_line = ''
                    for i in range(len(stat)):
                        write_line += str(stat[i])
                        if i != len(stat)-1:
                            write_line += ','
                        else:
                            write_line += '\n'
                    write_file.write(write_line)
                stat = np.zeros(len(name_list))
                write_line = ''
                info = float(line.split(' ')[-1])
                stat[0] += info
            else:
                name = line.split('	')[-1].strip(' \n')
                num = float(line.split('	')[0])
                index = name_list.index(name)
                stat[index] += num
        for i in range(len(stat)):
            write_line += str(stat[i])
            if i != len(stat)-1:
                write_line += ','
            else:
                write_line += '\n'
        write_file.write(write_line)
    read_file.close()
    write_file.close()
    print('CSV writing completed!')
    return 0


def multi_hist_to_df(FileName: str, SaveCsv: bool = True):
    multi_hist_to_csv(FileName)
    df = pd.read_csv('histogram.csv')
    if not SaveCsv:
        os.remove('histogram.csv')
        print('CSV deleted!')
    return df


def hist_temp(FileName: str, InitialTime: float, FinalTime: float, SpeciesName: str):
    t_i, t_f = time_valid(FileName, InitialTime, FinalTime, SpeciesName)
    if t_i != -1 and t_f != -1:
        hist = read_file(FileName, SpeciesName)
        plot_count = []
        plot_conv = []
        tot = 0
        for i in hist:
            if t_i <= i[0] <= t_f:
                tot += 1
                for j in i[2]:
                    if j not in plot_conv:
                        plot_conv.append(j)
                        plot_count.append(i[1][i[2].index(j)])
                    else:
                        index = plot_conv.index(j)
                        plot_count[index] += i[1][i[2].index(j)]
        plot_count_mean = []
        for i in plot_count:
            plot_count_mean.append(i/tot)
        return plot_conv, plot_count_mean
    else:
        return 0


def hist_3d_time(FileName: str, InitialTime: float, FinalTime: float, SpeciesName: str, TimeBins: int):
    InitialTime, FinalTime = time_valid(
        FileName, InitialTime, FinalTime, SpeciesName)
    t_arr = np.arange(InitialTime, FinalTime, (FinalTime-InitialTime)/TimeBins)
    t_arr = np.append(t_arr, FinalTime)
    max_num = 0
    x_lst = []
    z_lst = []
    t_plt = np.zeros(TimeBins)
    i = 0
    for i in range(0, len(t_arr)-1):
        t_plt[i] = (t_arr[i]+t_arr[i+1])/2
        x, z = hist_temp(FileName, t_arr[i], t_arr[i+1], SpeciesName)
        x_lst.append(x)
        z_lst.append(z)
        if max(x) > max_num:
            max_num = max(x)
    z_plt = np.zeros(shape=(max_num, TimeBins))
    k = 0
    for i in x_lst:
        l = 0
        for j in i:
            z_plt[j-1, k] = z_lst[k][l]
            l += 1
        k += 1
    x_plt = np.arange(0, max_num, 1)+1
    xx, yy = np.meshgrid(x_plt, t_plt)
    X, Y = xx.ravel(), yy.ravel()
    Z = z_plt.ravel()
    bottom = np.zeros_like(Z)
    width = 1
    depth = 1/TimeBins
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.bar3d(X, Y, bottom, width, depth, Z, shade=True)
    ax.set_xlabel('# of ' + SpeciesName + ' in sigle complex')
    ax.set_ylabel('Averaged Time')
    ax.set_zlabel('Relative Occurrence Probability')
    plt.show()
    return 0


def hist_time_heatmap(FileName: str, InitialTime: float, FinalTime: float, SpeciesName: str, TimeBins: int, ShowNum: bool = True, SaveFig: bool = False):
    InitialTime, FinalTime = time_valid(
        FileName, InitialTime, FinalTime, SpeciesName)
    t_arr = np.arange(InitialTime, FinalTime, (FinalTime-InitialTime)/TimeBins)
    t_arr = np.append(t_arr, FinalTime)
    max_num = 0
    x_lst = []
    z_lst = []
    t_plt = []
    i = 0
    for i in range(0, len(t_arr)-1):
        t_plt.append(str(round(t_arr[i], 2)) +
                     's ~ ' + str(round(t_arr[i+1], 2)) + 's')
        x, z = hist_temp(FileName, t_arr[i], t_arr[i+1], SpeciesName)
        x_lst.append(x)
        z_lst.append(z)
        if max(x) > max_num:
            max_num = max(x)
    z_plt = np.zeros(shape=(max_num, TimeBins))
    k = 0
    for i in x_lst:
        l = 0
        for j in i:
            z_plt[j-1, k] = z_lst[k][l]
            l += 1
        k += 1
    x_plt = np.arange(0, max_num, 1)+1
    z_plt_ = np.array(z_plt).T

    fig, ax = plt.subplots()
    im = ax.imshow(z_plt_)
    ax.set_xticks(np.arange(len(x_plt)))
    ax.set_yticks(np.arange(len(t_plt)))
    ax.set_xticklabels(x_plt)
    ax.set_yticklabels(t_plt)
    if ShowNum:
        for i in range(len(t_plt)):
            for j in range(len(x_plt)):
                text = ax.text(j, i, round(
                    z_plt_[i, j], 1), ha='center', va='center', color='w')
    ax.set_title('N-mers distribution vs. Time')
    fig.tight_layout()
    plt.colorbar(im)
    plt.xlabel('Size of N-mers')
    plt.ylabel('Averaged Time')
    if SaveFig:
        plt.savefig('hist_heatmap.png', dpi=500, bbox_inches='tight')
    plt.show()
    return 0


def hist_time_heatmap_mono_count(FileName: str, InitialTime: float, FinalTime: float, SpeciesName: str, TimeBins: int, ShowNum: bool = True, SaveFig: bool = False):
    InitialTime, FinalTime = time_valid(
        FileName, InitialTime, FinalTime, SpeciesName)
    t_arr = np.arange(InitialTime, FinalTime, (FinalTime-InitialTime)/TimeBins)
    t_arr = np.append(t_arr, FinalTime)
    max_num = 0
    x_lst = []
    z_lst = []
    t_plt = []
    i = 0
    for i in range(0, len(t_arr)-1):
        t_plt.append(str(round(t_arr[i], 2)) +
                     's ~ ' + str(round(t_arr[i+1], 2)) + 's')
        x, z = hist_temp(FileName, t_arr[i], t_arr[i+1], SpeciesName)
        x_lst.append(x)
        z_lst.append(z)
        if max(x) > max_num:
            max_num = max(x)
    z_plt = np.zeros(shape=(max_num, TimeBins))
    k = 0
    for i in x_lst:
        l = 0
        for j in i:
            z_plt[j-1, k] = z_lst[k][l]
            l += 1
        k += 1
    x_plt = np.arange(0, max_num, 1)+1
    const = 1
    z_plt_mod = []
    for i in z_plt:
        z_plt_mod_temp = []
        for j in i:
            z_plt_mod_temp.append(j * const)
        const += 1
        z_plt_mod.append(z_plt_mod_temp)
    z_plt_ = np.array(z_plt_mod).T

    fig, ax = plt.subplots()
    im = ax.imshow(z_plt_)
    ax.set_xticks(np.arange(len(x_plt)))
    ax.set_yticks(np.arange(len(t_plt)))
    ax.set_xticklabels(x_plt)
    ax.set_yticklabels(t_plt)
    if ShowNum:
        for i in range(len(t_plt)):
            for j in range(len(x_plt)):
                text = ax.text(j, i, round(
                    z_plt_[i, j], 1), ha='center', va='center', color='w')
    ax.set_title('Total Number of Monomers in Complexes  vs. Time')
    fig.tight_layout()
    plt.colorbar(im)
    plt.xlabel('Size of N-mers')
    plt.ylabel('Averaged Time')
    if SaveFig:
        plt.savefig('hist_heatmap_count.png', dpi=500, bbox_inches='tight')
    plt.show()
    return 0


def hist_time_heatmap_fraction(FileName: str, InitialTime: float, FinalTime: float, SpeciesName: str, TimeBins: int, ShowNum: bool = True, SaveFig: bool = False):
    InitialTime, FinalTime = time_valid(
        FileName, InitialTime, FinalTime, SpeciesName)
    t_arr = np.arange(InitialTime, FinalTime, (FinalTime-InitialTime)/TimeBins)
    t_arr = np.append(t_arr, FinalTime)
    xx, zz = hist_temp(FileName, 0, 0, SpeciesName)
    n_tot = sum(zz)
    max_num = 0
    x_lst = []
    z_lst = []
    t_plt = []
    i = 0
    for i in range(0, len(t_arr)-1):
        t_plt.append(str(round(t_arr[i], 2)) +
                     's ~ ' + str(round(t_arr[i+1], 2)) + 's')
        x, z = hist_temp(FileName, t_arr[i], t_arr[i+1], SpeciesName)
        x_lst.append(x)
        z_lst.append(z)
        if max(x) > max_num:
            max_num = max(x)
    z_plt = np.zeros(shape=(max_num, TimeBins))
    k = 0
    for i in x_lst:
        l = 0
        for j in i:
            z_plt[j-1, k] = z_lst[k][l]
            l += 1
        k += 1
    x_plt = np.arange(0, max_num, 1)+1
    const = 1
    z_plt_mod = []
    for i in z_plt:
        z_plt_mod_temp = []
        for j in i:
            z_plt_mod_temp.append(j * const / n_tot)
        const += 1
        z_plt_mod.append(z_plt_mod_temp)
    z_plt_ = np.array(z_plt_mod).T
    fig, ax = plt.subplots()
    im = ax.imshow(z_plt_)
    ax.set_xticks(np.arange(len(x_plt)))
    ax.set_yticks(np.arange(len(t_plt)))
    ax.set_xticklabels(x_plt)
    ax.set_yticklabels(t_plt)
    if ShowNum:
        for i in range(len(t_plt)):
            for j in range(len(x_plt)):
                text = ax.text(j, i, round(
                    z_plt_[i, j], 2), ha='center', va='center', color='w')
    ax.set_title('Franction of Monomers in Complexes vs. Time')
    fig.tight_layout()
    plt.colorbar(im)
    plt.xlabel('Size of N-mers')
    plt.ylabel('Averaged Time')
    if SaveFig:
        plt.savefig('hist_heatmap_fraction.png', dpi=500, bbox_inches='tight')
    plt.show()
    return 0

# Analysing tools for 'transition_matrix_time.dat'


def read_transition_matrix(FileName: str, SpeciesName: str, InitialTime: float, FinalTime: float):
    ti_switch = False
    tf_switch = False
    spec_switch = False
    ti_matrix = []
    tf_matrix = []
    with open(FileName, 'r') as file:
        for line in file.readlines():
            if line[0:5] == 'time:':
                if float(line.split(' ')[1]) == InitialTime:
                    ti_switch = True
                if float(line.split(' ')[1]) == FinalTime:
                    tf_switch = True
                if float(line.split(' ')[1]) != InitialTime:
                    ti_switch = False
                if float(line.split(' ')[1]) != FinalTime:
                    tf_switch = False
            if line[0:8] == 'lifetime':
                ti_switch = False
                tf_switch = False
                spec_switch = False
            if line[0:4] == 'size':
                ti_switch = False
                tf_switch = False
                spec_switch = False
            if line[0:4] == SpeciesName:
                spec_switch = True
            if ti_switch and spec_switch:
                if line != SpeciesName + '\n':
                    info = line.strip(' ').strip('\n').split(' ')
                    temp_list = []
                    for i in info:
                        temp_list.append(int(i))
                    ti_matrix.append(temp_list)
            if tf_switch and spec_switch:
                if line != SpeciesName + '\n':
                    info = line.strip(' ').strip('\n').split(' ')
                    temp_list = []
                    for i in info:
                        temp_list.append(int(i))
                    tf_matrix.append(temp_list)
    ti_matrix = np.array(ti_matrix)
    tf_matrix = np.array(tf_matrix)
    return ti_matrix, tf_matrix


def free_energy(FileName: str, FileNum: int, InitialTime: float, FinalTime: float, SpeciesName: str, SaveFig: bool = False):
    warnings.filterwarnings('ignore')
    matrix_list = []
    file_name_head = FileName.split('.')[0]
    file_name_tail = FileName.split('.')[1]
    for i in range(1, FileNum+1):
        temp_file_name = file_name_head + '_' + str(i) + '.' + file_name_tail
        if FileNum == 1:
            temp_file_name = 'transition_matrix_time.dat'
        ti_matrix, tf_matrix = read_transition_matrix(
            temp_file_name, SpeciesName, InitialTime, FinalTime)
        matrix = tf_matrix - ti_matrix
        matrix_list.append(matrix)
    sum_list_list = []
    for k in range(len(matrix_list)):
        sum_list = np.zeros(len(matrix))
        i = 0
        while i < len(matrix_list[k]):
            j = 0
            while j < len(matrix_list[k][i]):
                if i == j:
                    sum_list[i] += matrix_list[k][i][j]
                elif i > j:
                    if i % 2 == 0:
                        if j <= (i-1)/2:
                            sum_list[i] += matrix_list[k][i][j]
                    else:
                        if j <= i/2:
                            if (i-1)/2 == j:
                                sum_list[i] += matrix_list[k][i][j]/2
                            else:
                                sum_list[i] += matrix_list[k][i][j]
                else:
                    if j % 2 != 0:
                        if i <= j/2:
                            if (j-1)/2 == i:
                                sum_list[i] += matrix_list[k][i][j]/2
                            else:
                                sum_list[i] += matrix_list[k][i][j]
                        else:
                            sum_list[i] += matrix_list[k][i][j]
                    else:
                        sum_list[i] += matrix_list[k][i][j]
                j += 1
            i += 1
        sum_list_list.append(sum_list)
    energy_list_list = []
    for i in range(len(sum_list_list)):
        sum_arr = np.array(sum_list_list[i])
        sum_arr = sum_arr/sum_arr.sum()
        energy_list = np.asarray([])
        for i in sum_arr:
            if i > 0:
                energy_list = np.append(energy_list, -math.log(i))
            else:
                energy_list = np.append(energy_list, np.nan)
        energy_list_list.append(energy_list)
    n_list = list(range(1, 1 + len(matrix_list[0])))
    energy_list_list_rev = []
    for i in range(len(energy_list_list[0])):
        temp = []
        for j in range(len(energy_list_list)):
            temp.append(energy_list_list[j][i])
        energy_list_list_rev.append(temp)
    mean_energy_list = np.array([])
    std_energy_list = np.array([])
    for i in energy_list_list_rev:
        mean_energy_list = np.append(mean_energy_list, np.nanmean(i))
        if FileNum != 1:
            std_energy_list = np.append(std_energy_list, np.nanstd(i))
    errorbar_color = '#c9e3f6'
    plt.plot(n_list, mean_energy_list, 'C0')
    if FileNum != 1:
        plt.errorbar(n_list, mean_energy_list, yerr=std_energy_list,
                     ecolor=errorbar_color, capsize=2)
    plt.title('Free Energy Vs. Time from ' + str(float(InitialTime)
                                                 ) + 's to ' + str(float(FinalTime)) + 's')
    plt.xlabel('N (copies of ' + str(SpeciesName) + ')')
    plt.ylabel('-ln(p(N)) ($k_B$T)')
    plt.xticks(ticks=n_list)
    if SaveFig:
        plt.savefig('free_energy.png', dpi=500)
    plt.show()
    return 0


def associate_prob_symmetric(FileName: str, FileNum: int, InitialTime: float, FinalTime: float, SpeciesName: str, DivideSize: int = 2, SaveFig: bool = False):
    warnings.filterwarnings('ignore')
    matrix_list = []
    file_name_head = FileName.split('.')[0]
    file_name_tail = FileName.split('.')[1]
    for i in range(1, FileNum+1):
        temp_file_name = file_name_head + '_' + str(i) + '.' + file_name_tail
        if FileNum == 1:
            temp_file_name = 'transition_matrix_time.dat'
        ti_matrix, tf_matrix = read_transition_matrix(
            temp_file_name, SpeciesName, InitialTime, FinalTime)
        matrix = tf_matrix - ti_matrix
        matrix_list.append(matrix)
    above = []
    equal = []
    below = []
    for k in range(len(matrix_list)):
        above_temp = np.zeros(len(matrix_list[0][0]))
        equal_temp = np.zeros(len(matrix_list[0][0]))
        below_temp = np.zeros(len(matrix_list[0][0]))
        i = 0
        while i < len(matrix_list[k]):
            j = 0
            while j < len(matrix_list[k][i]):
                if i > j:
                    if i - j == DivideSize:
                        equal_temp[j] += matrix_list[k][i][j]
                    elif i - j > DivideSize:
                        above_temp[j] += matrix_list[k][i][j]
                    else:
                        below_temp[j] += matrix_list[k][i][j]
                j += 1
            i += 1
        above.append(above_temp)
        equal.append(equal_temp)
        below.append(below_temp)
    above_prob = []
    equal_prob = []
    below_prob = []
    for i in range(len(above)):
        above_prob_temp = np.array([])
        equal_prob_temp = np.array([])
        below_prob_temp = np.array([])
        for j in range(len(above[0])):
            sum = above[i][j] + equal[i][j] + below[i][j]
            if sum != 0:
                above_prob_temp = np.append(above_prob_temp, above[i][j]/sum)
                equal_prob_temp = np.append(equal_prob_temp, equal[i][j]/sum)
                below_prob_temp = np.append(below_prob_temp, below[i][j]/sum)
            else:
                above_prob_temp = np.append(above_prob_temp, np.nan)
                equal_prob_temp = np.append(equal_prob_temp, np.nan)
                below_prob_temp = np.append(below_prob_temp, np.nan)
        above_prob.append(above_prob_temp)
        equal_prob.append(equal_prob_temp)
        below_prob.append(below_prob_temp)
    above_prob_rev = []
    for i in range(len(above_prob[0])):
        temp = []
        for j in range(len(above_prob)):
            temp.append(above_prob[j][i])
        above_prob_rev.append(temp)
    equal_prob_rev = []
    for i in range(len(equal_prob[0])):
        temp = []
        for j in range(len(equal_prob)):
            temp.append(equal_prob[j][i])
        equal_prob_rev.append(temp)
    below_prob_rev = []
    for i in range(len(below_prob[0])):
        temp = []
        for j in range(len(below_prob)):
            temp.append(below_prob[j][i])
        below_prob_rev.append(temp)
    mean_above = []
    mean_equal = []
    mean_below = []
    std_above = []
    std_equal = []
    std_below = []
    for i in range(len(above_prob_rev)):
        mean_above.append(np.nanmean(above_prob_rev[i]))
        mean_equal.append(np.nanmean(equal_prob_rev[i]))
        mean_below.append(np.nanmean(below_prob_rev[i]))
        if FileNum != 1:
            std_above.append(np.nanstd(above_prob_rev[i]))
            std_equal.append(np.nanstd(equal_prob_rev[i]))
            std_below.append(np.nanstd(below_prob_rev[i]))
    n_list = list(range(1, 1 + len(matrix_list[0])))
    errorbar_color_1 = '#c9e3f6'
    errorbar_color_2 = '#ffe7d2'
    errorbar_color_3 = '#d7f4d7'
    plt.plot(n_list, mean_above, 'C0')
    plt.plot(n_list, mean_equal, 'C1')
    plt.plot(n_list, mean_below, 'C2')
    if FileNum != 1:
        plt.errorbar(n_list, mean_above, yerr=std_above,
                     ecolor=errorbar_color_1, capsize=2)
        plt.errorbar(n_list, mean_equal, yerr=std_equal,
                     ecolor=errorbar_color_2, capsize=2)
        plt.errorbar(n_list, mean_below, yerr=std_below,
                     ecolor=errorbar_color_3, capsize=2)
    plt.legend(['Associate Size > ' + str(DivideSize), 'Associate Size = ' +
               str(DivideSize), 'Associate Size < ' + str(DivideSize)])
    plt.xlabel('N (copies of ' + str(SpeciesName) + ')')
    plt.ylabel('Probability')
    plt.xticks(ticks=n_list)
    plt.title('Remodeling of Complex')
    if SaveFig:
        plt.savefig('associate_probability_symmetric.png', dpi=500)
    plt.show()
    return 0


def associate_prob_asymmetric(FileName: str, FileNum: int, InitialTime: float, FinalTime: float, SpeciesName: str, DivideSize: int = 2, SaveFig: bool = False):
    warnings.filterwarnings('ignore')
    matrix_list = []
    file_name_head = FileName.split('.')[0]
    file_name_tail = FileName.split('.')[1]
    for i in range(1, FileNum+1):
        temp_file_name = file_name_head + '_' + str(i) + '.' + file_name_tail
        if FileNum == 1:
            temp_file_name = 'transition_matrix_time.dat'
        ti_matrix, tf_matrix = read_transition_matrix(
            temp_file_name, SpeciesName, InitialTime, FinalTime)
        matrix = tf_matrix - ti_matrix
        matrix_list.append(matrix)
    above = []
    equal = []
    below = []
    for k in range(len(matrix_list)):
        above_temp = np.zeros(len(matrix_list[0][0]))
        equal_temp = np.zeros(len(matrix_list[0][0]))
        below_temp = np.zeros(len(matrix_list[0][0]))
        i = 0
        while i < len(matrix_list[k]):
            j = 0
            while j < len(matrix_list[k][i]):
                if i > j:
                    if i % 2 == 0:
                        if j >= (i-1)/2:
                            if i - j == DivideSize:
                                equal_temp[j] += matrix_list[k][i][j]
                            elif i - j > DivideSize:
                                above_temp[j] += matrix_list[k][i][j]
                            else:
                                below_temp[j] += matrix_list[k][i][j]
                    else:
                        if j >= int(i/2):
                            if (i-1)/2 == j:
                                if i - j == DivideSize:
                                    equal_temp[j] += matrix_list[k][i][j]/2
                                elif i - j > DivideSize:
                                    above_temp[j] += matrix_list[k][i][j]/2
                                else:
                                    below_temp[j] += matrix_list[k][i][j]/2
                            else:
                                if i - j == DivideSize:
                                    equal_temp[j] += matrix_list[k][i][j]
                                elif i - j > DivideSize:
                                    above_temp[j] += matrix_list[k][i][j]
                                else:
                                    below_temp[j] += matrix_list[k][i][j]
                j += 1
            i += 1
        above.append(above_temp)
        equal.append(equal_temp)
        below.append(below_temp)
    above_prob = []
    equal_prob = []
    below_prob = []
    for i in range(len(above)):
        above_prob_temp = np.array([])
        equal_prob_temp = np.array([])
        below_prob_temp = np.array([])
        for j in range(len(above[0])):
            sum = above[i][j] + equal[i][j] + below[i][j]
            if sum != 0:
                above_prob_temp = np.append(above_prob_temp, above[i][j]/sum)
                equal_prob_temp = np.append(equal_prob_temp, equal[i][j]/sum)
                below_prob_temp = np.append(below_prob_temp, below[i][j]/sum)
            else:
                above_prob_temp = np.append(above_prob_temp, np.nan)
                equal_prob_temp = np.append(equal_prob_temp, np.nan)
                below_prob_temp = np.append(below_prob_temp, np.nan)
        above_prob.append(above_prob_temp)
        equal_prob.append(equal_prob_temp)
        below_prob.append(below_prob_temp)
    above_prob_rev = []
    for i in range(len(above_prob[0])):
        temp = []
        for j in range(len(above_prob)):
            temp.append(above_prob[j][i])
        above_prob_rev.append(temp)
    equal_prob_rev = []
    for i in range(len(equal_prob[0])):
        temp = []
        for j in range(len(equal_prob)):
            temp.append(equal_prob[j][i])
        equal_prob_rev.append(temp)
    below_prob_rev = []
    for i in range(len(below_prob[0])):
        temp = []
        for j in range(len(below_prob)):
            temp.append(below_prob[j][i])
        below_prob_rev.append(temp)
    mean_above = []
    mean_equal = []
    mean_below = []
    std_above = []
    std_equal = []
    std_below = []
    for i in range(len(above_prob_rev)):
        mean_above.append(np.nanmean(above_prob_rev[i]))
        mean_equal.append(np.nanmean(equal_prob_rev[i]))
        mean_below.append(np.nanmean(below_prob_rev[i]))
        if FileNum != 1:
            std_above.append(np.nanstd(above_prob_rev[i]))
            std_equal.append(np.nanstd(equal_prob_rev[i]))
            std_below.append(np.nanstd(below_prob_rev[i]))
    n_list = list(range(1, 1 + len(matrix_list[0])))
    errorbar_color_1 = '#c9e3f6'
    errorbar_color_2 = '#ffe7d2'
    errorbar_color_3 = '#d7f4d7'
    plt.plot(n_list, mean_above, 'C0')
    plt.plot(n_list, mean_equal, 'C1')
    plt.plot(n_list, mean_below, 'C2')
    if FileNum != 1:
        plt.errorbar(n_list, mean_above, yerr=std_above,
                     ecolor=errorbar_color_1, capsize=2)
        plt.errorbar(n_list, mean_equal, yerr=std_equal,
                     ecolor=errorbar_color_2, capsize=2)
        plt.errorbar(n_list, mean_below, yerr=std_below,
                     ecolor=errorbar_color_3, capsize=2)
    plt.legend(['Associate Size > ' + str(DivideSize), 'Associate Size = ' +
               str(DivideSize), 'Associate Size < ' + str(DivideSize)])
    plt.xlabel('N (copies of ' + str(SpeciesName) + ')')
    plt.ylabel('Probability')
    plt.xticks(ticks=n_list)
    plt.title('Remodeling of Complex')
    if SaveFig:
        plt.savefig('associate_probability_asymmetric.png', dpi=500)
    plt.show()
    return 0


def dissociate_prob_symmetric(FileName: str, FileNum: int, InitialTime: float, FinalTime: float, SpeciesName: str, DivideSize: int = 2, SaveFig: bool = False):
    warnings.filterwarnings('ignore')
    matrix_list = []
    file_name_head = FileName.split('.')[0]
    file_name_tail = FileName.split('.')[1]
    for i in range(1, FileNum+1):
        temp_file_name = file_name_head + '_' + str(i) + '.' + file_name_tail
        if FileNum == 1:
            temp_file_name = 'transition_matrix_time.dat'
        ti_matrix, tf_matrix = read_transition_matrix(
            temp_file_name, SpeciesName, InitialTime, FinalTime)
        matrix = tf_matrix - ti_matrix
        matrix_list.append(matrix)
    above = []
    equal = []
    below = []
    for k in range(len(matrix_list)):
        above_temp = np.zeros(len(matrix_list[0][0]))
        equal_temp = np.zeros(len(matrix_list[0][0]))
        below_temp = np.zeros(len(matrix_list[0][0]))
        i = 0
        while i < len(matrix_list[k][0]):
            j = 0
            while j < len(matrix_list[k][i]):
                if i > j:
                    if j + 1 == DivideSize:
                        equal_temp[i] += matrix_list[k][j][i]
                    elif j + 1 > DivideSize:
                        above_temp[i] += matrix_list[k][j][i]
                    else:
                        below_temp[i] += matrix_list[k][j][i]
                j += 1
            i += 1
        above.append(above_temp)
        equal.append(equal_temp)
        below.append(below_temp)
    above_prob = []
    equal_prob = []
    below_prob = []
    for i in range(len(above)):
        above_prob_temp = np.array([])
        equal_prob_temp = np.array([])
        below_prob_temp = np.array([])
        for j in range(len(above[0])):
            sum = above[i][j] + equal[i][j] + below[i][j]
            if sum != 0:
                above_prob_temp = np.append(above_prob_temp, above[i][j]/sum)
                equal_prob_temp = np.append(equal_prob_temp, equal[i][j]/sum)
                below_prob_temp = np.append(below_prob_temp, below[i][j]/sum)
            else:
                above_prob_temp = np.append(above_prob_temp, np.nan)
                equal_prob_temp = np.append(equal_prob_temp, np.nan)
                below_prob_temp = np.append(below_prob_temp, np.nan)
        above_prob.append(above_prob_temp)
        equal_prob.append(equal_prob_temp)
        below_prob.append(below_prob_temp)
    above_prob_rev = []
    for i in range(len(above_prob[0])):
        temp = []
        for j in range(len(above_prob)):
            temp.append(above_prob[j][i])
        above_prob_rev.append(temp)
    equal_prob_rev = []
    for i in range(len(equal_prob[0])):
        temp = []
        for j in range(len(equal_prob)):
            temp.append(equal_prob[j][i])
        equal_prob_rev.append(temp)
    below_prob_rev = []
    for i in range(len(below_prob[0])):
        temp = []
        for j in range(len(below_prob)):
            temp.append(below_prob[j][i])
        below_prob_rev.append(temp)
    mean_above = []
    mean_equal = []
    mean_below = []
    std_above = []
    std_equal = []
    std_below = []
    for i in range(len(above_prob_rev)):
        mean_above.append(np.nanmean(above_prob_rev[i]))
        mean_equal.append(np.nanmean(equal_prob_rev[i]))
        mean_below.append(np.nanmean(below_prob_rev[i]))
        if FileNum != 1:
            std_above.append(np.nanstd(above_prob_rev[i]))
            std_equal.append(np.nanstd(equal_prob_rev[i]))
            std_below.append(np.nanstd(below_prob_rev[i]))
    mean_above = np.nan_to_num(mean_above)
    mean_equal = np.nan_to_num(mean_equal)
    mean_below = np.nan_to_num(mean_below)
    n_list = list(range(1, 1 + len(matrix_list[0])))
    errorbar_color_1 = '#c9e3f6'
    errorbar_color_2 = '#ffe7d2'
    errorbar_color_3 = '#d7f4d7'
    plt.plot(n_list, mean_above, 'C0')
    plt.plot(n_list, mean_equal, 'C1')
    plt.plot(n_list, mean_below, 'C2')
    if FileNum != 1:
        plt.errorbar(n_list, mean_above, yerr=std_above,
                     ecolor=errorbar_color_1, capsize=2)
        plt.errorbar(n_list, mean_equal, yerr=std_equal,
                     ecolor=errorbar_color_2, capsize=2)
        plt.errorbar(n_list, mean_below, yerr=std_below,
                     ecolor=errorbar_color_3, capsize=2)
    plt.legend(['Dissociate Size > ' + str(DivideSize), 'Dissociate Size = ' +
               str(DivideSize), 'Dissociate Size < ' + str(DivideSize)])
    plt.xlabel('N (copies of ' + str(SpeciesName) + ')')
    plt.ylabel('Probability')
    plt.xticks(ticks=n_list)
    plt.title('Remodeling of Complex')
    if SaveFig:
        plt.savefig('dissociate_probability_symmetric.png', dpi=500)
    plt.show()
    return 0


def dissociate_prob_asymmetric(FileName: str, FileNum: int, InitialTime: float, FinalTime: float, SpeciesName: str, DivideSize: int = 2, SaveFig: bool = False):
    warnings.filterwarnings('ignore')
    matrix_list = []
    file_name_head = FileName.split('.')[0]
    file_name_tail = FileName.split('.')[1]
    for i in range(1, FileNum+1):
        temp_file_name = file_name_head + '_' + str(i) + '.' + file_name_tail
        if FileNum == 1:
            temp_file_name = 'transition_matrix_time.dat'
        ti_matrix, tf_matrix = read_transition_matrix(
            temp_file_name, SpeciesName, InitialTime, FinalTime)
        matrix = tf_matrix - ti_matrix
        matrix_list.append(matrix)
    above = []
    equal = []
    below = []
    for k in range(len(matrix_list)):
        above_temp = np.zeros(len(matrix_list[0][0]))
        equal_temp = np.zeros(len(matrix_list[0][0]))
        below_temp = np.zeros(len(matrix_list[0][0]))
        i = 0
        while i < len(matrix_list[k][0]):
            j = 0
            while j < len(matrix_list[k][i]):
                if i > j:
                    if i % 2 == 0:
                        if j <= (i-1)/2:
                            if j + 1 == DivideSize:
                                equal_temp[i] += matrix_list[k][j][i]
                            elif j + 1 > DivideSize:
                                above_temp[i] += matrix_list[k][j][i]
                            else:
                                below_temp[i] += matrix_list[k][j][i]
                    else:
                        if j <= int(i/2):
                            if (i-1)/2 == j:
                                if j + 1 == DivideSize:
                                    equal_temp[i] += matrix_list[k][j][i]/2
                                elif j + 1 > DivideSize:
                                    above_temp[i] += matrix_list[k][j][i]/2
                                else:
                                    below_temp[i] += matrix_list[k][j][i]/2
                            else:
                                if j + 1 == DivideSize:
                                    equal_temp[i] += matrix_list[k][j][i]
                                elif j + 1 > DivideSize:
                                    above_temp[i] += matrix_list[k][j][i]
                                else:
                                    below_temp[i] += matrix_list[k][j][i]
                j += 1
            i += 1
        above.append(above_temp)
        equal.append(equal_temp)
        below.append(below_temp)
    above_prob = []
    equal_prob = []
    below_prob = []
    for i in range(len(above)):
        above_prob_temp = np.array([])
        equal_prob_temp = np.array([])
        below_prob_temp = np.array([])
        for j in range(len(above[0])):
            sum = above[i][j] + equal[i][j] + below[i][j]
            if sum != 0:
                above_prob_temp = np.append(above_prob_temp, above[i][j]/sum)
                equal_prob_temp = np.append(equal_prob_temp, equal[i][j]/sum)
                below_prob_temp = np.append(below_prob_temp, below[i][j]/sum)
            else:
                above_prob_temp = np.append(above_prob_temp, np.nan)
                equal_prob_temp = np.append(equal_prob_temp, np.nan)
                below_prob_temp = np.append(below_prob_temp, np.nan)
        above_prob.append(above_prob_temp)
        equal_prob.append(equal_prob_temp)
        below_prob.append(below_prob_temp)
    above_prob_rev = []
    for i in range(len(above_prob[0])):
        temp = []
        for j in range(len(above_prob)):
            temp.append(above_prob[j][i])
        above_prob_rev.append(temp)
    equal_prob_rev = []
    for i in range(len(equal_prob[0])):
        temp = []
        for j in range(len(equal_prob)):
            temp.append(equal_prob[j][i])
        equal_prob_rev.append(temp)
    below_prob_rev = []
    for i in range(len(below_prob[0])):
        temp = []
        for j in range(len(below_prob)):
            temp.append(below_prob[j][i])
        below_prob_rev.append(temp)
    mean_above = []
    mean_equal = []
    mean_below = []
    std_above = []
    std_equal = []
    std_below = []
    for i in range(len(above_prob_rev)):
        mean_above.append(np.nanmean(above_prob_rev[i]))
        mean_equal.append(np.nanmean(equal_prob_rev[i]))
        mean_below.append(np.nanmean(below_prob_rev[i]))
        if FileNum != 1:
            std_above.append(np.nanstd(above_prob_rev[i]))
            std_equal.append(np.nanstd(equal_prob_rev[i]))
            std_below.append(np.nanstd(below_prob_rev[i]))
    mean_above = np.nan_to_num(mean_above)
    mean_equal = np.nan_to_num(mean_equal)
    mean_below = np.nan_to_num(mean_below)
    n_list = list(range(1, 1 + len(matrix_list[0])))
    errorbar_color_1 = '#c9e3f6'
    errorbar_color_2 = '#ffe7d2'
    errorbar_color_3 = '#d7f4d7'
    plt.plot(n_list, mean_above, 'C0')
    plt.plot(n_list, mean_equal, 'C1')
    plt.plot(n_list, mean_below, 'C2')
    if FileNum != 1:
        plt.errorbar(n_list, mean_above, yerr=std_above,
                     ecolor=errorbar_color_1, capsize=2)
        plt.errorbar(n_list, mean_equal, yerr=std_equal,
                     ecolor=errorbar_color_2, capsize=2)
        plt.errorbar(n_list, mean_below, yerr=std_below,
                     ecolor=errorbar_color_3, capsize=2)
    plt.legend(['Dissociate Size > ' + str(DivideSize), 'Dissociate Size = ' +
               str(DivideSize), 'Dissociate Size < ' + str(DivideSize)])
    plt.xlabel('N (copies of ' + str(SpeciesName) + ')')
    plt.ylabel('Probability')
    plt.xticks(ticks=n_list)
    plt.title('Remodeling of Complex')
    if SaveFig:
        plt.savefig('dissociate_probability_asymmetric.png', dpi=500)
    plt.show()
    return 0


def growth_prob(FileName: str, FileNum: int, InitialTime: float, FinalTime: float, SpeciesName: str, SaveFig: bool = False):
    warnings.filterwarnings('ignore')
    matrix_list = []
    file_name_head = FileName.split('.')[0]
    file_name_tail = FileName.split('.')[1]
    for i in range(1, FileNum+1):
        temp_file_name = file_name_head + '_' + str(i) + '.' + file_name_tail
        if FileNum == 1:
            temp_file_name = 'transition_matrix_time.dat'
        ti_matrix, tf_matrix = read_transition_matrix(
            temp_file_name, SpeciesName, InitialTime, FinalTime)
        matrix = tf_matrix - ti_matrix
        matrix_list.append(matrix)
    growth_list_list = []
    tot_list_list = []
    for k in range(len(matrix_list)):
        growth_list = []
        tot_list = []
        i = 0
        while i < len(matrix_list[k][0]):
            j = 0
            growth_sum = 0
            tot_sum = 0
            while j < len(matrix_list[k][i]):
                if i != j:
                    tot_sum += matrix_list[k][j][i]
                    if i < j:
                        growth_sum += matrix_list[k][j][i]
                j += 1
            growth_list.append(growth_sum)
            tot_list.append(tot_sum)
            i += 1
        growth_list_list.append(growth_list)
        tot_list_list.append(tot_list)
    growth_prob = []
    for i in range(len(growth_list_list)):
        growth_prob_temp = []
        for j in range(len(growth_list_list[i])):
            if tot_list_list[i][j] != 0:
                growth_prob_temp.append(
                    growth_list_list[i][j]/tot_list_list[i][j])
            else:
                growth_prob_temp.append(0.0)
        growth_prob.append(growth_prob_temp)
    growth_prob_rev = []
    for i in range(len(growth_prob[0])):
        temp = []
        for j in range(len(growth_prob)):
            temp.append(growth_prob[j][i])
        growth_prob_rev.append(temp)
    mean = []
    std = []
    for i in growth_prob_rev:
        mean.append(np.nanmean(i))
        std.append(np.nanstd(i))
    n_list = list(range(1, 1 + len(matrix_list[0])))
    errorbar_color = '#c9e3f6'
    plt.plot(n_list, mean, color='C0')
    if FileNum != 1:
        plt.errorbar(n_list, mean, yerr=std, ecolor=errorbar_color, capsize=2)
    plt.axhline(y=1/2, c='black', lw=1.0)
    plt.xlabel('N (copies of ' + str(SpeciesName) + ')')
    plt.ylabel('$P_{growth}$')
    plt.xticks(ticks=n_list)
    plt.yticks((0, 0.25, 0.5, 0.75, 1))
    plt.title('Growth Probability')
    if SaveFig:
        plt.savefig('growth_probability.png', dpi=500)
    plt.show()
    return 0


def read_cluster_lifetime(FileName: str, SpeciesName: str, InitialTime: float, FinalTime: float):
    ti_switch = False
    tf_switch = False
    spec_switch = False
    lifetime_switch = False
    size_list = []
    ti_lifetime = []
    tf_lifetime = []
    with open(FileName, 'r') as file:
        for line in file.readlines():
            if line[0:6] == 'time: ':
                lifetime_switch = False
                spec_switch = False
                if float(line.split(' ')[1].strip('\n')) == InitialTime:
                    ti_switch = True
                if float(line.split(' ')[1].strip('\n')) == FinalTime:
                    tf_switch = True
                if float(line.split(' ')[1].strip('\n')) != InitialTime:
                    ti_switch = False
                if float(line.split(' ')[1].strip('\n')) != FinalTime:
                    tf_switch = False
            if line == 'lifetime for each mol type: \n':
                lifetime_switch = True
            if line == str(SpeciesName) + '\n':
                spec_switch = True
            if ti_switch and lifetime_switch and spec_switch:
                if line != str(SpeciesName) + '\n' and line != 'lifetime for each mol type: \n':
                    if line[0:20] == 'size of the cluster:':
                        size_list.append(int(line.split(':')[1].strip('\n')))
                    else:
                        str_list = line.strip('\n').strip(' ').split(' ')
                        temp = np.array([])
                        for i in str_list:
                            if i != '':
                                temp = np.append(temp, float(i))
                        ti_lifetime.append(temp)
            if tf_switch and lifetime_switch and spec_switch:
                if line != str(SpeciesName) + '\n' and line != 'lifetime for each mol type: \n':
                    if line[0:20] != 'size of the cluster:':
                        str_list = line.strip('\n').strip(' ').split(' ')
                        temp = np.array([])
                        for i in str_list:
                            if i != '':
                                temp = np.append(temp, float(i))
                        tf_lifetime.append(temp)
    return ti_lifetime, tf_lifetime, size_list


def complex_lifetime(FileName: str, FileNum: int, InitialTime: float, FinalTime: float, SpeciesName: str, SaveFig: bool = False):
    warnings.filterwarnings('ignore')
    file_name_head = FileName.split('.')[0]
    file_name_tail = FileName.split('.')[1]
    mean_lifetime = []
    for i in range(1, FileNum+1):
        temp_file_name = file_name_head + '_' + str(i) + '.' + file_name_tail
        if FileNum == 1:
            temp_file_name = 'transition_matrix_time.dat'
        ti_lifetime, tf_lifetime, size_list = read_cluster_lifetime(
            temp_file_name, SpeciesName, InitialTime, FinalTime)
        mean_temp = []
        for i in range(len(tf_lifetime)):
            tf_lifetime[i] = np.delete(
                tf_lifetime[i], range(0, len(ti_lifetime[i])), axis=0)
            mean_temp.append(tf_lifetime[i].mean())
        mean_lifetime.append(mean_temp)
    mean_lifetime_rev = []
    for i in range(len(mean_lifetime[0])):
        temp = []
        for j in range(len(mean_lifetime)):
            temp.append(mean_lifetime[j][i])
        mean_lifetime_rev.append(temp)
    mean = []
    std = []
    for i in mean_lifetime_rev:
        mean.append(np.nanmean(i))
        if FileNum != 1:
            std.append(np.nanstd(i))
    errorbar_color = '#c9e3f6'
    plt.plot(size_list, mean, color='C0')
    if FileNum != 1:
        plt.errorbar(size_list, mean, yerr=std,
                     ecolor=errorbar_color, capsize=2)
    plt.xlabel('N (copies of ' + str(SpeciesName) + ')')
    plt.ylabel('Lifetime (s)')
    plt.xticks(ticks=size_list)
    plt.title('Lifetime of Complex')
    if SaveFig:
        plt.savefig('complex_lifetime.png', dpi=500)
    plt.show()
    return 0


# --------------------------------Locate Position by Pdb or Restart----------------------------------


def PDB_pdb_to_df(file_name):
    df = pd.DataFrame(columns=['Protein_Num', 'Protein_Name',
                      'Cite_Name', 'x_coord', 'y_coord', 'z_coord'])
    with open(file_name, 'r') as file:
        index = 0
        for line in file.readlines():
            line = line.split(' ')
            if line[0] == 'ATOM':
                info = []
                for i in line:
                    if i != '':
                        info.append(i)
                df.loc[index, 'Protein_Num'] = int(info[4])
                df.loc[index, 'Protein_Name'] = info[3]
                df.loc[index, 'Cite_Name'] = info[2]
                df.loc[index, 'x_coord'] = float(info[5])
                df.loc[index, 'y_coord'] = float(info[6])
                df.loc[index, 'z_coord'] = float(info[7])
            index += 1
        df = df.dropna()
        df = df.drop(index=df[(df.Cite_Name == 'COM')].index.tolist())
        df = df.reset_index(drop=True)
    return df


def PDB_dis_cal(x, y):
    return ((x[0]-y[0])**2+(x[1]-y[1])**2+(x[2]-y[2])**2)**0.5


def PDB_dis_df_gen(df, info):
    dis_df = pd.DataFrame(columns=['Protein_Num_1', 'Protein_Name_1', 'Cite_Name_1',
                          'Protein_Num_2', 'Protein_Name_2', 'Cite_Name_2', 'sigma', 'dis'])
    index = 0
    count = 1
    for i in range(len(info)):
        df_temp_1 = df[df['Protein_Name'].isin([info.iloc[i, 0]])]
        df_1 = df_temp_1[df_temp_1['Cite_Name'].isin([info.iloc[i, 1]])]
        df_temp_2 = df[df['Protein_Name'].isin([info.iloc[i, 2]])]
        df_2 = df_temp_2[df_temp_2['Cite_Name'].isin([info.iloc[i, 3]])]
        df_1 = df_1.reset_index(drop=True)
        df_2 = df_2.reset_index(drop=True)
        print('Calculating distance for reaction #', count, '...')
        count += 1
        for j in range(len(df_1)):
            for k in range(len(df_2)):
                dis_df.loc[index, 'Protein_Num_1'] = df_1.loc[j, 'Protein_Num']
                dis_df.loc[index, 'Protein_Name_1'] = df_1.loc[j,
                                                               'Protein_Name']
                dis_df.loc[index, 'Cite_Name_1'] = df_1.loc[j, 'Cite_Name']
                dis_df.loc[index, 'Protein_Num_2'] = df_2.loc[k, 'Protein_Num']
                dis_df.loc[index, 'Protein_Name_2'] = df_2.loc[k,
                                                               'Protein_Name']
                dis_df.loc[index, 'Cite_Name_2'] = df_2.loc[k, 'Cite_Name']
                dis_df.loc[index, 'sigma'] = info.loc[i, 'sigma']
                x = [df_1.loc[j, 'x_coord'], df_1.loc[j,
                                                      'y_coord'], df_1.loc[j, 'z_coord']]
                y = [df_2.loc[k, 'x_coord'], df_2.loc[k,
                                                      'y_coord'], df_2.loc[k, 'z_coord']]
                dis_df.loc[index, 'dis'] = PDB_dis_cal(x, y)
                index += 1
    return dis_df


def PDB_bind_df_gen(dis_df, buffer_ratio):
    bind_df = pd.DataFrame(columns=['Protein_Num_1', 'Protein_Name_1', 'Cite_Name_1',
                           'Protein_Num_2', 'Protein_Name_2', 'Cite_Name_2', 'sigma', 'dis'])
    index = 0
    for i in range(len(dis_df)):
        if dis_df.loc[i, 'dis'] >= dis_df.loc[i, 'sigma']*(1-buffer_ratio):
            if dis_df.loc[i, 'dis'] <= dis_df.loc[i, 'sigma']*(1+buffer_ratio):
                bind_df.loc[index] = dis_df.loc[i]
                index += 1
    return bind_df


def PDB_find_bond(bind_df):
    bond_lst = []
    for i in range(len(bind_df)):
        bond_lst.append([int(bind_df.loc[i, 'Protein_Num_1']),
                        int(bind_df.loc[i, 'Protein_Num_2'])])
    for i in bond_lst:
        i.sort()
    bond_lst_ = []
    for i in bond_lst:
        if i not in bond_lst_:
            bond_lst_.append(i)
    return bond_lst_


def PDB_find_complex(pdb_df, bond_lst):
    complex_lst = []
    for i in range(1, 1+pdb_df['Protein_Num'].max()):
        complex_temp = [i]
        j = 0
        while j < len(bond_lst):
            if bond_lst[j][0] in complex_temp and bond_lst[j][1] not in complex_temp:
                complex_temp.append(bond_lst[j][1])
                j = 0
            elif bond_lst[j][1] in complex_temp and bond_lst[j][0] not in complex_temp:
                complex_temp.append(bond_lst[j][0])
                j = 0
            else:
                j += 1
        complex_lst.append(complex_temp)
    for i in complex_lst:
        i.sort()
    complex_lst_ = []
    for i in complex_lst:
        if i not in complex_lst_:
            complex_lst_.append(i)
    return complex_lst_


def PDB_complex_df_gen(pdb_df, complex_lst):
    name_lst = list(pdb_df['Protein_Name'])
    name_lst_ = []
    for i in name_lst:
        if i not in name_lst_:
            name_lst_.append(i)
    column_lst = []
    for i in name_lst_:
        column_lst.append(i)
    column_lst.append('Protein_Num')
    complex_df = pd.DataFrame(columns=column_lst)
    index = 0
    for i in complex_lst:
        complex_df.loc[index] = 0
        complex_df.loc[index, 'Protein_Num'] = str(i)
        for j in i:
            for indexs in pdb_df.index:
                for k in range(len(pdb_df.loc[indexs].values)):
                    if(pdb_df.loc[indexs].values[k] == j):
                        col = pdb_df.loc[indexs, 'Protein_Name']
                        complex_df.loc[index, col] += 1
                        break
                else:
                    continue
                break
        index += 1
    return complex_df


def PDB_find_complex_df(complex_df, num_lst, pdb_df):
    protein_name = []
    for i in range(len(pdb_df)):
        if pdb_df.loc[i, 'Protein_Name'] not in protein_name:
            protein_name.append(pdb_df.loc[i, 'Protein_Name'])
    complex_df['Num_List'] = ''
    for i in range(complex_df.shape[0]):
        lst = []
        for j in range(complex_df.shape[1]-2):
            lst.append(complex_df.iloc[i, j])
        complex_df.loc[i, 'Num_List'] = str(lst)
    num_lst_str = str(num_lst)
    protein_remain = []
    for i in range(complex_df.shape[0]):
        if complex_df.loc[i, 'Num_List'] == num_lst_str:
            string = complex_df.loc[i, 'Protein_Num']
            string = string.strip('[').strip(']').split(',')
            for i in string:
                protein_remain.append(int(i))
    return protein_remain


def PDB_new_pdb(file_name, protein_remain):
    with open(file_name, 'r') as file:
        write_lst = []
        for line in file.readlines():
            line_ = line.split(' ')
            if line_[0] == 'TITLE':
                write_lst.append(line)
            elif line_[0] == 'CRYST1':
                write_lst.append(line)
            elif line_[0] == 'ATOM':
                info = []
                for i in line_:
                    i.strip('\n')
                    if i != '':
                        info.append(i)
                info[9] = info[9].strip('\n')
                if int(info[4]) in protein_remain:
                    write_lst.append(line)
    with open('output_file.pdb', 'w') as file_:
        file_.seek(0)
        file_.truncate()
        for i in write_lst:
            file_.writelines(i)
    return 0


def PDB_binding_info_df(inp_name):
    status = False
    index = -1
    binding_info = pd.DataFrame(
        columns=['Protein_Name_1', 'Cite_Name_1', 'Protein_Name_2', 'Cite_Name_2', 'sigma'])
    with open(inp_name, 'r') as file:
        for line in file.readlines():
            if line == 'end reactions\n':
                status = False
                break
            if line == 'start reactions\n':
                status = True
            if status:
                if '<->' in line:
                    index += 1
                    line1 = line.split('+')
                    element1 = line1[0].strip(' ')
                    line2 = line1[1].split('<->')
                    element2 = line2[0].strip(' ')
                    element1_ = element1.strip(')').split('(')
                    element2_ = element2.strip(')').split('(')
                    binding_info.loc[index,
                                     'Protein_Name_1'] = element1_[0][0:3]
                    binding_info.loc[index, 'Cite_Name_1'] = element1_[1][0:3]
                    binding_info.loc[index,
                                     'Protein_Name_2'] = element2_[0][0:3]
                    binding_info.loc[index, 'Cite_Name_2'] = element2_[1][0:3]
                if 'sigma' in line:
                    binding_info.loc[index, 'sigma'] = float(
                        line.split(' = ')[-1].strip('\n'))
    return binding_info


def locate_position_PDB(FileNamePdb, NumList, FileNameInp, BufferRatio=0.01):
    print('Reading files......')
    pdb_df = PDB_pdb_to_df(FileNamePdb)
    print('Reading files complete!')
    print('Extracting binding information......')
    binding_info = PDB_binding_info_df(FileNameInp)
    print('Extracting complete!')
    print('Calculating distance......')
    dis_df = PDB_dis_df_gen(pdb_df, binding_info)
    print('Calculation complete!')
    print('Finding bonds......')
    bind_df = PDB_bind_df_gen(dis_df, BufferRatio)
    bond_lst = PDB_find_bond(bind_df)
    print('Finding bonds complete!')
    print('Finding complexes......')
    complex_lst = PDB_find_complex(pdb_df, bond_lst)
    complex_df = PDB_complex_df_gen(pdb_df, complex_lst)
    print('Finding complexes complete!')
    print('Writing new PDB files......')
    protein_remain = PDB_find_complex_df(complex_df, NumList, pdb_df)
    PDB_new_pdb(FileNamePdb, protein_remain)
    print('PDB writing complete!(named as output_file.pdb)')
    return 0


def RESTART_read_restart(file_name_restart):
    with open(file_name_restart, 'r') as file:
        status = False
        count = 0
        complex_lst = []
        for line in file.readlines():
            if line == '#All Complexes and their components \n':
                status = True
            if status:
                if count % 8 == 7:
                    info = line.split()
                    temp_lst = []
                    for i in range(len(info)):
                        if i != 0:
                            temp_lst.append(int(info[i]))
                    complex_lst.append(temp_lst)
                count += 1
            if line == '#Observables \n':
                break
    print('The total number of complexes is', len(complex_lst))
    return complex_lst


def RESTART_pdb_to_df(file_name_pdb):
    df = pd.DataFrame(columns=['Protein_Num', 'Protein_Name'])
    with open(file_name_pdb, 'r') as file:
        index = 0
        for line in file.readlines():
            line = line.split(' ')
            if line[0] == 'ATOM':
                info = []
                for i in line:
                    if i != '':
                        info.append(i)
                df.loc[index, 'Protein_Num'] = int(info[4])
                df.loc[index, 'Protein_Name'] = info[3]
            index += 1
        df = df.dropna()
        df = df.reset_index(drop=True)
    return df


def RESTART_complex_df_gen(pdb_df, complex_lst):
    name_lst = list(pdb_df['Protein_Name'])
    name_lst_ = []
    for i in name_lst:
        if i not in name_lst_:
            name_lst_.append(i)
    column_lst = []
    for i in name_lst_:
        column_lst.append(i)
    column_lst.append('Protein_Num')
    complex_df = pd.DataFrame(columns=column_lst)
    index = 0
    for i in complex_lst:
        complex_df.loc[index] = 0
        complex_df.loc[index, 'Protein_Num'] = str(i)
        for j in i:
            for indexs in pdb_df.index:
                for k in range(len(pdb_df.loc[indexs].values)):
                    if(pdb_df.loc[indexs].values[k] == j):
                        col = pdb_df.loc[indexs, 'Protein_Name']
                        complex_df.loc[index, col] += 1
                        break
                else:
                    continue
                break
        index += 1
    return complex_df


def RESTART_find_complex_df(complex_df, num_lst, pdb_df):
    protein_name = []
    for i in range(len(pdb_df)):
        if pdb_df.loc[i, 'Protein_Name'] not in protein_name:
            protein_name.append(pdb_df.loc[i, 'Protein_Name'])
    complex_df['Num_List'] = ''
    for i in range(complex_df.shape[0]):
        lst = []
        for j in range(complex_df.shape[1]-2):
            lst.append(complex_df.iloc[i, j])
        complex_df.loc[i, 'Num_List'] = str(lst)
    num_lst_str = str(num_lst)
    protein_remain = []
    for i in range(complex_df.shape[0]):
        if complex_df.loc[i, 'Num_List'] == num_lst_str:
            string = complex_df.loc[i, 'Protein_Num']
            string = string.strip('[').strip(']').split(',')
            for i in string:
                protein_remain.append(int(i))
    return protein_remain


def RESTART_new_pdb(file_name_pdb, protein_remain):
    with open(file_name_pdb, 'r') as file:
        write_lst = []
        for line in file.readlines():
            line_ = line.split(' ')
            if line_[0] == 'TITLE':
                write_lst.append(line)
            elif line_[0] == 'CRYST1':
                write_lst.append(line)
            elif line_[0] == 'ATOM':
                info = []
                for i in line_:
                    i.strip('\n')
                    if i != '':
                        info.append(i)
                info[9] = info[9].strip('\n')
                if int(info[4]) in protein_remain:
                    write_lst.append(line)
    with open('output_file.pdb', 'w') as file_:
        file_.seek(0)
        file_.truncate()
        for i in write_lst:
            file_.writelines(i)
    return 0


def locate_position_restart(FileNamePdb, NumList, FileNameRestart='restart.dat'):
    print('Reading restart.dat......')
    complex_lst = RESTART_read_restart(FileNameRestart)
    print('Reading files complete!')
    print('Reading PDB files......')
    pdb_df = RESTART_pdb_to_df(FileNamePdb)
    print('Reading files complete!')
    print('Finding complexes......')
    complex_df = RESTART_complex_df_gen(pdb_df, complex_lst)
    print('Finding complexes complete!')
    print('Writing new PDB files......')
    protein_remain = RESTART_find_complex_df(complex_df, NumList, pdb_df)
    RESTART_new_pdb(FileNamePdb, protein_remain)
    print('PDB writing complete!(named as output_file.pdb)')
    return 0
