import requests
import time
import os
from graphviz import Graph
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import *
from tkinter import scrolledtext

# Strutture
class Albero:  # classe albero che conterrà i vari nodi del mio albero
    def __init__(self, Contenuto):
        self.Contenuto = Contenuto
        self.figlio = []

    def __str__(self):
        return str(self.Contenuto)


# Funzioni
def make_soup(url):  # restituisce la pagina html da analizzare
    page = requests.get(url)  # invio la pagina da controllare
    # return BeautifulSoup(page.content, 'html.parser')  # restituisce l'html della pagina selezionata
    # restituisce l'html della pagina selezionata
    return BeautifulSoup(page.content, "html.parser", from_encoding="iso-8859-1")


def update_window():
    new_window = Toplevel(window)
    new_window.geometry("450x200")
    new_window.title("Conferma")
    new_window.resizable(0, 0)
    new_window.configure(background="white")
    new_window.grid_columnconfigure(0, weight=1)

    new_label = Label(new_window,
          text="L'aggiornamento richiederà una decina di minuti, \nsei sicuro di voler procedere?", bg="white")

    new_label.pack()
    new_label.grid(row=0, columnspan=2, sticky="N", padx=20, pady=20)

    button_true = tk.Button(new_window, text="Aggiorna", command=lambda: [update(), new_window.destroy()])  # update dei miei file
    button_true.grid(row=8, column=0, sticky="NW", pady=20, padx=30)

    button_false = tk.Button(new_window, text="Annulla", command=new_window.destroy)  # update dei miei file
    button_false.grid(row=8, column=1, sticky="NE", pady=20, padx=30)


