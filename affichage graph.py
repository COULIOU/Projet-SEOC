import serial
import time
import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def get_co2_temp_t():#définition de la fonction qui permet d'aquérir les données de CO2 et température issues du capteur
    #MHZ19. On génère aussi l'information temporelle à l'aide de cette fonction.

    start = datetime.datetime.now()
    t = 0
    while True:
        now = datetime.datetime.now()
        t = (now - start).total_seconds()#ces 4 premières lignes de codes permettent de générée l'information temporelle
        #correspondant à l'instant d'aquisition des données issues du capteur.

        ser = serial.Serial('/dev/ttyAMA0')  # on ouvre le port serie du Raspberry
        ser.write(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79')  # on envoie une requête sur le port serie pour interroger les données 8 bits du capteur
        p = ser.read(5)  # on lit les 5 premiers bits ?
        testBytes = p  # conversion hexadécimal ?

        octet3 = testBytes[3]
        octet2 = testBytes[2]
        octet4 = testBytes[4]

        temperature = (octet4 - 40)
        co2 = (octet2 * 256) + octet3
        time.sleep(2)  # on attend 2s car le détecteur a déjà besoin d'au moins 1s pour récupérer une mesure. Cette étape
        #est à affiner pour véirifier qu'elle est cohérente avec ce que fait le capteur pour calculer le taux de CO2 !

        yield t, temperature, co2  #yiel est une sorte de "return".
        #Il faut réfléchir à comment afficher l'instant d'aquisition d'une donnée sous forme date/heure/minute. Comme il s'agit
        #d'un type non gérable avec la fonction local.time (ce n'est pas du float ou du int) il faudra trouver une astuce.


def init_anim():# Cette fonction permet de créer le graphique qui va être mis à jour à l'aide de FincAnimation.

    global fig, axe_CO2, axe_temp, ln_co2, ln_temp #on définit nos variables qui vont être appelées dans notre
    # construction de graphique. fig c'est la fenêtre, axe_ les axes, ln sont des listes créées à partir de point lues sur
    #le graph (on stocke temporairement les données affichées.
    fig, axe_CO2 = plt.subplots() #fonction de traçage qui gère des tableaux à plusieurs dimension (nous, on en a 2 avec
    #la température et le CO2.
    axe_temp = axe_CO2.twinx() # Création d'un autre axe des ordonnées pour la température en regard de celui du CO2.
    ln_co2, = axe_CO2.plot(data_time,data_co2, 'ro', animated=True,  # On créé une sorte de liste de points
                           color="red", label='co2 (ppm)', marker='.')  # issus de la courbe du co2 tout en définissant
    # l'allure de la courbe d'un point de vue graphisme. La virgule derrière ln permet de stipuler que le tableau est 1D.
    ln_temp, = axe_temp.plot(data_time, data_temp, 'ro', animated=True,
                             color="green", label='température (°C)', marker='*')
    axe_CO2.set_xlabel('temps (s)') # définition de l'aspect du graph et des pleines échelles des axes
    axe_CO2.set_ylabel('ppm')
    axe_CO2.legend(loc='upper left')
    axe_temp.set_ylabel('°C')
    axe_temp.legend(loc='upper right')
    axe_CO2.set_xlim(0, 60) #Comme on souhaite mettre en place un rafraichissement du graph toute les heure par exemple
    # il va falloir travailler sur l'échelle des abscisses.
    axe_CO2.set_ylim(0, 2000)
    axe_temp.set_ylim(0, 50)


def update_anim(frames): # c'est la fonction qui va être affichée et donc rafraichit à l'écran
    t, temperature, co2 = frames  # frames c'est le nombre d'images constituant l'animation : donc il y a autant de
    # d'images constituant l'animation que des points aquis
    data_temp.append(temperature)  # on ajoute les données aquises au fur et à mesure aux listes
    data_co2.append(co2)
    data_time.append(t)
    ln_co2.set_data(data_time, data_co2)  # la méthode set_data permet de remplacer les valeurs des coordonnées
    # des points de la courbe d'indice 0 de l'objet ln (liste temporaire issue du graph) par les valeurs de x (data_time) et y (data_co2)
    ln_temp.set_data(data_time, data_temp)
    return ln_co2, ln_temp

#Finalement c'est ici que le programme se lance pour de vrai
data_co2 = [] #on créé des listes initialement vides pour les remplir avec les données aquises issues du capteur
data_time = []
data_temp = []

#On initialise l'affichage du graphique en lançant la fonction init_anim. A noter qu'il est possible en principe
# de réaliser cette opération à l'intérieur de FuncAnimation.
init_anim()

# La fonction ani= FuncAnimation permet de réaliser l'affichage en temps réel des données. Dans la position 1 dans
# la parenthèse on retrouve la fenêtre qui va s'afficher, en 2 la fonction qui va apporter les points dans le graphique,
# on aurait pu avoir en 3 init_anim, dans les frames c'est le nombre d'images successives qui va s'afficher (ici autant
# que de point aquis dans la limite de l'échelle des abscisses,
ani = FuncAnimation(fig, update_anim, frames=get_co2_temp_t, blit=True, repeat=False)
plt.show() #lance l'affichage du graphique

#EXPLICATION COMPLETE DE FuncAnimation :

#class matplotlib.animation.FuncAnimation(fig, func, frames=None, init_func=None, fargs=None, save_count=None, *,
# cache_frame_data=True, **kwargs)[source]

#figFigure
#L'objet figure utilisé pour obtenir les événements nécessaires, tels que dessiner ou redimensionner.

#funccallable
#La fonction à appeler à chaque image. Le premier argument sera la valeur suivante en frames. Tous les arguments positionnels supplémentaires peuvent être fournis via le paramètre fargs.

#La signature requise est:

#def func (frame, * fargs) -> iterable_of_artists
#Si blit == True, func doit retourner un itérable de tous les artistes qui ont été modifiés ou créés. Ces informations sont utilisées par l'algorithme de blitting pour déterminer quelles parties de la figure doivent être mises à jour. La valeur de retour est inutilisée si blit == False et peut être omise dans ce cas.

#framesiterable, int, fonction de générateur, ou None, facultatif
#Source de données pour passer func et chaque image de l'animation

#S'il s'agit d'un itérable, utilisez simplement les valeurs fournies. Si l'itérable a une longueur, il remplacera le kwarg save_count.

#Si un entier, alors équivalent à passer la plage (cadres)

#Si une fonction de générateur, alors doit avoir la signature:

#def gen_function () -> obj
#Si aucun, alors équivalent à passer itertools.count.

#Dans tous ces cas, les valeurs en frames sont simplement transmises à la fonction fournie par l'utilisateur et peuvent donc être de n'importe quel type.

#init_funccallable, facultatif
#Une fonction utilisée pour dessiner un cadre clair. Sinon, les résultats du dessin à partir du premier élément de la séquence d'images seront utilisés. Cette fonction sera appelée une fois avant la première image.

#La signature requise est:

#def init_func () -> iterable_of_artists
#Si blit == True, init_func doit retourner un itérable d'artistes à redessiner. Ces informations sont utilisées par l'algorithme de blitting pour déterminer quelles parties de la figure doivent être mises à jour. La valeur de retour est inutilisée si blit == False et peut être omise dans ce cas.

#fargstuple ou None, facultatif
#Arguments supplémentaires à transmettre à chaque appel à func.

#save_countint, par défaut: 100
#Repli pour le nombre de valeurs des trames au cache. Ceci n'est utilisé que si le nombre d'images ne peut pas être déduit des images, c'est-à-dire lorsqu'il s'agit d'un itérateur sans longueur ou d'un générateur.

#intervalint, par défaut: 200
#Délai entre les images en millisecondes.

#repeat_delayint, par défaut: 0
#Délai en millisecondes entre les exécutions d'animations consécutives, si la répétition a la valeur True.

#repeatbool, par défaut: True
#Indique si l'animation se répète lorsque la séquence d'images est terminée.

#blitbool, par défaut: False
#Si le blitting est utilisé pour optimiser le dessin. Remarque: lors de l'utilisation du blitting, tous les artistes animés seront dessinés en fonction de leur ordre z; cependant, ils seront dessinés au-dessus de tous les artistes précédents, quel que soit leur ordre.

#cache_frame_databool, par défaut: True
#Si les données de trame sont mises en cache. La désactivation du cache peut être utile lorsque les cadres contiennent des objets volumineux.
