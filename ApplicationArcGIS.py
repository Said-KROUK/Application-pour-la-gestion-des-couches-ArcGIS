# -*- coding: utf-8 -*-

import arcpy
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

#from builtins import dict, float, int, len, print, range, str, zip

def quitter():
    root.quit()

def Erreur(liste):
    if not liste.curselection():
        messagebox.showerror("Erreur", "Aucune couche sélectionnée")

def Afficher_liste():
    liste.delete(0, tk.END)
    for couche in GetCouche():
        liste.insert('end', couche)
    liste.pack()

def afficher_couche():
    if not liste.curselection():
        Erreur(liste)
        return
    selected_index = liste.curselection()
    couche_selectionnee = liste.get(selected_index)
    attributs = [field.name for field in arcpy.ListFields(couche_selectionnee)]
    valeurs_attributs = []
    with arcpy.da.SearchCursor(couche_selectionnee, '*') as curseur:
        for row in curseur:
            valeurs_attributs.append(row)
    fenetre = tk.Tk()
    fenetre.title("La Couche " + str(couche_selectionnee).upper())
    tableau = ttk.Treeview(fenetre, columns=attributs, show="headings")
    for attribut in attributs:
        tableau.heading(attribut, text=attribut)
        tableau.column(attribut, width=100)
    for valeur_attribut in valeurs_attributs:
        tableau.insert("", tk.END, values=valeur_attribut)
    tableau.pack()
    fenetre.mainloop()

def ajouter_couche():
    def valider():
        nom_couche = champ_saisie.get()
        type_couche = liste_types.get()
        if nom_couche and type_couche:
            Ajouter_Couche(nom_couche, type_couche)
            messagebox.showinfo("Information", "Nom de la couche : {}\nType de la couche : {}".format(nom_couche, type_couche))
            Afficher_liste()
            fenetre_saisie.destroy()
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
    fenetre_saisie = tk.Tk()
    fenetre_saisie.geometry("300x150")
    fenetre_saisie.title("Ajouter une couche")
    label_nom = tk.Label(fenetre_saisie, text="Nom de la couche:")
    label_nom.pack(pady=5)
    champ_saisie = tk.Entry(fenetre_saisie)
    champ_saisie.pack(pady=5)
    label_type = tk.Label(fenetre_saisie, text="Type de la couche:")
    label_type.pack(pady=5)
    types_couche = ["POINT", "MULTIPOINT", "POLYGON", "POLYLINE", "MULTIPATCH"]
    liste_types = ttk.Combobox(fenetre_saisie, values=types_couche, state="readonly")
    liste_types.pack(pady=5)
    bouton_valider = tk.Button(fenetre_saisie, text="Valider", command=valider, bg="lightgreen")
    bouton_valider.pack(pady=10)
    fenetre_saisie.mainloop()

path = ""

def GetCouche():
    if not arcpy.Exists(path):
        print("La géodatabase spécifiée n'existe pas.")
        return []

    arcpy.env.workspace = path
    layer_list = []

    for layer in arcpy.ListFeatureClasses():
        layer_list.append(layer)

    for data in arcpy.ListDatasets():
        for layer in arcpy.ListFeatureClasses("", "", data):
            layer_list.append(layer)

    if not layer_list:
        print("Aucune couche n'a été trouvée dans le dataset.")
        return []
    else:
        return layer_list

def Ajouter_Couche(nom_couche, type_couche):
    if arcpy.Exists(path + "\\" + nom_couche):
        return 0
    else:
        arcpy.CreateFeatureclass_management(path, nom_couche, type_couche)
        return 1

def Modifier_Couche(nom_couche, nouveau_nom, nouveau_type):
    arcpy.env.workspace = path
    arcpy.env.overwriteOutput = True

    if arcpy.Exists(nom_couche):
        couche = arcpy.Describe(nom_couche)
        chemin_couche = couche.catalogPath

        arcpy.Rename_management(chemin_couche, nouveau_nom)
        arcpy.CopyFeatures_management(nouveau_nom, nouveau_type)

        print("La couche a été modifiée avec succès.")
        return (1, "La couche a été modifiée avec succès.")
    else:
        print("La couche spécifiée n'existe pas dans la géodatabase.")
        return (0, "La couche spécifiée n'existe pas dans la géodatabase.")