# aggiorno la scansione
def update():
    # primi nodi dell'albero
    def primi_nodi(padre):
        # inserisco nell'albero da stampare il primo nodo
        sp = normaliz(padre.Contenuto.get_text())
        hp = str(hash(normaliz(padre.Contenuto['href'])))
        dot.node(hp, sp, href=padre.Contenuto['href'], shape="box")
        # inserisce i primi figli dell'albero del portale
        aux = 0  # contatore li

        for i in range(1, len(children)):
            child = Albero(children[i].find('a'))  # figlio da aggiungere
            list_href.append(child.Contenuto['href'])

            # aggiorno l'albero
            sf = normaliz(child.Contenuto.get_text())
            hf = str(hash(normaliz(child.Contenuto['href'])))
            dot.node(hf, sf, href=child.Contenuto['href'], shape="box")
            dot.edge(hp, hf, splines="ortho")  # link tr nodo padre e nuovo nodo

            # controllo se questo figlio ha a sua volta altri figli
            ul_side_f = soup.find('ul', {'class': 'navmenu'})  # seleziona la barra menu laterale
            li_side_f = ul_side_f.findChildren('li')  # seleziona tutti i figli della navbar
            ul_side_s = li_side_f[i + aux].find('ul')  # seleziona la sottobarra dei figli diretti
            if ul_side_s is not None:
                li_side_s = ul_side_s.findChildren('a')  # seleziona tutti i figli della sottonavbar
                aux += len(li_side_s)

                j = 0
                for j in range(len(li_side_s)):
                    nep = Albero(li_side_s[j])  # nipote
                    list_href.append(nep.Contenuto['href'])
                    child.figlio.append(nep)  # inserisco il nipote della radice come figlio del figlio diretto

                    # aggiorno l'albero
                    sn = normaliz(nep.Contenuto.get_text())
                    hn = str(hash(normaliz(nep.Contenuto['href'])))
                    dot.node(hn, sn, href=nep.Contenuto['href'], shape="box")
                    dot.edge(hf, hn, splines="ortho")  # link tr nodo padre e nuovo nodo

            tree.figlio.append(child)  # inserisco questo figlio

        # dot.render("prova", format='svg')
        #     print(os.system('prova.svg'))
        return padre

    def insert_list_group(padre):
        aux = 0  # contatore li
        a_ref = padre.Contenuto['href']
        new_soup = make_soup(a_ref)
        vert_internal_menu = new_soup.find(class_='list-group')  # menu' laterale

        hp = str(hash(normaliz(padre.Contenuto['href'])))

        if vert_internal_menu is not None:  # verifico se è presente il menu'
            child_li = vert_internal_menu.findAll(class_='list-group-item')  # tutti gli li di questa sidebar

            # controllo gli li principali (già presenti nell'albero) e verifico se possiedono figli
            for i in range(len(child_li)):  # -> organizzazione...
                direct_child = child_li[i]  # figlio i della sidebar. Devo verificare se possiede figli
                if padre.Contenuto['href'] == direct_child.find('a')[
                    'href']:  # verifico se sto analizzando il nodo corrett
                    direct_child_child = direct_child.findChildren('li')  # lista dei sottofigli
                    j = 0

                    if len(direct_child_child) != 0:
                        # scorro i figli della lista laterale -> organi accademici...
                        for j in range(
                                len(direct_child.find('ul', recursive=False).findChildren('li', recursive=False))):
                            albe_da_inserire = Albero(direct_child_child[j + aux].find('a'))
                            list_href.append(albe_da_inserire.Contenuto['href'])

                            # aggiorno l'albero
                            sf = normaliz(albe_da_inserire.Contenuto.get_text())
                            hf = str(hash(normaliz(albe_da_inserire.Contenuto['href'])))
                            dot.node(hf, sf, href=albe_da_inserire.Contenuto['href'], shape="box")
                            dot.edge(hp, hf, splines="ortho")  # link tr nodo padre e nuovo nodo

                            # caso in cui non ci siano figli da inserire (quindi cerco nel body)
                            if direct_child_child[j + aux].find('ul') is None:
                                body_link(albe_da_inserire)

                            padre.figlio.append(albe_da_inserire)  # inserisco il sotto nodo

                            # verifico se ci sono ulteriori figli e se sto analizzando il nodo corretto
                            if direct_child_child[j + aux].find('ul') is not None:
                                h = 0
                                for h in range(len(direct_child_child[j + aux].findChildren('li'))):  # -> rettore..
                                    albe_da_inserire_deep = Albero(direct_child_child[j + aux + 1].find('a'))
                                    list_href.append(albe_da_inserire_deep.Contenuto['href'])

                                    # aggiorno l'albero
                                    sn = normaliz(albe_da_inserire_deep.Contenuto.get_text())
                                    hn = str(hash(normaliz(albe_da_inserire_deep.Contenuto['href'])))
                                    dot.node(hn, sn, href=albe_da_inserire_deep.Contenuto['href'], shape="box")
                                    dot.edge(hf, hn, splines="ortho")  # link tr nodo padre e nuovo nodo

                                    body_link(albe_da_inserire_deep)  # controllo body
                                    padre.figlio[j].figlio.append(albe_da_inserire_deep)
                                    aux += 1
        return padre

    # creazione albero
    def insert_child(padre):
        i = 0
        if len(padre.figlio) != 0:
            for i in range(len(padre.figlio)):
                padre.figlio[i] = insert_child(
                    padre.figlio[i])  # percorro ricorsivamente tutto l'albero sino a trovare tutti i nodi finali
        else:
            padre = insert_list_group(padre)
        return padre

    # test link interni
    def body_link(alb):
        soup = make_soup(alb.Contenuto['href'])

        hp = str(hash(normaliz(alb.Contenuto['href'])))

        # controlli errori della pagina
        check_page(soup, alb)

        internal_link = soup.findChildren('ul', {'class': 'article-links-list'})
        for i in range(len(internal_link)):
            link_check = internal_link[i].findAll("li")
            if len(link_check) > 1:  # più di un link
                for j in range(len(link_check)):
                    aux = True
                    link_check_href = Albero(link_check[j].find('a'))
                    for old_h in list_href:  # controllo se è già stato aggiunto questo nodo
                        if link_check_href.Contenuto['href'] == old_h:
                            aux = False
                    if aux:
                        list_href.append(link_check_href.Contenuto['href'])

                        # aggiorno l'albero
                        sf = normaliz(link_check_href.Contenuto.get_text())
                        hf = str(hash(normaliz(link_check_href.Contenuto['href'])))
                        dot.node(hf, sf, href=link_check_href.Contenuto['href'], shape="box")
                        dot.edge(hp, hf, splines="ortho")  # link tr nodo padre e nuovo nodo

                        # controllo se sono presenti altri link dentro questo link (solo se appartiene a Unica)
                        if trova(link_check_href.Contenuto['href'], "unica.it"):
                            try:
                                body_link(link_check_href)

                            except requests.exceptions.ConnectionError:
                                file_connect = open("list_connection_errors.txt", "a", encoding='utf-8')
                                s_href = alb.Contenuto['href'] + " -> " + link_check_href.Contenuto.get_text() + "\n"
                                file_connect.write(s_href)
                                file_connect.close()

                                # segno nell'albero l'errore
                                dot.node(str(hash(normaliz(alb.Contenuto['href']))), style="filled",
                                         fillcolor="firebrick1")

                        # aggiungo il nodo figlio all'albero
                        alb.figlio.append(link_check_href)

            else:
                if len(link_check) == 1:  # un solo link
                    aux = True
                    link_check_href = Albero(link_check[0].find('a'))
                    for old_h in list_href:  # controllo se è già stato aggiunto quetso nodo
                        if link_check_href.Contenuto['href'] == old_h:
                            aux = False
                    if aux:
                        list_href.append(link_check_href.Contenuto['href'])

                        # aggiorno l'albero
                        sf = normaliz(link_check_href.Contenuto.get_text())
                        hf = str(hash(normaliz(link_check_href.Contenuto['href'])))
                        dot.node(hf, sf, href=link_check_href.Contenuto['href'], shape="box")
                        dot.edge(hp, hf, splines="ortho")  # link tr nodo padre e nuovo nodo

                        # controllo se sono presenti altri link dentro questo link (solo se appartiene a Unica)
                        if trova(link_check_href.Contenuto['href'], "unica.it"):
                            try:
                                body_link(link_check_href)

                            except requests.exceptions.ConnectionError:
                                file_connect = open("list_connection_errors.txt", "a", encoding='utf-8')
                                s_href = alb.Contenuto['href'] + " -> " + link_check_href.Contenuto.get_text() + "\n"
                                file_connect.write(s_href)
                                file_connect.close()

                                # segno nell'albero l'errore
                                dot.node(str(hash(normaliz(alb.Contenuto['href']))), style="filled",
                                         fillcolor="firebrick1")

                        # aggiungo il nodo figlio all'albero
                        alb.figlio.append(link_check_href)

    def check_page(soup, alb):
        # verifico se la pagina è vuota
        check_empty_page(soup, alb)

        # verifico se la pagina ha link ricorsivi
        check_recurs_page(soup, alb)

        # veriico se sto visualizzando il vecchio template
        check_old_template(soup, alb)

    # veriico se sto visualizzando il vecchio template
    def check_old_template(soup_check, alb):
        check = soup_check.find('body', {'class': 'page-template-default'})

        if check is not None:
            dot.node(str(hash(normaliz(alb.Contenuto['href']))), style="filled", fillcolor="beige")
            old_temp = open('list_old_template.txt', 'a', encoding='utf-8')
            s_href = alb.Contenuto['href'] + "\n"
            old_temp.write(s_href)
            old_temp.close()

    # verifica se la pagina è priva di contenuto
    def check_empty_page(soup_check, alb):
        cla = None
        aux = True  # presuppongo che la pagina sia corretta

        with open("list_empty_page.txt", "r", encoding='utf-8') as fp:
            lines = fp.readlines()

        # controlli per ricerca link o div
        sec = soup_check.find('section', {'class': 'contenuto'})
        if sec is not None:
            cla = sec.find('div', {'class': 'col-lg-9'})

        # controllo se presente l'article con il seguente testo e poi se presente almeno un link o div
        if (soup_check.find('article') is not None and soup_check.find(
                'article').get_text() == "\n\r\nNessun contenuto trovato\t\t\t\n") \
                or (cla is not None and cla.find('a') is None and cla.find('div') is None):
            aux = False

        if not aux:  # se è false insomma
            re = False  # controllo se questa riga è già stata segnata
            for i in range(len(lines)):
                if lines[i] == alb.Contenuto['href'] + "\n":
                    re = True
            if not re:
                file_empty = open('list_empty_page.txt', 'a', encoding='utf-8')
                s_href = alb.Contenuto['href'] + "\n"
                file_empty.write(s_href)
                file_empty.close()

                # segno nell'albero l'errore
                dot.node(str(hash(normaliz(alb.Contenuto['href']))), style="filled", fillcolor="darkorange")

    # non funziona perfettamente. Alvune pagine mantengono stesso contenuto ma cambiano link
    def check_recurs_page(soup_check, alb):
        aux = True  # presuppongo che la pagina sia corretta

        internal_link = soup_check.findChildren('ul', {'class': 'article-links-list'})
        for i in range(len(internal_link)):
            link_check = internal_link[i].findAll("li")
            if len(link_check) > 1:  # più di un link
                for j in range(len(link_check)):
                    if link_check[j].find('a')['href'] == alb.Contenuto['href']:
                        aux = False

            else:  # un solo link
                if len(link_check) == 1 and link_check[0].find('a')['href'] == alb.Contenuto['href']:
                    aux = False

        if not aux:  # se è false insomma
            file_rec = open('list_recurs_page.txt', 'a', encoding='utf-8')
            s_href = alb.Contenuto['href'] + "\n"
            file_rec.write(s_href)
            file_rec.close()

            # segno nell'albero l'errore
            dot.node(str(hash(normaliz(alb.Contenuto['href']))), style="filled", fillcolor="gold1")

    # creazione albero SVG
    dot = Graph(
        comment='file per la visualizzazione dell\'albero')  # da esportare in svg così da poter creare una web page
    dot.attr(nodesep="0.8", ranksep="1.2")

    # elmino i vecchi backup
    delete_backups()

    # inizio il timer
    start = time.time()

    # crea l'albero e aggiorna la lista dei percorsi
    soup = make_soup('https://www.unica.it/unica/it/homepage.page')

    # ricerca del menu laterale contenente i primi figli dell'albero del portale
    ul = soup.find('ul', {'class': 'navmenu'})
    children = ul.findChildren("li", recursive=False)  # seleziona solo i figli diretti
    tree = Albero(children[0].find('a'))  # albero finale, inizalmente contiene solo la radice

    # inserisco i primi figli presenti nella barra laterale sinistra
    tree = primi_nodi(tree)

    # per ogni nodo finale controllo se al suo interno son presenti ulteriori link
    tree = insert_child(tree)  # costruzione albero

    # salvo l'albero come file
    # Lo 0 serve per indicare l'inizio dei tab da inserire prima della stringa da stampare
    stamp_updated_tree(tree, 0)  # ripopola il file

    # fermo il timer
    end = time.time()

    final_timer = float("{:.2f}".format(end - start))
    minuti = 0
    sec = 0
    dec = 0

    if float(final_timer) > 60:
        minuti = int(int(final_timer) / 60)
    if float(final_timer) > 60:
        sec = (int(final_timer) - (minuti * 60))

    dec = "{:.2f}".format(float(final_timer) - minuti * 60 - sec)
    print("Sono state analizzate " + str(len(list_href)) + " pagine in: "
          + str(minuti) + " min e " + str(sec) + " sec ")  # + str(int(float(dec) * 100)) + " centesimi")

    # salva il file SVG
    dot.render("prova", format='svg')


