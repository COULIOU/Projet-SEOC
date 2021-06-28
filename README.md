# Projet-Atmosph-Air
Information pour brancher et piloter le MH-Z19 avec la carte LoPy4

Branchement du capteur.

Broche capteur    -    Broche LoPy4

Vin               -    Vin 
GND               -    GND
Rx                -    P3, Tx de la LoPy
Tx                -    P4, Rx de le LoPy
HD                -    P8
PWM               -    P9
Vo                -    P13

------------------------------

Programme.

------------------------------


Version : 1.0

Cette version ne prends pas en compte les fonction PWM et Vo du capteur.

Description:

Le programme initialise la communication Uart.
Récupération des données en Hex.
Convertion des données brut en données compréhensible.
Affichage des données.

