"""
Projet Atmosph'air
Programme pour pilotage du capteur de CO2
MH-Z19 depuis la carte LoPy4
Permet d'enregistrer les données temp et CO2
dans un fichier texte pour obtenir des donnée pour le
projet Innovation et SOC
"""
# 19 avril 2021

# importation des modules
import pycom
import machine
from machine import SD
import time
from network import *
import sys
import os
import socket
#import datetime

# configuration de la carte

# ------------------------------
# Initialisation des pattes
# MH-Z19
#HD = Pin('P8', mode = Pin.OUT)
#PWM_CO2 = Pin('P9', mode = Pin.IN)

# Création d'une entrée ADC pour lecture de la batterie
adc = machine.ADC()             # create an ADC object
adc.init(bits=12)             # Sur 12 bits
apin = adc.channel(pin='P16')   # create an analog pin on P16

# ------------------------------
# Initialisation des protocole de communication
# UART

Tx = 'P3' # de la carte à relier à Rx du capteur
Rx = 'P4' # de la carte à relier à Tx du capteur
# Utilisation de l'UART 1, vitesse 9600nombre de bits par caractére, parité, bit d'arrêt, affectation de Tx et Rx
uart=UART(1,baudrate = 9600, bits = 8, parity = None, stop = 1, pins = (Tx,Rx))

# Réseau LoRa
lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)

# ------------------------------
# Variable globales

version = '1.0' # Version du programme
ID_MHZ19 = 'CO2_001' # Identifiant du capteur de CO2
att_init = 1 # Attente pour initialistion du programme
attente = 1 # Temps entre mesures

# ------------------------------
# Sous-fonction

# Initialisation du MH-Z19
# A réaliser 1 fois régulièrement
def init_mhz19(calib):
    if (calib == 0):
        print("Initialisation du MH-Z19")
        HD.value(0)
        time.sleep(8)
        HD.value(1)
        print("Initialisation terminé")
        time.sleep(1)

# Calibration du capteur
def calib(x):
    if (x == 1):
        print("début de calibration")
        i = uart.write(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79')
        print("Fin de calibration")
    else:
        print("Pas de calibration")

# Mesure du taux de CO2 avec le MH-Z19
def CO2_MHZ19():
    i = uart.write(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79')
    # i doit être égale à 9
    CO2 = uart.read(i)
    # Starting byte \ Command \ HL concentration \ LL concentration \ - \ - \ - \ - \ - \ Check value
    # 0Xff\0x86\0x01\0xbd\0x00\0x00\0x00\0x7f
    # Gas concentration= high level *256+low level
    # Résultat 445 = 1*256+189 car bd = 189
    return CO2

# Conversion hexa MH-Z19 CO2 en ppm
def conv_hex(hex):
    octet2=hex[2]
    octet3=hex[3]
    octet4=hex[4]
    e = (octet2*256)+octet3
    return octet4-40, (octet2*256)+octet3

# Fonction de relecture de tension de batterie
def vbat():
    bat = apin() # read an analog value
    return bat

# Fonction affichage décompte
def repos(x):
    for i in range (x,0,-1):
        print("Il reste",i,"secondes avant la prochaine mesure")
        time.sleep (1) # Attente entre deux mesures

# ------------------------------
# Sous-ensemble de programme LoRa
# ------------------------------

def envoie(id,niv1,niv2,niv3):
    # Identifiant du capteur, divers niveaux envoyés
    print(id,niv1,niv2,niv3)
    print("Envoie des donnée sur réseau LoRa !!")
    mot = str(id)+";"+str(niv1)+";"+str(niv2)+";"+str(niv3)
    print(type(mot),mot)
    s.send(mot)

# ------------------------------
# Programme
# ------------------------------
calib(0)
print("Repos",att_init,"secondes")
time.sleep (att_init) # Temps d'initialisation des capteurs

# Pour ne pas initialiser le MH-Z19 au démarrage
#HD.value(1)

a=0 # Numéro de l'acquisition
while True: # pour tourner en permanence
    print("index:",a)
    bat = vbat()
    print ("Niveau de batterie :",bat)
    val = CO2_MHZ19() # lance
    if (type(val) == bytes):
        temp, CO2_ppm = conv_hex(val)
        print("La température est de",temp,"°C")
        print("La concentartion de CO2 est de",CO2_ppm,"ppm")
        envoie(ID_MHZ19,bat,CO2_ppm,temp)
        print("Attente",attente,"secondes pour prochaine mesure")
    else:
        print("Mesure erronée")
    a = a + 1
    repos(attente) # Fontion d'attente