# stampa del percorso
def stamp_updated_tree(t, tab):  # t = tree, s = stringa
    if t is not None:
        file_tree = open('last_updated_tree.txt', 'a', encoding='utf-8')
        s = "\t" * tab + normaliz(t.Contenuto.get_text() + "\n")
        file_tree.write(s)
        file_tree.close()
        if t.figlio is not None and len(t.figlio) != 0:  # Se esiste almeno un figlio a questo nodo
            tab += 1  # avanzo di un tab
            for i in range(0, len(t.figlio)):
                stamp_updated_tree(t.figlio[i], tab)
            tab -= 1  # si ritorna alla tabulazione precedente
    else:
        print("Nessun albero trovato")


# Modifica la stringa al fine di stamparla correttamente
def normaliz(s):  # elimina caratteri indesiderati
    x = 0
    while s[x+1] == " " or s[x+1] == "\t" or s[x+1] == "\n":
        if s[x + 1] == "\n":
            x += 5
        x += 1
    return s[x:len(s)]


# cerca un parola dentro una stringa base
def trova(base, ricerca):
    res = 0
    j = 0

    for i in range(len(base)):
        if base[i] == ricerca[j]:
            res += 1  # match!
            j += 1
            if res == len(ricerca):  # controllo se ho raggiunto il risultato richiesto
                break
        else:
            res = 0
            j = 0

    if res == len(ricerca):  # controllo se ho raggiunto il risultato richiesto
        return True
    else:
        return False