def Supprimer_Couche(nom_couche):
    try:
        arcpy.env.workspace = path
        arcpy.Delete_management(nom_couche)
        print("La couche {} a été supprimée avec succès.".format(nom_couche))
        return (1, "La couche {} a été supprimée avec succès.".format(nom_couche))
    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        return (0, arcpy.GetMessages())

def Ajouter_champ(nom_couche, nom_champ, type_champ):
    if arcpy.Exists(path + "\\" + nom_couche):
        arcpy.AddField_management(nom_couche, nom_champ, type_champ)
        print("Le champ a été ajouté avec succès à la couche.")
        return (1, "Le champ a été ajouté avec succès à la couche.")
    else:
        print("La couche spécifiée n'existe pas.")
        return (0, "La couche spécifiée n'existe pas.")

def Supprimer_champ(nom_couche, nom_champ):
    if arcpy.Exists(path + "\\" + nom_couche):
        arcpy.DeleteField_management(nom_couche, nom_champ)
        print("Le champ a été supprimé avec succès de la couche.")
        return (1, "Le champ a été supprimé avec succès de la couche.")
    else:
        print("La couche spécifiée n'existe pas.")
        return (0, "La couche spécifiée n'existe pas.")

def Modifier_champ(nom_couche, nom_champ, nouveau_nom, nouveau_type):
    if arcpy.Exists(path + "\\" + nom_couche):
        arcpy.AlterField_management(nom_couche, nom_champ, nouveau_nom, field_type=nouveau_type)
        print("Le champ a été modifié avec succès dans la couche.")
        return (1, "Le champ a été modifié avec succès dans la couche.")
    else:
        print("La couche spécifiée n'existe pas.")
        return (0, "La couche spécifiée n'existe pas.")

def ajouter_enregistrement_dans_couche(couche, values):
    chemin_couche = path + "\\" + couche
    if arcpy.Exists('couche_temp'):
        arcpy.Delete_management('couche_temp')
    couche = arcpy.management.MakeFeatureLayer(chemin_couche, "couche_temp").getOutput(0)
    description = arcpy.Describe(couche)
    ID = [champ for champ in description.fields ][0]
    print(ID)
    champs = [champ for champ in description.fields if champ.name not in [ID , "SHAPE", "Shape"]]

    if len(values) != len(champs):
        print("Le nombre de valeurs ne correspond pas au nombre de champs.")
        return

    valeurs_converties = []
    for i in range(len(values)):
        valeur = values[i]
        champ = champs[i]
        if champ.type == 'String':
            valeur_convertie = str(valeur)
        elif champ.type == 'Double':
            valeur_convertie = float(valeur)
        elif champ.type == 'Integer':
            valeur_convertie = int(valeur)
        elif champ.type == 'Date':
            valeur_convertie = arcpy.ParseDateTime(valeur)
        else:
            valeur_convertie = valeur
        valeurs_converties.append(valeur_convertie)

    with arcpy.da.InsertCursor(couche, [champ.name for champ in champs if not champ.required]) as curseur:
        curseur.insertRow(valeurs_converties)
    print("Enregistrement ajouté avec succès.")

def supprimer_enregistrement_dans_arcgis(nom_couche, objectid):
    chemin_couche = path + "\\" + nom_couche
    if arcpy.Exists('couche_temp'):
            arcpy.Delete_management('couche_temp')
    couche = arcpy.management.MakeFeatureLayer(chemin_couche, "couche_temp").getOutput(0)

    with arcpy.da.UpdateCursor(couche, "*") as curseur:
        for row in curseur:
            if row[0] == objectid:
                curseur.deleteRow()
                print("Supprimé avec succès.")
                return

    print("Aucun enregistrement correspondant à l'OBJECTID spécifié n'a été trouvé.")

def importer_gdb():
    global path
    path = filedialog.askdirectory(title="Sélectionner le dossier GDB")
    if path:
        messagebox.showinfo("Information", "GDB importé : {}".format(path))
    else:
        messagebox.showerror("Erreur", "Aucun chemin sélectionné")

