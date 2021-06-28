#!/usr/bin/python
# coding=utf-8
#--------------------------------------------------------------------------------------------------------------------------------------------
#                                                  IMPORTATION DES BIBLIOTHEQUES
#--------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------
import serial
import time
import RPi.GPIO as GPIO
from gpiozero import LED
GPIO.setmode(GPIO.BCM)
import datetime
import drivers
from time import sleep
display = drivers.Lcd()



#--------------------------------------------------------------------------------------------------------------------------------------------
#                                                  VARIABLES
#--------------------------------------------------------------------------------------------------------------------------------------------

# Déclaration de la broche de sortie raccordée au buzzer
GPIO_PIN = 16
GPIO.setup(GPIO_PIN, GPIO.OUT)

# Initialisation du module PWM - la fréquence de 1000 Hz est prise comme valeur de départ
Frequence = 1000 #In Hertz
pwm = GPIO.PWM(GPIO_PIN, Frequence)


#Variables LED
LEDverte = LED(23)
LEDRouge = LED(24)
LEDBleue = LED(25)

#relais la pause entre 2 commutation est paramétrée
delayTime = 12   # en secondes
delayTime1 = 1

# La broche de raccordement du relais est déclarée. En outre la résistance de Pull-up est activée.
RELAIS_PIN = 18
GPIO.setup(RELAIS_PIN, GPIO.OUT)
GPIO.output(RELAIS_PIN, False)




#--------------------------------------------------------------------------------------------------------------------------------------------
#                                                  FONCTIONS
#--------------------------------------------------------------------------------------------------------------------------------------------

    #Fonction " génération date et heure "
def temps():
    date = datetime.datetime.now()
    date = str(date)
    return date

    # Fonction d'enregistrement sur un fichier
def log(Taux,T,instant):
    f = open("/var/www/html/test.txt",'a')
    f.write("\n")
    f.write(Taux + "/"+ T + "/" + instant)
    f.close()

    # Fonction de relecture de CO2
def co2():
    l=[]
    l.append(e)
    donnee = str(l[0])
    print ("1",donnee)
    return donnee

    # Fonction de relecture la temperature
def temperature():
    l=[]
    l.append(Temperature)
    donnee1 = str(l[0])
    print ("2",donnee1)
    return donnee1



#-------------------------------------------------------------------------------------------------------------------------------------------
#                                                       PROGRAMME PRINCIPAL
#-------------------------------------------------------------------------------------------------------------------------------------------
display.lcd_clear()
display.lcd_display_string(("BOX ATMOSPHAIR"), 1)
display.lcd_display_string(("   BIENVENUE"), 2)
sleep(10)
display.lcd_clear()

while True:
    ser=serial.Serial('/dev/ttyAMA0')
    ser.write(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79')
    p=ser.read(5)
    testBytes= p
    octet3=testBytes[3]
    octet2=testBytes[2]
    octet4=testBytes[4]
    Temperature = octet4-40
    print("Temperature:",Temperature)
    e=(octet2*256)+octet3
    print ("Taux de CO2 =",e,"ppm")
    Taux = co2()
    instant=temps()
    T=temperature()
    print("1 : ",instant,  "2 :",Taux,"3 : ",T)
    log(instant,Taux,T)
    display.lcd_display_string(("CO2: "+(Taux)+" Ppm"), 1)
    display.lcd_display_string(("Temp: "+(T)+" degres C"), 2)
    time.sleep(5)

   #Asservissemnt de niveaux du CO2
    #print("CO2: ", e)
    if e <= 500:
        LEDverte.on()
        LEDRouge.off()
        LEDBleue.off()
        print ("LED verte ON")
        pwm.stop()
        GPIO.output(RELAIS_PIN, False) # NO est ouvert

    #Pb avec l'intégration d'un seuil intermédiaire
    if e > 500 and e < 700:
        LEDverte.off()
        LEDRouge.off()
        LEDBleue.on()
        print ("LED Bleue ON")
        pwm.stop()

    else:
        if e >= 700:
            LEDRouge.on()
            LEDverte.off()
            LEDBleue.off()
            print ("LED Rouge ON")
            pwm.start(10)
            GPIO.output(RELAIS_PIN, True) # NO est fermé
            time.sleep(delayTime)
            GPIO.output(RELAIS_PIN, False) # NC est passant
            time.sleep(delayTime1)

        #LEDverte.off()
    sleep(1)
    ser.close()
display.lcd_clear()

#except KeyboardInterrupt:
        #print("Cleaning up!")
        #display.lcd_clear()