def delete_backups():
    # elimino il vecchio albero
    file_tree = open("last_updated_tree.txt", "w")
    file_tree.truncate()  # elimina il contenuto
    file_tree.close()

    # elimino i vecchi backup degli errori
    file_empty = open("list_empty_page.txt", "w")
    file_empty.truncate()  # elimina il contenuto
    file_empty.close()

    file_recurs = open("list_recurs_page.txt", "w")
    file_recurs.truncate()  # elimina il contenuto
    file_recurs.close()

    file_connect = open("list_connection_errors.txt", "w")
    file_connect.truncate()  # elimina il contenuto
    file_connect.close()

    file_connect = open("list_old_template.txt", "w")
    file_connect.truncate()  # elimina il contenuto
    file_connect.close()


def stampa_alb():
    # stampa tutto l'albero.
    file1 = open("last_updated_tree.txt", "r", encoding='utf-8')

    textwidget = tk.scrolledtext.ScrolledText(window,
                                              wrap=tk.WORD,
                                              width=40,
                                              height=28)
    textwidget.insert(tk.END, file1.read())
    textwidget.grid(row=10, column=0, sticky="WE", pady=10, padx=10)

    file1.close()


def ricerca_error():  # ricerca errori

    # pagine vuote
    file2 = open("list_empty_page.txt", "r", encoding='utf-8')
    stringa_errori = "Lista delle pagine non aventi contenuto:" + file2.read()
    file2.close()

    # pagine ricorsive
    file3 = open("list_recurs_page.txt", "r", encoding='utf-8')
    stringa_errori = stringa_errori + "\nLista delle pagine con link che richiamano alla stessa pagina:" + file3.read()
    file3.close()

    # errori di connessioni
    file4 = open("list_connection_errors.txt", "r", encoding='utf-8')
    stringa_errori = stringa_errori + "\nLista delle pagine che hanno creato errori di connessione:" + file4.read()
    file4.close()

    # pagine col vecchio template
    file5 = open("list_old_template.txt", "r", encoding='utf-8')
    stringa_errori = stringa_errori + "\nLista delle pagine che hanno il vecchio template:" + file5.read()
    file5.close()

    textwidget = tk.scrolledtext.ScrolledText(window,
                                              wrap=tk.WORD,
                                              width=40,
                                              height=28)
    textwidget.insert(tk.END, stringa_errori)
    textwidget.grid(row=10, column=0, sticky="WE", pady=10, padx=10)


