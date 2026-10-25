"""patients.py : module Patients (ajouter, afficher, modifier, supprimer, rechercher)."""
from tkinter import *
from tkinter import ttk, messagebox
import database
import style


class PatientsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.nom, self.prenom, self.naissance, self.sexe = StringVar(), StringVar(), StringVar(), StringVar()
        self.cin, self.telephone, self.adresse = StringVar(), StringVar(), StringVar()
        # même ordre que les colonnes de la table patients
        self.variables = [self.nom, self.prenom, self.naissance, self.sexe, self.cin, self.telephone, self.adresse]
        self.recherche = StringVar()
        self.id_selection = None
        self.creer_widgets()
        self.afficher_patients()

    def creer_widgets(self):
        style.titre(self, "Gestion des patients", "Enregistrer et suivre les patients de la clinique")
        form = style.formulaire(self, "Informations du patient")
        style.champ(form, "Nom *", self.nom, 0)
        style.champ(form, "Prénom *", self.prenom, 1)
        style.champ(form, "Naissance (JJ/MM/AAAA)", self.naissance, 2)
        style.champ(form, "Sexe", self.sexe, 3, valeurs=["M", "F"])
        style.champ(form, "CIN *", self.cin, 0, 1)
        style.champ(form, "Téléphone", self.telephone, 1, 1)
        style.champ(form, "Adresse", self.adresse, 2, 1)
        style.boutons(self, self.ajouter_patient, self.modifier_patient, self.supprimer_patient, self.vider_champs)

        zone = ttk.LabelFrame(self, text="Recherche", padding=8)
        zone.pack(fill=X, padx=15, pady=6)
        ttk.Label(zone, text="Nom ou CIN :").pack(side=LEFT, padx=(5, 6))
        entree = ttk.Entry(zone, textvariable=self.recherche, width=30)
        entree.pack(side=LEFT, padx=5)
        entree.bind("<Return>", lambda event: self.rechercher_patient())
        ttk.Button(zone, text="Chercher", style="Modifier.TButton", command=self.rechercher_patient).pack(side=LEFT, padx=5)
        ttk.Button(zone, text="Tout afficher", style="Neutre.TButton", command=self.afficher_patients).pack(side=LEFT, padx=5)

        self.tableau = style.tableau(self, ["ID", "Nom", "Prénom", "Naissance", "Sexe", "CIN", "Téléphone", "Adresse"],
                                     [45, 120, 120, 100, 55, 100, 110, 200])
        self.tableau.bind("<<TreeviewSelect>>", self.selectionner_patient)

    def valeurs(self):
        valeurs = [v.get().strip() for v in self.variables]
        valeurs[4] = valeurs[4].upper()     # CIN en majuscules
        return tuple(valeurs)

    def valider_champs(self):
        nom, prenom, naissance, _, cin, tel, _ = self.valeurs()
        if not (nom and prenom and cin):
            erreur = "Nom, prénom et CIN sont obligatoires."
        elif naissance and not database.date_valide(naissance):
            erreur = "La date de naissance doit être au format JJ/MM/AAAA."
        elif tel and not (tel.isdigit() and len(tel) == 10):
            erreur = "Le téléphone doit contenir 10 chiffres."
        else:
            return True
        messagebox.showerror("Erreur", erreur)
        return False

    def afficher_patients(self):
        style.remplir(self.tableau, database.lire("select * from patients order by nom"))

    def rechercher_patient(self):
        mot = "%" + self.recherche.get().strip() + "%"
        style.remplir(self.tableau, database.lire(
            "select * from patients where nom like ? or cin like ? order by nom", (mot, mot)))

    def selectionner_patient(self, event=None):
        if not self.tableau.selection():
            return
        self.id_selection = int(self.tableau.selection()[0])
        ligne = database.lire("select * from patients where id_patient=?", (self.id_selection,))[0]
        for variable, valeur in zip(self.variables, tuple(ligne)[1:]):
            variable.set(valeur or "")

    def ajouter_patient(self):
        if not self.valider_champs():
            return
        if database.executer("insert into patients(nom, prenom, date_naissance, sexe, cin, telephone, adresse) "
                             "values(?,?,?,?,?,?,?)", self.valeurs()):
            self.afficher_patients()
            self.vider_champs()
        else:
            messagebox.showerror("Erreur", "Ce CIN existe déjà.")

    def modifier_patient(self):
        if self.id_selection is None:
            messagebox.showwarning("Attention", "Sélectionnez un patient dans le tableau.")
        elif self.valider_champs():
            if database.executer("update patients set nom=?, prenom=?, date_naissance=?, sexe=?, cin=?, "
                                 "telephone=?, adresse=? where id_patient=?", self.valeurs() + (self.id_selection,)):
                self.afficher_patients()
                self.vider_champs()
            else:
                messagebox.showerror("Erreur", "Ce CIN existe déjà.")

    def supprimer_patient(self):
        if self.id_selection is None:
            messagebox.showwarning("Attention", "Sélectionnez un patient dans le tableau.")
        elif messagebox.askyesno("Confirmation", "Supprimer ce patient ?"):
            if database.executer("delete from patients where id_patient=?", (self.id_selection,)):
                self.afficher_patients()
                self.vider_champs()
            else:
                messagebox.showerror("Erreur", "Ce patient a des rendez-vous : supprimez-les d'abord.")

    def vider_champs(self):
        for variable in self.variables:
            variable.set("")
        self.id_selection = None
        self.tableau.selection_remove(*self.tableau.selection())


# Test du module seul : python patients.py
if __name__ == "__main__":
    database.creer_tables()
    fenetre = Tk()
    style.appliquer_style(fenetre)
    PatientsFrame(fenetre).pack(fill=BOTH, expand=True)
    fenetre.mainloop()
