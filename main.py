"""main.py : fenêtre principale de la clinique, relie Patients, Médecins et Rendez-vous."""
from tkinter import *
from tkinter.messagebox import askyesno
import database
import style
from patients import PatientsFrame
from medecins import MedecinsFrame
from rendez_vous import RendezVousFrame

# Application est la fenetre principale (Tk) : elle contient le menu en haut et les pages en dessous
class Application(Tk):
    def __init__(self):
        # initialise la fenetre Tk
        super().__init__()
        self.title("Clinique - Gestion des patients, médecins et rendez-vous")
        self.geometry("1000x720")
        self.minsize(900, 620)
        # cree les 3 tables si elles n'existent pas encore
        database.creer_tables()
        style.appliquer_style(self)          # avant de créer les modules
        # construit le menu, puis les pages, puis affiche l'accueil au demarrage
        self.creer_menu_navigation()
        self.creer_frames()
        self.afficher_frame("Accueil")

    # menu de navigation
    def creer_menu_navigation(self):
        # barre bleue en haut, sur toute la largeur
        barre = Frame(self, bg=style.BLEU)
        barre.pack(fill=X)
        # dictionnaire nom -> bouton, pour pouvoir changer la couleur du bouton actif
        self.boutons = {}
        for nom in ["Accueil", "Patients", "Médecins", "Rendez-vous"]:
            # "lambda n=nom" garde le bon nom pour chaque bouton (sinon tous afficheraient le dernier)
            self.boutons[nom] = self.bouton_menu(barre, nom, lambda n=nom: self.afficher_frame(n), LEFT)
        # le bouton Quitter est place a droite
        self.bouton_menu(barre, "Quitter", self.quitter, RIGHT)


    def bouton_menu(self, parent, texte, commande, cote):
        # fabrique un bouton plat bleu avec texte blanc ; activebackground = couleur quand on clique
        bouton = Button(parent, text=texte, command=commande, bg=style.BLEU, fg="white",
                        activebackground=style.BLEU_FONCE, activeforeground="white", relief="flat",
                        bd=0, padx=20, pady=12, cursor="hand2", font=(style.POLICE, 11, "bold"))
         # cote = LEFT ou RIGHT
        bouton.pack(side=cote)
        return bouton


    def creer_frames(self):
        # les 4 pages sont placées dans la même case ; tkraise() amène la page choisie devant
        # conteneur = zone sous le menu qui contient toutes les pages
        conteneur = Frame(self, bg=style.FOND)
        conteneur.pack(fill=BOTH, expand=True)
        # weight=1 : la case (ligne 0, colonne 0) prend toute la place disponible
        conteneur.grid_rowconfigure(0, weight=1)
        conteneur.grid_columnconfigure(0, weight=1)
        # on cree une seule fois chaque page, avec le conteneur comme parent
        patients, medecins, rdv = PatientsFrame(conteneur), MedecinsFrame(conteneur), RendezVousFrame(conteneur)
        # dictionnaire nom du menu -> page
        self.frames = {"Accueil": self.creer_accueil(conteneur), "Patients": patients,
                       "Médecins": medecins, "Rendez-vous": rdv}
        # ce qu'on recharge à chaque affichage (les rendez-vous voient les nouveaux patients/médecins)
        # nom du menu -> methode a appeler pour recharger la page quand on l'ouvre
        self.rafraichir = {"Accueil": self.maj_accueil, "Patients": patients.afficher_patients,
                           "Médecins": medecins.afficher_medecins, "Rendez-vous": rdv.rafraichir_listes}
        # toutes les pages dans la meme case ; sticky="nsew" les etire dans les 4 directions
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")


    def creer_accueil(self, conteneur):
         # page d'accueil : un cadre avec un bloc de texte centre
        accueil = Frame(conteneur, bg=style.FOND)
        centre = Frame(accueil, bg=style.FOND)
        # place le bloc au milieu (relx=0.5 : milieu horizontal, rely=0.4 : un peu au-dessus du milieu)
        centre.place(relx=0.5, rely=0.4, anchor="center")
        # gros titre, puis message de bienvenue
        Label(centre, text="Clinique", font=(style.POLICE, 36, "bold"), fg=style.BLEU, bg=style.FOND).pack()
        Label(centre, text="Bienvenue ! Utilisez le menu en haut pour gérer les patients,\n"
                           "les médecins et les rendez-vous.", font=(style.POLICE, 13),
              fg=style.GRIS, bg=style.FOND).pack(pady=15)
        # texte des statistiques, rempli plus tard par maj_accueil()
        self.lbl_stats = Label(centre, font=(style.POLICE, 14, "bold"), fg=style.TEXTE, bg=style.FOND)
        self.lbl_stats.pack(pady=10)
        return accueil


    def maj_accueil(self):
         # compte les lignes de chaque table : [nb patients, nb medecins, nb rendez-vous]
        nb = [database.lire(f"select count(*) from {t}")[0][0] for t in ("patients", "medecins", "rendez_vous")]
        # affiche les 3 nombres dans le label de l'accueil
        self.lbl_stats.config(text=f"{nb[0]} patients   •   {nb[1]} médecins   •   {nb[2]} rendez-vous")

    def afficher_frame(self, nom):
        #recharge les donnees de la page, 2) l'amene devant les autres
        self.rafraichir[nom]()
        self.frames[nom].tkraise()
        # le bouton de la page active devient plus fonce, les autres restent bleus
        for n, bouton in self.boutons.items():
            bouton.config(bg=style.BLEU_FONCE if n == nom else style.BLEU)

    def quitter(self):
        # demande confirmation, puis ferme la fenetre si la reponse est Oui
        if askyesno("Quitter", "Voulez-vous quitter l'application ?"):
            self.destroy()


if __name__ == "__main__":
    Application().mainloop()
