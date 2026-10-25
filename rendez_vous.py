"""rendez_vous.py : module Rendez-vous (relie un patient à un médecin à une date et une heure)."""
from tkinter import *
from tkinter import ttk, messagebox
import database
import style

CRENEAUX = [f"{h:02d}:{m:02d}" for h in range(8, 18) for m in (0, 30)]

# Rendez-vous avec les noms (JOIN) : id, patient, médecin, date, heure, motif
REQUETE = """select r.id_rdv, p.nom || ' ' || p.prenom,
                    m.nom || ' ' || m.prenom || ' (' || coalesce(m.specialite, '') || ')',
                    r.date_rdv, r.heure_rdv, coalesce(r.motif, '')
             from rendez_vous r
             join patients p on p.id_patient = r.id_patient
             join medecins m on m.id_medecin = r.id_medecin"""
# tri chronologique (les dates sont stockées en JJ/MM/AAAA)
ORDRE = " order by substr(r.date_rdv,7,4) || substr(r.date_rdv,4,2) || substr(r.date_rdv,1,2), r.heure_rdv"


class RendezVousFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.patient, self.medecin, self.date = StringVar(), StringVar(), StringVar()
        self.heure, self.motif = StringVar(), StringVar()
        self.variables = [self.patient, self.medecin, self.date, self.heure, self.motif]
        self.patients, self.medecins = {}, {}      # "libellé affiché" -> id
        self.id_selection = None
        self.creer_widgets()
        self.rafraichir_listes()

    def creer_widgets(self):
        style.titre(self, "Gestion des rendez-vous", "Planifier les consultations entre patients et médecins")
        form = style.formulaire(self, "Informations du rendez-vous")
        self.combo_patient = style.champ(form, "Patient *", self.patient, 0, valeurs=[])
        self.combo_medecin = style.champ(form, "Médecin *", self.medecin, 1, valeurs=[])
        style.champ(form, "Motif", self.motif, 2)
        style.champ(form, "Date * (JJ/MM/AAAA)", self.date, 0, 1)
        style.champ(form, "Heure *", self.heure, 1, 1, valeurs=CRENEAUX)
        style.boutons(self, self.ajouter_rdv, self.modifier_rdv, self.supprimer_rdv, self.vider_champs)
        self.tableau = style.tableau(self, ["ID", "Patient", "Médecin", "Date", "Heure", "Motif"],
                                     [45, 170, 230, 100, 70, 200])
        self.tableau.bind("<<TreeviewSelect>>", self.selectionner_rdv)

    # ---------- listes déroulantes ----------
    def charger_patients(self):
        lignes = database.lire("select * from patients order by nom, prenom")
        self.patients = {f"{p['nom']} {p['prenom']}": p["id_patient"] for p in lignes}
        self.combo_patient["values"] = list(self.patients)

    def charger_medecins(self):
        lignes = database.lire("select * from medecins order by nom, prenom")
        self.medecins = {f"{m['nom']} {m['prenom']} ({m['specialite'] or ''})": m["id_medecin"] for m in lignes}
        self.combo_medecin["values"] = list(self.medecins)

    def rafraichir_listes(self):
        """Appelée à chaque affichage du module : on y voit les nouveaux patients et médecins."""
        self.charger_patients()
        self.charger_medecins()
        self.afficher_rdv()

    # ---------- contrôles ----------
    def valider_champs(self):
        """Renvoie (id_patient, id_medecin, date, heure, motif) ou None si le formulaire est incorrect."""
        patient, medecin, date, heure, motif = (v.get().strip() for v in self.variables)
        if patient not in self.patients or medecin not in self.medecins:
            erreur = "Choisissez un patient et un médecin dans les listes."
        elif not database.date_valide(date):
            erreur = "La date doit être au format JJ/MM/AAAA."
        elif heure not in CRENEAUX:
            erreur = "Choisissez un créneau horaire."
        else:
            return self.patients[patient], self.medecins[medecin], date, heure, motif
        messagebox.showerror("Erreur", erreur)

    def verifier_disponibilite(self, id_patient, id_medecin, date, heure, id_rdv=0):
        """Interdit deux rendez-vous au même créneau pour le même médecin OU le même patient."""
        for colonne, valeur, message in [
                ("id_medecin", id_medecin, "Ce médecin a déjà un rendez-vous à cette date et cette heure."),
                ("id_patient", id_patient, "Ce patient a déjà un rendez-vous à cette date et cette heure.")]:
            nb = database.lire(f"select count(*) from rendez_vous where {colonne}=? and date_rdv=? "
                               "and heure_rdv=? and id_rdv<>?", (valeur, date, heure, id_rdv))[0][0]
            if nb:
                messagebox.showerror("Créneau occupé", message)
                return False
        return True

    # ---------- CRUD ----------
    def afficher_rdv(self):
        style.remplir(self.tableau, database.lire(REQUETE + ORDRE))

    def selectionner_rdv(self, event=None):
        if not self.tableau.selection():
            return
        self.id_selection = int(self.tableau.selection()[0])
        ligne = database.lire(REQUETE + " where r.id_rdv=?", (self.id_selection,))[0]
        for variable, valeur in zip(self.variables, tuple(ligne)[1:]):
            variable.set(valeur)

    def ajouter_rdv(self):
        champs = self.valider_champs()
        if champs and self.verifier_disponibilite(*champs[:4]) and database.executer(
                "insert into rendez_vous(id_patient, id_medecin, date_rdv, heure_rdv, motif) "
                "values(?,?,?,?,?)", champs):
            self.afficher_rdv()
            self.vider_champs()

    def modifier_rdv(self):
        if self.id_selection is None:
            messagebox.showwarning("Attention", "Sélectionnez un rendez-vous dans le tableau.")
            return
        champs = self.valider_champs()
        if champs and self.verifier_disponibilite(*champs[:4], self.id_selection) and database.executer(
                "update rendez_vous set id_patient=?, id_medecin=?, date_rdv=?, heure_rdv=?, motif=? "
                "where id_rdv=?", champs + (self.id_selection,)):
            self.afficher_rdv()
            self.vider_champs()

    def supprimer_rdv(self):
        if self.id_selection is None:
            messagebox.showwarning("Attention", "Sélectionnez un rendez-vous dans le tableau.")
        elif messagebox.askyesno("Confirmation", "Supprimer ce rendez-vous ?"):
            database.executer("delete from rendez_vous where id_rdv=?", (self.id_selection,))
            self.afficher_rdv()
            self.vider_champs()

    def vider_champs(self):
        for variable in self.variables:
            variable.set("")
        self.id_selection = None
        self.tableau.selection_remove(*self.tableau.selection())


# Test du module seul : python rendez_vous.py
if __name__ == "__main__":
    database.creer_tables()
    fenetre = Tk()
    style.appliquer_style(fenetre)
    RendezVousFrame(fenetre).pack(fill=BOTH, expand=True)
    fenetre.mainloop()
