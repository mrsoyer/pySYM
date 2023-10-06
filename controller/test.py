import os


def run(request,SYM):
    #global SYM
    #SYM = symClient("","","")
    # Récupérer toutes les variables d'environnement
    print(SYM.env("HUBSPOT_API_KEY"))
    SYM.app('n8n').test()
    return{"request" : request}