def modifier_couche():
    if not liste.curselection():
        Erreur(liste)
        return
    selected_index = liste.curselection()
    couche_selectionnee = liste.get(selected_index)
    def valider():
        nom_couche = champ_saisie.get()
        type_couche = liste_types.get()
        if nom_couche and type_couche:
            resultat = Modifier_Couche(couche_selectionnee, nom_couche, type_couche)
            if resultat[0]:
                messagebox.showinfo("Information", resultat[1])
                Afficher_liste()
                fenetre_saisie.destroy()
            else:
                messagebox.showerror("Erreur", resultat[1])
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
    fenetre_saisie = tk.Tk()
    fenetre_saisie.geometry("300x150")
    fenetre_saisie.title("Modifier une couche")
    label_nom = tk.Label(fenetre_saisie, text="Nouveau nom de la couche:")
    label_nom.pack(pady=5)
    champ_saisie = tk.Entry(fenetre_saisie)
    champ_saisie.insert(0, couche_selectionnee)
    champ_saisie.pack(pady=5)
    label_type = tk.Label(fenetre_saisie, text="Type de la couche:")
    label_type.pack(pady=5)
    types_couche = ["POINT", "MULTIPOINT", "POLYGON", "POLYLINE", "MULTIPATCH"]
    liste_types = ttk.Combobox(fenetre_saisie, values=types_couche, state="readonly")
    liste_types.pack(pady=5)
    bouton_valider = tk.Button(fenetre_saisie, text="Valider", command=valider, bg="lightblue")
    bouton_valider.pack(pady=10)
    fenetre_saisie.mainloop()

def supprimer_couche():
    if not liste.curselection():
        Erreur(liste)
        return
    selected_index = liste.curselection()
    couche_selectionnee = liste.get(selected_index)
    resultat = Supprimer_Couche(couche_selectionnee)
    if resultat[0]:
        messagebox.showinfo("Information", resultat[1])
        Afficher_liste()
    else:
        messagebox.showerror("Erreur", resultat[1])

def ajouter_champ():
    if not liste.curselection():
        Erreur(liste)
        return
    selected_index = liste.curselection()
    couche_selectionnee = liste.get(selected_index)
    def valider():
        nom_champ = champ_saisie.get()
        type_champ = liste_types.get()
        if nom_champ and type_champ:
            resultat = Ajouter_champ(couche_selectionnee, nom_champ, type_champ)
            if resultat[0]:
                messagebox.showinfo("Information", resultat[1])
                Afficher_liste()
                fenetre_saisie.destroy()
            else:
                messagebox.showerror("Erreur", resultat[1])
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
    fenetre_saisie = tk.Tk()
    fenetre_saisie.geometry("300x150")
    fenetre_saisie.title("Ajouter un champ à la couche " + str(couche_selectionnee).upper())
    label_nom = tk.Label(fenetre_saisie, text="Nom du champ:")
    label_nom.pack(pady=5)
    champ_saisie = tk.Entry(fenetre_saisie)
    champ_saisie.pack(pady=5)
    label_type = tk.Label(fenetre_saisie, text="Type de champ:")
    label_type.pack(pady=5)
    types_champ = ["TEXT", "FLOAT", "DOUBLE", "SHORT", "LONG", "DATE", "BLOB", "RASTER", "GUID"]
    liste_types = ttk.Combobox(fenetre_saisie, values=types_champ, state="readonly")
    liste_types.pack(pady=5)
    bouton_valider = tk.Button(fenetre_saisie, text="Valider", command=valider, bg="lightyellow")
    bouton_valider.pack(pady=10)
    fenetre_saisie.mainloop()

def supprimer_champ():
    if not liste.curselection():
        Erreur(liste)
        return
    selected_index = liste.curselection()
    couche_selectionnee = liste.get(selected_index)
    def valider():
        nom_champ = champ_saisie.get()
        if nom_champ:
            resultat = Supprimer_champ(couche_selectionnee, nom_champ)
            if resultat[0]:
                messagebox.showinfo("Information", resultat[1])
                Afficher_liste()
                fenetre_saisie.destroy()
            else:
                messagebox.showerror("Erreur", resultat[1])
        else:
            messagebox.showerror("Erreur", "Veuillez entrer le nom du champ.")
    fenetre_saisie = tk.Tk()
    fenetre_saisie.geometry("300x150")
    fenetre_saisie.title("Supprimer un champ")
    label_nom = tk.Label(fenetre_saisie, text="Nom du champ:")
    label_nom.pack(pady=5)
    champ_saisie = tk.Entry(fenetre_saisie)
    champ_saisie.pack(pady=5)
    bouton_valider = tk.Button(fenetre_saisie, text="Valider", command=valider, bg="red", fg="white")
    bouton_valider.pack(pady=10)
    fenetre_saisie.mainloop()

