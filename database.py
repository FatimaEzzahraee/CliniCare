"""database.py : connexion SQLite, création des 3 tables et petites fonctions communes."""
import sqlite3
from datetime import datetime


def get_connection():
    db = sqlite3.connect("clinique.db")
    db.row_factory = sqlite3.Row            # row["nom"] au lieu de row[1]
    db.execute("PRAGMA foreign_keys = ON")  # active les clés étrangères
    return db


def creer_tables():
    db = get_connection()
    db.executescript("""
        create table if not exists patients(
            id_patient     integer primary key autoincrement,
            nom            text not null,
            prenom         text not null,
            date_naissance text,
            sexe           text,
            cin            text unique,
            telephone      text,
            adresse        text
        );
        create table if not exists medecins(
            id_medecin integer primary key autoincrement,
            nom        text not null,
            prenom     text not null,
            specialite text,
            telephone  text,
            email      text,
            unique(nom collate nocase, prenom collate nocase, telephone)
        );
        create table if not exists rendez_vous(
            id_rdv     integer primary key autoincrement,
            id_patient integer not null references patients(id_patient),
            id_medecin integer not null references medecins(id_medecin),
            date_rdv   text not null,
            heure_rdv  text not null,
            motif      text,
            unique(id_medecin, date_rdv, heure_rdv),
            unique(id_patient, date_rdv, heure_rdv)
        );
    """)
    db.commit()
    db.close()


def executer(sql, params=()):
    """INSERT / UPDATE / DELETE. Renvoie False si la base refuse (doublon, clé étrangère)."""
    db = get_connection()
    try:
         # sql = requete avec des ? ; params = les valeurs qui remplacent les ?
        db.execute(sql, params)
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        db.close()


def lire(sql, params=()):
    """SELECT : renvoie la liste des lignes."""
    db = get_connection()
    try:
         # fetchall recupere toutes les lignes trouvees
        return db.execute(sql, params).fetchall()
    finally:
        db.close()


# verifie qu'un texte est une vraie date au format JJ/MM/AAAA
def date_valide(texte):
    try:
        datetime.strptime(texte, "%d/%m/%Y")
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    creer_tables()
    print("Base créée avec succès")
