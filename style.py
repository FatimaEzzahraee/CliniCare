"""style.py : couleurs et éléments d'interface communs aux 3 modules (même apparence partout)."""
from tkinter import *
from tkinter import ttk

# couleurs : fond des pages, bleu principal, bleu fonce (bouton actif du menu)
FOND, BLEU, BLEU_FONCE = "#f4f8fb", "#1a6b8a", "#14536b"
# blanc (tableau), gris (texte secondaire et bouton Vider), couleur du texte
BLANC, GRIS, TEXTE = "#ffffff", "#5f7482", "#14364a"
# vert (bouton Ajouter), rouge (bouton Supprimer)
VERT, ROUGE, LIGNE_IMPAIRE = "#2e8b57", "#c0392b", "#eaf2f7"
# police utilisee partout
POLICE = "Segoe UI"

# regle les styles des widgets ttk une seule fois pour toute l'application
def appliquer_style(fenetre):
    """À appeler une fois, avant de créer les modules."""
    # couleur de fond de la fenetre principale
    fenetre.configure(background=FOND)
    # s = objet qui gere les styles ttk
    s = ttk.Style(fenetre)
    s.theme_use("clam")  
     # "." = reglage par defaut de tous les widgets ttk (fond, couleur du texte, police)                   # ce thème accepte les couleurs
    s.configure(".", background=FOND, foreground=TEXTE, font=(POLICE, 10))
     # titre des cadres de formulaire (ex : "Informations du medecin") en bleu et gras
    s.configure("TLabelframe.Label", foreground=BLEU, font=(POLICE, 10, "bold"))
    # tableau : hauteur des lignes et fond blanc
    s.configure("Treeview", rowheight=24, background=BLANC, fieldbackground=BLANC)
    # en-tetes des colonnes : fond bleu, texte blanc
    s.configure("Treeview.Heading", background=BLEU, foreground="white", font=(POLICE, 10, "bold"))
    # map = couleur selon l'etat : une ligne selectionnee devient bleue avec texte blanc
    s.map("Treeview", background=[("selected", BLEU)], foreground=[("selected", "white")])
    # liste deroulante en lecture seule : fond blanc au lieu de gris
    s.map("TCombobox", fieldbackground=[("readonly", BLANC)])
    # cree 4 styles de bouton : Ajouter.TButton, Modifier.TButton, Supprimer.TButton, Neutre.TButton
    for nom, couleur in [("Ajouter", VERT), ("Modifier", BLEU), ("Supprimer", ROUGE), ("Neutre", GRIS)]:
        # couleur du bouton, texte blanc, marge interieure, pas de bordure
        s.configure(nom + ".TButton", background=couleur, foreground="white", padding=6, borderwidth=0)
        # quand la souris est dessus (active), la couleur ne change pas
        s.map(nom + ".TButton", background=[("active", couleur)])


#bandeau du haut de chaque page : un titre et une petite phrase en dessous
def titre(parent, texte, sous_titre):
    """Bandeau bleu en haut de chaque module."""
    # fill=X : le bandeau prend toute la largeur
    bandeau = Frame(parent, bg=BLEU)
    bandeau.pack(fill=X)
    # anchor="w" colle le texte a gauche ; padx/pady = marges
    Label(bandeau, text=texte, bg=BLEU, fg="white", font=(POLICE, 18, "bold")).pack(anchor="w", padx=20, pady=(12, 0))
    Label(bandeau, text=sous_titre, bg=BLEU, fg="#cfe0f1", font=(POLICE, 10)).pack(anchor="w", padx=20, pady=(0, 12))


# cadre avec un titre qui contiendra les champs du formulaire
def formulaire(parent, titre):
    cadre = ttk.LabelFrame(parent, text=titre, padding=12)
    cadre.pack(fill=X, padx=15, pady=(12, 6))
    # on renvoie le cadre pour que les modules y placent leurs champs
    return cadre


# ajoute une ligne du formulaire : un texte (label) et le champ a cote
def champ(cadre, texte, variable, ligne, colonne=0, valeurs=None):
    """Label + zone de saisie (liste déroulante si 'valeurs' est donné). Formulaire sur 2 colonnes."""
    ttk.Label(cadre, text=texte).grid(row=ligne, column=2 * colonne, sticky="w", padx=(10, 6), pady=4)
    #champ de texte normal ; textvariable relie le champ a la StringVar du module
    if valeurs is None:
        widget = ttk.Entry(cadre, textvariable=variable, width=30)
    # le champ est dans la colonne juste a droite du label
    else:
        widget = ttk.Combobox(cadre, textvariable=variable, values=valeurs, state="readonly", width=28)
    # le champ est dans la colonne juste a droite du label
    widget.grid(row=ligne, column=2 * colonne + 1, sticky="w", padx=(0, 20), pady=4)
    return widget

# rangee des 4 boutons ; chaque module donne les fonctions a appeler au clic
def boutons(parent, ajouter, modifier, supprimer, vider):
    cadre = ttk.Frame(parent)
    cadre.pack(pady=8)
    # chaque element = (texte du bouton, nom du style de couleur, fonction a appeler)
    for texte, nom, commande in [("Ajouter", "Ajouter", ajouter), ("Modifier", "Modifier", modifier),
                                 ("Supprimer", "Supprimer", supprimer), ("Vider", "Neutre", vider)]:
        # nom + ".TButton" = le style cree dans appliquer_style ; side=LEFT : les boutons sont cote a cote
        ttk.Button(cadre, text=texte, style=nom + ".TButton", command=commande).pack(side=LEFT, padx=6)


def tableau(parent, colonnes, largeurs):
    """Tableau (Treeview) avec barre de défilement."""
    # expand=True : le tableau prend toute la place restante de la page
    cadre = ttk.Frame(parent)
    cadre.pack(fill=BOTH, expand=True, padx=15, pady=(6, 12))
    # show="headings" : affiche seulement les colonnes avec leurs titres
    t = ttk.Treeview(cadre, columns=colonnes, show="headings", height=8)
    for colonne, largeur in zip(colonnes, largeurs):
        t.heading(colonne, text=colonne)
        t.column(colonne, width=largeur)
    barre = ttk.Scrollbar(cadre, orient="vertical", command=t.yview)
    t.configure(yscrollcommand=barre.set)
    barre.pack(side=RIGHT, fill=Y)
    t.pack(side=LEFT, fill=BOTH, expand=True)
    # etiquette "impair" : couleur des lignes a rayer (utilisee dans remplir)
    t.tag_configure("impair", background=LIGNE_IMPAIRE)
    return t


# remplit un tableau avec les lignes lues dans la base
def remplir(tableau, lignes):
    """Vide le tableau puis le remplit ; la 1re colonne (l'id) identifie chaque ligne."""
    tableau.delete(*tableau.get_children())
    # i = numero de la ligne (0, 1, 2...), ligne = une ligne de la base
    for i, ligne in enumerate(lignes):
        # remplace les valeurs vides (None) par "" pour ne pas afficher "None"
        valeurs = tuple("" if v is None else v for v in ligne)
        # iid = l'id de la ligne ; une ligne sur deux (i impair) recoit la couleur "impair"
        tableau.insert("", END, iid=valeurs[0], values=valeurs, tags=("impair",) if i % 2 else ())