# lista di tutti gli href. Usata per capire quando un link richiama una pagina già inserita nell'albero
list_href = ["https://www.unica.it/unica/it/ateneo_s04_ss03_sss01.page"]  # primo link della lista

# Creazione della finestra

window = tk.Tk()
window.geometry("1300x1000")
window.title("WebScrpatUnica")
window.configure(background="white")
window.resizable(0, 0)
window.grid_columnconfigure(0, weight=1)

logo = tk.PhotoImage(file="res/unica_logo_black.png")

logo = logo.subsample(5)

label = Label(window, image=logo, bg="white")
label.pack()
label.grid(row=0, column=0, sticky="N", padx=20, pady=10)

update_button = tk.Button(text="Aggiorna albero dei percorsi e relativi errori", command=lambda: update_window())  # update dei miei file
update_button.grid(row=2, column=0, sticky="WE", pady=10, padx=10)

tre_button = tk.Button(text="Apri il file svg dell'ultimo albero aggiornato", command=lambda: print(os.system('prova.svg'))) # apre il file svg
tre_button.grid(row=4, column=0, sticky="WE", pady=10, padx=10)

stamp_button = tk.Button(text="Stampa percorsi (txt)", command=lambda: stampa_alb())
stamp_button.grid(row=6, column=0, sticky="WE", pady=10, padx=10)

count_er = 0

error_button = tk.Button(text="Stampa errori (txt)", command=lambda: ricerca_error())  # ricerca e stampa errori
error_button.grid(row=8, column=0, sticky="WE", pady=10, padx=10)

if __name__ == "__main__":
    window.mainloop()

# TODO trovare nuovi errori