def modifier_champ():
    if not liste.curselection():
        Erreur(liste)
        return
    selected_index = liste.curselection()
    couche_selectionnee = liste.get(selected_index)
    def valider():
        nom_champ = champ_saisie.get()
        nouveau_nom = nouveau_nom_saisie.get()
        nouveau_type = liste_types.get()
        if nom_champ and nouveau_nom and nouveau_type:
            resultat = Modifier_champ(couche_selectionnee, nom_champ, nouveau_nom, nouveau_type)
            if resultat[0]:
                messagebox.showinfo("Information", resultat[1])
                Afficher_liste()
                fenetre_saisie.destroy()
            else:
                messagebox.showerror("Erreur", resultat[1])
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
    fenetre_saisie = tk.Tk()
    fenetre_saisie.geometry("300x200")
    fenetre_saisie.title("Modifier un champ")
    label_nom = tk.Label(fenetre_saisie, text="Nom du champ:")
    label_nom.pack(pady=5)
    champ_saisie = tk.Entry(fenetre_saisie)
    champ_saisie.pack(pady=5)
    label_nouveau_nom = tk.Label(fenetre_saisie, text="Nouveau nom:")
    label_nouveau_nom.pack(pady=5)
    nouveau_nom_saisie = tk.Entry(fenetre_saisie)
    nouveau_nom_saisie.pack(pady=5)
    label_type = tk.Label(fenetre_saisie, text="Nouveau type de champ:")
    label_type.pack(pady=5)
    types_champ = ["TEXT", "FLOAT", "DOUBLE", "SHORT", "LONG", "DATE", "BLOB", "RASTER", "GUID"]
    liste_types = ttk.Combobox(fenetre_saisie, values=types_champ, state="readonly")
    liste_types.pack(pady=5)
    bouton_valider = tk.Button(fenetre_saisie, text="Valider", command=valider, bg="lightyellow")
    bouton_valider.pack(pady=10)
    fenetre_saisie.mainloop()

def ajouter_enregistrement_couche_arcgis():
    if not liste.curselection():
        Erreur(liste)
        return
    selected_index = liste.curselection()
    couche = liste.get(selected_index)
    description = arcpy.Describe(couche)
    champs = [field for field in description.fields if not field.required]
    ID = [champ for champ in description.fields ][0]
    fenetre = tk.Tk()
    fenetre.geometry("300x500")
    fenetre.title("Ajouter un nouvel enregistrement")
    entrees = []
    for champ in champs:
        tk.Label(fenetre, text=champ.name).pack()
        entree = tk.Entry(fenetre)
        entree.pack()
        entrees.append(entree)
    def ajouter():
        valeurs = [entree.get() for entree in entrees]
        ajouter_enregistrement_dans_couche(couche, valeurs)
        fenetre.destroy()
    bouton = tk.Button(fenetre, text="Ajouter", command=ajouter, bg="lightgreen")
    bouton.pack(pady=5)
    fenetre.mainloop()

def supprimer_enregistrement():
    if not liste.curselection():
        Erreur(liste)
        return
    selected_index = liste.curselection()
    couche = liste.get(selected_index)
    def valider():
        IDOBJECT = champ_saisie.get()
        if IDOBJECT:
            supprimer_enregistrement_dans_arcgis(couche, int(IDOBJECT))
            messagebox.showinfo("Information", "L'enregistrement a été supprimé avec succès")
            Afficher_liste()
            fenetre_saisie.destroy()
        else:
            messagebox.showerror("Erreur", "Veuillez entrer l'OBJECTID.")
    fenetre_saisie = tk.Tk()
    fenetre_saisie.geometry("300x200")
    fenetre_saisie.title("Supprimer un enregistrement")
    label_nom = tk.Label(fenetre_saisie, text="OBJECTID:")
    label_nom.pack(pady=5)
    champ_saisie = tk.Entry(fenetre_saisie)
    champ_saisie.pack(pady=5)
    bouton_valider = tk.Button(fenetre_saisie, text="Valider", command=valider, bg="red", fg="white")
    bouton_valider.pack(pady=10)
    fenetre_saisie.mainloop()


