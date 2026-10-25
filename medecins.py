"""medecins.py : module Médecins (ajouter, afficher, modifier, supprimer)."""
from tkinter import *
from tkinter import ttk, messagebox #ttk contient widgets modernes (Combobox ,Treeview etc)
import database
import style

SPECIALITES = ["Généraliste", "Cardiologue", "Pédiatre", "Dermatologue",
               "Gynécologue", "Ophtalmologue", "Dentiste", "Autre"]


#MedecinsFrame est un cadre (Frame) qui contient toute la page Medecins
# "parent" = le conteneur dans lequel la page sera placee (donne par main.py)
class MedecinsFrame(ttk.Frame):
    def __init__(self, parent):
        # initialise la partie Frame de la classe, placee dans parent
        super().__init__(parent)
        self.nom, self.prenom, self.specialite = StringVar(), StringVar(), StringVar()
        self.telephone, self.email = StringVar(), StringVar()
        # même ordre que les colonnes de la table medecins
        self.variables = [self.nom, self.prenom, self.specialite, self.telephone, self.email]
        self.id_selection = None
        self.creer_widgets()
        self.afficher_medecins()

    def creer_widgets(self):
        # bandeau bleu du haut
        style.titre(self, "Gestion des médecins", "Enregistrer et suivre les médecins de la clinique")
        # cadre du formulaire ; champ(texte, variable, ligne, colonne) place un label + un champ
        form = style.formulaire(self, "Informations du médecin")
        style.champ(form, "Nom *", self.nom, 0)
        style.champ(form, "Prénom *", self.prenom, 1)
        style.champ(form, "Spécialité *", self.specialite, 2, valeurs=SPECIALITES)
        style.champ(form, "Téléphone", self.telephone, 0, 1)
        style.champ(form, "Email", self.email, 1, 1)
        # les 4 boutons ; on donne les methodes a appeler au clic
        style.boutons(self, self.ajouter_medecin, self.modifier_medecin, self.supprimer_medecin, self.vider_champs)
         # tableau : titres des colonnes puis leurs largeurs
        self.tableau = style.tableau(self, ["ID", "Nom", "Prénom", "Spécialité", "Téléphone", "Email"],
                                     [45, 150, 150, 150, 120, 220])
         # quand on clique sur une ligne, on appelle selectionner_medecin
        self.tableau.bind("<<TreeviewSelect>>", self.selectionner_medecin)

    def valeurs(self):
         # lit les 5 champs, enleve les espaces autour (strip) et renvoie un tuple pour les "?" du SQL
        return tuple(v.get().strip() for v in self.variables)

    def valider_champs(self):
        nom, prenom, specialite, tel, email = self.valeurs()
        if not (nom and prenom and specialite):
            erreur = "Nom, prénom et spécialité sont obligatoires."
        elif tel and not (tel.isdigit() and len(tel) == 10):
            erreur = "Le téléphone doit contenir 10 chiffres."
        elif email and "@" not in email:
            erreur = "Email invalide."
        else:
            return True
        messagebox.showerror("Erreur", erreur)
        return False

    def afficher_medecins(self):
        # relit tous les medecins dans la base et remplace le contenu du tableau
        style.remplir(self.tableau, database.lire("select * from medecins order by nom"))

    def selectionner_medecin(self, event=None):
          # si aucune ligne n'est selectionnee, on ne fait rien
        if not self.tableau.selection():
            return
        # l'identifiant de la ligne cliquee est l'id du medecin
        self.id_selection = int(self.tableau.selection()[0])
         # on relit le medecin dans la base (evite que le tableau enleve le 0 du telephone)
        ligne = database.lire("select * from medecins where id_medecin=?", (self.id_selection,))[0]
        # on remplit le formulaire ; [1:] saute l'id qui n'a pas de champ
        for variable, valeur in zip(self.variables, tuple(ligne)[1:]):
            variable.set(valeur or "")


    def ajouter_medecin(self):
        if not self.valider_champs():
            return
        # executer renvoie True si l'insertion a reussi
        if database.executer("insert into medecins(nom, prenom, specialite, telephone, email) "
                             "values(?,?,?,?,?)", self.valeurs()):
             # on recharge le tableau et on vide le formulaire
            self.afficher_medecins()
            self.vider_champs()
         # False = la base a refuse (regle unique : medecin deja present)
        else:
            messagebox.showerror("Erreur", "Ce médecin existe déjà (même nom, prénom et téléphone).")


    def modifier_medecin(self):
        # il faut d'abord avoir clique sur un medecin
        if self.id_selection is None:
            messagebox.showwarning("Attention", "Sélectionnez un médecin dans le tableau.")
        # puis le formulaire doit etre correct
        elif self.valider_champs():
            if database.executer("update medecins set nom=?, prenom=?, specialite=?, telephone=?, email=? "
                                 "where id_medecin=?", self.valeurs() + (self.id_selection,)):
                self.afficher_medecins()
                self.vider_champs()
                # refuse : la modification creerait un doublon
            else:
                messagebox.showerror("Erreur", "Ce médecin existe déjà (même nom, prénom et téléphone).")


    def supprimer_medecin(self):
        # il faut d'abord avoir clique sur un medecin
        if self.id_selection is None:
            messagebox.showwarning("Attention", "Sélectionnez un médecin dans le tableau.")
            # demande confirmation (Oui = True)
        elif messagebox.askyesno("Confirmation", "Supprimer ce médecin ?"):
            if database.executer("delete from medecins where id_medecin=?", (self.id_selection,)):
                self.afficher_medecins()
                self.vider_champs()
             # refuse : la cle etrangere de rendez_vous protege le medecin qui a des rendez-vous
            else:
                messagebox.showerror("Erreur", "Ce médecin a des rendez-vous : supprimez-les d'abord.")

    def vider_champs(self):
        # remet tous les champs a vide
        for variable in self.variables:
            variable.set("")
        # plus aucun medecin selectionne
        self.id_selection = None
        self.tableau.selection_remove(*self.tableau.selection())


# Test du module seul : python medecins.py
if __name__ == "__main__":
    database.creer_tables()
    fenetre = Tk()
    style.appliquer_style(fenetre)
    MedecinsFrame(fenetre).pack(fill=BOTH, expand=True)
    fenetre.mainloop()
