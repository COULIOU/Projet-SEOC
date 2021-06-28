# Projet Atmosph'air
# Programme pour pilotage du capteur de CO2
# MH-Z19

# 24 février 2021

# importation des modules
import pycom
import machine
import time
from network import *
import sys
import socket



# configuration de la carte
pycom.heartbeat(False)

# ------------------------------
# Initialisation des pattes
# MH-Z19
HD = Pin('P8', mode = Pin.OUT)
PWM_CO2 = Pin('P9', mode = Pin.IN)
# Création d'une entrée ADC pour V0
adc = machine.ADC()             # create an ADC object
adc.init(bits=12)
#adc.vref(3.3)
VO = adc.channel(pin='P13')   # create an analog pin on P10


# ------------------------------
# Initialisation des protocole de communication
# UART

Tx = 'P3' # de la carte à relier à Rx du capteur
Rx = 'P4' # de la carte à relier à Tx du capteur
# Utilisation de l'UART 1, vitesse 9600nombre de bits par caractére, parité, bit d'arrêt, affectation de Tx et Rx
uart=UART(1,baudrate = 9600, bits = 8, parity = None, stop = 1, pins = (Tx,Rx))

# Réseau Wifi
mode_w = WLAN.STA
ssid_w = 'xxx'
auth_w = (WLAN.WEP, 'xxx')
antenna_w = WLAN.INT_ANT

# Création de l'objet wifi
wlan = WLAN(mode=mode_w, ssid=ssid_w, auth=auth_w, antenna=antenna_w)

# Config réseau du pycom
IP_w = '192.168.0.107'
Subnet_w = '255.255.255.0'
Gateway_w = '192.168.0.1'
DNS_w = '192.168.0.1'
# (IP, Subnet, Gateway, DNS)
wlan.ifconfig(config=(IP_w, Subnet_w, Gateway_w, DNS_w))



# Information serveur
HOST = '192.168.1.64' # Adresse du serveur
PORT = 50000 # Port

# ------------------------------
# Variable globales

version = '1.0' # Version du programme

ID_MHZ19 = 'CO2_001' # Identifiant du capteur de CO2

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
    #print("Temperature:",octet4-40)
    e = (octet2*256)+octet3
    #print ("Taux de CO2 =",e,"ppm")
    return octet4-40, (octet2*256)+octet3

# Lecture de la valeur de CO2 par VOUT
def VO_ppm():
    val = VO()                    # read an analog value
    return val #int((val*2000)/3.3)

# Vérification données CO2
# A compèter
def verif(temp, CO2_ppm):
    a , b = True, True
    if (temp < -20 and temp > 50):
        a = False

    if (CO2_ppm < 400 and CO2_ppm > 5000):
        b = False

    return a, b

# ------------------------------
# Sous-ensemble de programme serveur
# ------------------------------

# Fonction connexion au réseau
def connexion_reseau():
    # 1) connexion au réseau
    print("Connexion au réseau :", ssid_w)
    while not wlan.isconnected():
        time.sleep_ms(50)
    print("Connxion effectuée")
    t = wlan.scan()
    print(t)


# Fonction de connexion au serveur
def connexion_serveur():
    # 2) envoi d'une requ�te de connexion au serveur_test :
    print("Accès au serveur...")
    connect = False
    while (connect == False):
        try:
            mySocket.connect((HOST, PORT))
            connect = True
        except socket.error:
            print("La connexion a échoué.")

        print("Connexion établie avec le serveur.")
        time.sleep(2)
        print("45")

    # 3) Dialogue avec le serveur_test :
    msgServeur = mySocket.recv(1024).decode("Utf8")

# fonction d'envoie de la donn�e
def message(ID, CO2, Temp):
    print("Envoie des données...")
    msgServeur = mySocket.recv(1024).decode("Utf8")
    if (msgServeur == "OK"):
        mySocket.send(ID.encode("Utf8"))
        mySocket.send(CO2.encode("Utf8"))
        mySocket.send(Temp.encode("Utf8"))

# Fonction de fermeture de la connexion
def deconnexion_serveur():
    print("Déconnexion du serveur et réseau...")
    # 4) Fermeture de la connexion :
    wlan.disconnect()

# ------------------------------
# Programme
# ------------------------------
#time.sleep (10) # Temps d'initialisation des capteurs

# Pour ne pas initialiser le MH-Z19 au démarrage
HD.value(1)

#init_mhz19 (0):
a=0

while True: # pour tourner en permanence
    print(a)
    val = CO2_MHZ19() # lance
    if (type(val) == bytes):
        temp, CO2_ppm = conv_hex(val)
        print("La température est de",temp,"°C")
        print("La concentartion de CO2 est de",CO2_ppm,"ppm")
        #connexion_reseau()

    time.sleep (1)

    # Partie du programme qui se connecte et envoie les données au serveur


    """
    connexion_serveur()

    message(ID_MHZ19, CO2_ppm, temp)
    deconnexion_serveur()
    time.sleep (1)
    """


    a = a + 1