def modifier_enregistrement_dans_couche(couche, objectid, field_to_modify, new_value):
    chemin_couche = path + "\\" + couche
    if arcpy.Exists('couche_temp'):
        arcpy.Delete_management('couche_temp')
    couche_temp = arcpy.management.MakeFeatureLayer(chemin_couche, "couche_temp").getOutput(0)
    description = arcpy.Describe(couche_temp)
    ID  = [champ.name for champ in description.fields][0]
    with arcpy.da.UpdateCursor(couche_temp, [ID, field_to_modify]) as curseur:
        for row in curseur:
            if row[0] == int(objectid):  # Check if the OBJECTID matches
                row[1] = new_value
                curseur.updateRow(row)
                print("Enregistrement modifié avec succès.")
                return True
    return False

def modifier_enregistrement():
    if not liste.curselection():
        Erreur(liste)
        return
    selected_index = liste.curselection()
    couche = liste.get(selected_index)
    
    def valider():
        IDOBJECT = champ_saisie.get()
        field_to_modify = field_dropdown.get()
        new_value = new_value_entry.get()
        if IDOBJECT and field_to_modify and new_value:
            result = modifier_enregistrement_dans_couche(couche, IDOBJECT, field_to_modify, new_value)
            if result:
                messagebox.showinfo("Information", "L'enregistrement a été modifié avec succès")
            else:
                messagebox.showerror("Erreur", "Échec de la modification de l'enregistrement")
            Afficher_liste()
            fenetre_saisie.destroy()
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
    
    fenetre_saisie = tk.Tk()
    fenetre_saisie.geometry("300x500")
    fenetre_saisie.title("Modifier un enregistrement")
    
    label_nom = tk.Label(fenetre_saisie, text="OBJECTID:")
    label_nom.pack(pady=5)
    champ_saisie = tk.Entry(fenetre_saisie)
    champ_saisie.pack(pady=5)
    
    description = arcpy.Describe(couche)
    champs = [field.name for field in description.fields if not field.required]
    
    # Dropdown for selecting the field to modify
    label_field = tk.Label(fenetre_saisie, text="Champ à modifier:")
    label_field.pack(pady=5)
    field_dropdown = ttk.Combobox(fenetre_saisie, values=champs, state="readonly")
    field_dropdown.pack(pady=5)
    
    # Entry for the new value
    label_new_value = tk.Label(fenetre_saisie, text="Nouvelle valeur:")
    label_new_value.pack(pady=5)
    new_value_entry = tk.Entry(fenetre_saisie)
    new_value_entry.pack(pady=5)
    
    
    bouton_valider = tk.Button(fenetre_saisie, text="Valider", command=valider, bg="lightgreen")
    bouton_valider.pack(pady=10)
    
    fenetre_saisie.mainloop()
def rechercher_enregistrement_dans_couche(couche, objectid):
    chemin_couche = path + "\\" + couche
    if arcpy.Exists('couche_temp'):
        arcpy.Delete_management('couche_temp')
    couche_temp = arcpy.management.MakeFeatureLayer(chemin_couche, "couche_temp").getOutput(0)
    description = arcpy.Describe(couche_temp)
    champs = [champ.name for champ in description.fields]
    with arcpy.da.SearchCursor(couche_temp, champs) as curseur:
        for row in curseur:
            if row[0] == objectid:
                return dict(zip(champs, row))
    return None


def rechercher_enregistrement():
    if not liste.curselection():
        Erreur(liste)
        return
    selected_index = liste.curselection()
    couche = liste.get(selected_index)
    def valider():
        IDOBJECT = champ_saisie.get()
        if IDOBJECT:
            enregistrement = rechercher_enregistrement_dans_couche(couche, int(IDOBJECT))

            if enregistrement:
                resultats = "\n".join(["{}: {}".format(k, v) for k, v in enregistrement.items()])
                messagebox.showinfo("Résultat de la recherche", resultats)
            else:
                messagebox.showerror("Erreur", "Aucun enregistrement trouvé pour l'OBJECTID donné.")
            fenetre_saisie.destroy()
        else:
            messagebox.showerror("Erreur", "Veuillez entrer l'OBJECTID.")
    fenetre_saisie = tk.Tk()
    fenetre_saisie.geometry("300x100")
    fenetre_saisie.title("Rechercher un enregistrement par OBJECTID")
    label_nom = tk.Label(fenetre_saisie, text="OBJECTID:")
    label_nom.pack(pady=5)
    champ_saisie = tk.Entry(fenetre_saisie)
    champ_saisie.pack(pady=5)
    bouton_valider = tk.Button(fenetre_saisie, text="Rechercher", command=valider, bg="lightblue")
    bouton_valider.pack(pady=10)
    fenetre_saisie.mainloop()

