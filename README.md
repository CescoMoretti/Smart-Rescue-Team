# Smart-Rescue-Team
Progetto per l'esame di IOT and 3D intelligent systems

Schema della comunicazione --> Tramite MQTT --> paho-mqtt

![alt text](https://github.com/CescoMoretti/Smart-Rescue-Team/blob/master/Schema%20di%20Base.png?raw=true)



Dettagli/Idee/Proposte/Dubbi Smart device:

Cane:
* Machine learnig a bordo: lo ha detto il prof che è meglio e che lo vedremo a lezione più avanti --> riconoscimento facciale --> yolo
  * riconoscimento facciale
    * parte quando il cane sta fermo
    * si ferma se non ci sono figure umane
* Invia i dati dei suoi sensori
  * tenere uno storico in caso di problemi di connessione 
* Immagini filtrate a partire dal video con ML
* (Altoparlante / microfono)
* Lora


Broker - squadra di soccorso:
* Come mettere insieme tutti i dati?
* Gestire comunicazione in caso di segnale disturbato
* Eventuale secondo device per far vedere la mappa alla squadra?
* Secondo filtro di machine learning per le eventuali immagini inviate dai cani?
* Internet (4g?) --> su HTTP 
* Visualizza mappa tramite web app --> usare un secondo oggetto IoT? (tipo tablet)



Cloud:
* Riceve mappa e sistema di riferimento
* Disegna le coordinate convertendole in zone di pixel
* Provare con Np a cambiare rgb della zona interessata
* HTTP