def creer_buffer_couche(couche, distance, unite):
    try:
        output_path = path + "\\{}_Buffer".format(couche)
        arcpy.Buffer_analysis(couche, output_path, "{} {}".format(distance, unite))
        return output_path
    except arcpy.ExecuteError:
        print(arcpy.GetMessages())
        return None

def creer_buffer():
    if not liste.curselection():
        Erreur(liste)
        return
    selected_index = liste.curselection()
    couche_selectionnee = liste.get(selected_index)
    def valider():
        distance = champ_distance.get()
        unite = unite_selectionnee.get()
        if distance and unite:
            buffer_layer = creer_buffer_couche(couche_selectionnee, distance, unite)
            if buffer_layer:
                messagebox.showinfo("Information", "Buffer créé avec succès: {}".format(buffer_layer))
                Afficher_liste()
                fenetre_saisie.destroy()
            else:
                messagebox.showerror("Erreur", "Échec de la création du buffer")
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
    fenetre_saisie = tk.Tk()
    fenetre_saisie.geometry("300x200")
    fenetre_saisie.title("Créer un buffer")
    label_distance = tk.Label(fenetre_saisie, text="Distance:")
    label_distance.pack(pady=5)
    champ_distance = tk.Entry(fenetre_saisie)
    champ_distance.pack(pady=5)
    label_unite = tk.Label(fenetre_saisie, text="Unité:")
    label_unite.pack(pady=5)
    unites = ["Meters", "Kilometers", "Feet", "Miles"]
    unite_selectionnee = ttk.Combobox(fenetre_saisie, values=unites, state="readonly")
    unite_selectionnee.pack(pady=5)
    bouton_valider = tk.Button(fenetre_saisie, text="Valider", command=valider, bg="lightgreen")
    bouton_valider.pack(pady=10)
    fenetre_saisie.mainloop()
# Création de la fenêtre principale
root = tk.Tk()
root.title("ArcGIS App")
root.geometry("1300x400")
root.configure(bg="#d9d9d9")

# Première interface pour importer la base de données
frame_import = tk.Frame(root, bg="#d9d9d9")
frame_import.pack(pady=20)

bouton_importer = tk.Button(frame_import, text="Importer BD", command=importer_gdb, bg="lightblue")
bouton_importer.grid(row=0, column=2, padx=10, pady=10)
#Gestion frame
frame_gestion = tk.Frame(root, bg="#d9d9d9", relief=tk.GROOVE)
frame_gestion.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)


# Gestion des couches
frame_gestion_couches = tk.Frame(frame_gestion, bg="#d9d9d9", relief=tk.GROOVE, borderwidth=2)
frame_gestion_couches.pack(side=tk.LEFT,padx=20, pady=10, fill=tk.BOTH, expand=True)

label_gestion_couches = tk.Label(frame_gestion_couches, text="Gestion des Couches", font=("Arial", 14), bg="#d9d9d9")
label_gestion_couches.pack(pady=10)

global liste

liste = tk.Listbox(frame_gestion_couches, width=50, height=5, font=("Arial", 12))
for couche in GetCouche():
    liste.insert('end', couche)
liste.pack(pady=5)

bouton_actualiser = tk.Button(frame_gestion_couches, text="Actualiser", command=Afficher_liste, bg="lightblue")
bouton_actualiser.pack(pady=5)

frame_couches_btn = tk.Frame(frame_gestion_couches, bg="#d9d9d9")
frame_couches_btn.pack(pady=10)

afficher_button = tk.Button(frame_couches_btn, text="Afficher Couche", command=afficher_couche, bg="lightgreen")
afficher_button.grid(row=0, column=0, padx=10, pady=5)

bouton_ajouter_couche = tk.Button(frame_couches_btn, text="Ajouter Couche", command=ajouter_couche, bg="lightgreen")
bouton_ajouter_couche.grid(row=0, column=1, padx=10, pady=5)

bouton_modifier_couche = tk.Button(frame_couches_btn, text="Modifier Couche", command=modifier_couche, bg="lightyellow")
bouton_modifier_couche.grid(row=0, column=2, padx=10, pady=5)

bouton_supprimer_couche = tk.Button(frame_couches_btn, text="Supprimer Couche", command=supprimer_couche, bg="red", fg="white")
bouton_supprimer_couche.grid(row=0, column=3, padx=10, pady=5)

#Gestion frames enregistrements et autre 
frame_gestion_enregistrements_authre = tk.Frame(frame_gestion , bg="#d9d9d9", relief=tk.GROOVE)
frame_gestion_enregistrements_authre.pack(side=tk.RIGHT ,padx=20, pady=10, fill=tk.BOTH, expand=True)

# Gestion des enregistrements frame
frame_gestion_enregistrements = tk.Frame(frame_gestion_enregistrements_authre, bg="#d9d9d9", relief=tk.GROOVE, borderwidth=2)
frame_gestion_enregistrements.pack( padx=20, pady=5, fill=tk.BOTH, expand=True)

label_gestion_enregistrements = tk.Label(frame_gestion_enregistrements, text="Gestion des Enregistrements", font=("Arial", 14), bg="#d9d9d9")
label_gestion_enregistrements.pack(pady=10)

frame_enregistrements_btn = tk.Frame(frame_gestion_enregistrements, bg="#d9d9d9")
frame_enregistrements_btn.pack(pady=10)

bouton_ajouter_enregistrement = tk.Button(frame_enregistrements_btn, text="Ajouter Enregistrement", command=ajouter_enregistrement_couche_arcgis, bg="lightgreen")
bouton_ajouter_enregistrement.grid(row=0, column=0, padx=10, pady=5)

bouton_modifier_enregistrement = tk.Button(frame_enregistrements_btn, text="Modifier Enregistrement", command=modifier_enregistrement, bg="lightyellow")
bouton_modifier_enregistrement.grid(row=0, column=1, padx=10, pady=5)

bouton_rechercher_enregistrement = tk.Button(frame_enregistrements_btn, text="Rechercher par ID", command=rechercher_enregistrement, bg="lightblue")
bouton_rechercher_enregistrement.grid(row=0, column=3, padx=10, pady=5)

bouton_supprimer_enregistrement = tk.Button(frame_enregistrements_btn, text="Supprimer Enregistrement", command=supprimer_enregistrement, bg="red", fg="white")
bouton_supprimer_enregistrement.grid(row=0, column=2, padx=10, pady=5)

# Gestion des autres fonctionnalités

frame_gestion_autres = tk.Frame(frame_gestion_enregistrements_authre, bg="#d9d9d9", relief=tk.GROOVE, borderwidth=2)
frame_gestion_autres.pack(padx=5, pady=1, fill=tk.BOTH, expand=True)

label_gestion_autres = tk.Label(frame_gestion_autres, text="Gestion Autres Fonctionnalités", font=("Arial", 14), bg="#d9d9d9")
label_gestion_autres.pack(pady=5)

frame_autres_btn = tk.Frame(frame_gestion_autres, bg="#d9d9d9")
frame_autres_btn.pack(pady=10)

bouton_ajouter_champ = tk.Button(frame_autres_btn, text="Ajouter Champ", command=ajouter_champ, bg="lightgreen")
bouton_ajouter_champ.grid(row=0, column=0, padx=10, pady=5)

bouton_supprimer_champ = tk.Button(frame_autres_btn, text="Supprimer Champ", command=supprimer_champ, bg="red", fg="white")
bouton_supprimer_champ.grid(row=0, column=1, padx=10, pady=5)

bouton_modifier_champ = tk.Button(frame_autres_btn, text="Modifier Champ", command=modifier_champ, bg="lightyellow")
bouton_modifier_champ.grid(row=0, column=2, padx=10, pady=5)

bouton_creer_buffer = tk.Button(frame_autres_btn, text="Créer Buffer", command=creer_buffer, bg="lightblue")
bouton_creer_buffer.grid(row=0, column=3, padx=10, pady=5)

bouton_quitter = tk.Button(root, text="Quitter", command=quitter, bg="gray", fg="white", font=("Arial", 12))
bouton_quitter.pack(pady=20)

# Exécution de la boucle principale
root.mainloop()
