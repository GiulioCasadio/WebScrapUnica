import requests
from bs4 import BeautifulSoup

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
    return BeautifulSoup(page.content, 'html.parser')  # restituisce l'html della pagina selezionata


# primi nodi dell'albero
def primi_nodi(padre):
    # inserisce i primi figli dell'albero del portale
    aux = 0  # contatore li

    for i in range(1, len(children)):
        child = Albero(children[i].find('a'))  # figlio da aggiungere
        list_href.append(child.Contenuto['href'])
        # controllo se questo figlio ha a sua volta altri figli
        ul_side_f = soup.find('ul', {'class': 'navmenu'})  # seleziona la barra menu laterale
        li_side_f = ul_side_f.findChildren('li')  # seleziona tutti i figli della navbar
        ul_side_s = li_side_f[i+aux].find('ul')  # seleziona la sottobarra dei figli diretti
        if ul_side_s is not None:
            li_side_s = ul_side_s.findChildren('a')  # seleziona tutti i figli della sottonavbar
            aux += len(li_side_s)

            j = 0
            for j in range(len(li_side_s)):
                nep = Albero(li_side_s[j])  # nipote
                list_href.append(nep.Contenuto['href'])
                child.figlio.append(nep)  # inserisco il npote della radice come figlio del figlio diretto

        tree.figlio.append(child)  # inserisco questo figlio

    return padre


# stampa del percorso
def update_tree(t, tab):  # t = tree, s = stringa
    if t is not None:
        file_tree = open('last_updated_tree.txt', 'a')
        s = "\t" * tab + normaliz(t.Contenuto.get_text() + "\n")
        file_tree.write(s)
        file_tree.close()
        if t.figlio is not None and len(t.figlio) != 0:  # Se esiste almeno un figlio a questo nodo
            tab += 1  # avanzo di un tab
            for i in range(0, len(t.figlio)):
                update_tree(t.figlio[i], tab)
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


# creazione albero
def insert_child(padre):
    i = 0
    if len(padre.figlio) != 0:
        for i in range(len(padre.figlio)):
            padre.figlio[i] = insert_child(padre.figlio[i])  # percorro ricorsivamente tutto l'albero sino a trovare tutti i nodi finali
    else:
        padre = insert_list_group(padre)
    return padre


def insert_list_group(padre):
    aux = 0  # contatore li
    a_ref = padre.Contenuto['href']
    new_soup = make_soup(a_ref)
    vert_internal_menu = new_soup.find(class_='list-group')  # menu laterale

    if vert_internal_menu is not None:  # verifico se è presente il menu'
        child_li = vert_internal_menu.findAll(class_='list-group-item')  # tutti gli li di questa sidebar

        # controllo gli li principali (già presenti nell'albero) e verifico se possiedono figli
        for i in range(len(child_li)):  # -> organizzazione...
            direct_child = child_li[i]  # figlio i della sidebar. Devo verificare se possiede figli
            if padre.Contenuto['href'] == direct_child.find('a')['href']:  # verifico se sto analizzando il nodo corrett
                direct_child_child = direct_child.findChildren('li')  # lista dei sottofigli
                j = 0

                if len(direct_child_child) != 0:
                    # scorro i figli della lista laterale -> organi accademici...
                    for j in range(len(direct_child.find('ul', recursive=False).findChildren('li', recursive=False))):
                        albe_da_inserire = Albero(direct_child_child[j+aux].find('a'))
                        list_href.append(albe_da_inserire.Contenuto['href'])
                        # caso in cui non ci siano figli da inserire (quindi cerco nel body)
                        if direct_child_child[j+aux].find('ul') is None:
                            body_link(albe_da_inserire)

                        padre.figlio.append(albe_da_inserire)  # inserisco il sotto nodo
                        # verifico se ci sono ulteriori figli e se sto analizzando il nodo corretto

                        if direct_child_child[j+aux].find('ul') is not None:
                            h = 0
                            for h in range(len(direct_child_child[j+aux].findChildren('li'))):  # -> rettore..
                                albe_da_inserire_deep = Albero(direct_child_child[j+aux+1].find('a'))
                                list_href.append(albe_da_inserire_deep.Contenuto['href'])
                                body_link(albe_da_inserire_deep)  # controllo body
                                padre.figlio[j].figlio.append(albe_da_inserire_deep)
                                aux += 1

    return padre


# test link interni
def body_link(alb):
    soup = make_soup(alb.Contenuto['href'])
    internal_link = soup.findChildren('ul', {'class': 'article-links-list'})
    for i in range(len(internal_link)):
        link_check = internal_link[i].findAll("li")
        if len(link_check) > 1:
            for j in range(len(link_check)):
                aux = True
                link_check_href = Albero(link_check[j].find('a'))
                for old_h in list_href:  # controllo se è già stato aggiunto quetso nodo
                    if link_check_href.Contenuto['href'] == old_h:
                        aux = False
                if aux:
                    alb.figlio.append(link_check_href)
                    list_href.append(link_check_href.Contenuto['href'])
                    try:
                        # controllo se dentro questa pagina son presenti ulteriori link
                        soup_next = make_soup(link_check_href.Contenuto['href'])
                        if soup_next is not None \
                                and soup_next.find("base") is not None \
                                and soup_next.find("base") == "href=\"https://www.unica.it/unica/":  # verifica dominio

                            # controllo errori
                            check_page(soup_next, link_check_href)

                        #     body_link(link_check_href)
                    except requests.exceptions.SSLError:
                        print("An exception occurred")
                    except requests.exceptions.ConnectionError:
                        print("An exception occurred")
            else:
                if len(link_check) == 1:
                    aux = True
                    link_check_href = Albero(link_check[0].find('a'))
                    for old_h in list_href:   # controllo se è già stato aggiunto quetso nodo
                        if link_check_href.Contenuto['href'] == old_h:
                            aux = False
                    if aux:
                        try:
                            alb.figlio.append(link_check_href)
                            list_href.append(link_check_href.Contenuto['href'])

                            # controllo se dentro questa pagina son presenti ulteriori link
                            soup_next = make_soup(link_check_href.Contenuto['href'])
                            if soup_next is not None \
                                    and soup_next.find("base") is not None \
                                    and soup_next.find("base") == "href=\"https://www.unica.it/unica/":  # verifica dominio

                                # controllo errori
                                check_page(soup_next, link_check_href)
                            #     body_link(link_check_href)
                        except requests.exceptions.SSLError:
                            print("An exception occurred")
                        except requests.exceptions.ConnectionError:
                            print("An exception occurred")

            # controlli errori della pagina
            check_page(soup, alb)


def check_page(soup, alb):
    # verifico se la pagina è vuota
    check_empty_page(soup, alb)


# verifica se la pagina è priva di contenuto
def check_empty_page(soup, alb):
    cla = None
    aux = True  # presuppongo che la pagina sia corretta

    # controlli per ricerca link o div
    sec = soup.find('section', {'class': 'contenuto'})
    if sec is not None:
        cla = sec.find('div', {'class': 'col-lg-9'})

    # controllo se presente l'article con il seguente testo e poise presente almeno un link o div
    if (soup.find('article') is not None and soup.find('article').get_text() == "\n\r\nNessun contenuto trovato\t\t\t\n")\
            or (cla is not None and cla.find('a') is None and cla.find('div') is None):
        aux = False

    if not aux:  # se è false insomma
        file_empty = open('list_empty_page.txt', 'a')
        s_href = alb.Contenuto['href'] + "\n"
        file_empty.write(s_href)
        file_empty.close()



def delete_backups():
    # elimino il vecchio albero
    file_tree = open("last_updated_tree.txt", "w")
    file_tree.truncate()  # elimina il contenuto
    file_tree.close()

    # elimino i vecchi backup degli errori
    file_empty = open("list_empty_page.txt", "w")
    file_empty.truncate()  # elimina il contenuto
    file_empty.close()


##################################################################
#                       AREA DEI TEST                            #
##################################################################

# tree = None  # albero finale, inizalmente contiene solo la radice
# soup = make_soup('https://www.unica.it/unica/it/ateneo_s07_ss05_sss02_ssss01.page')
#
# check_empty_page(soup, tree)

##################################################################

# lista di tutti gli href. Usata per capire quando un link richiama una pagina già inserita nell'albero
list_href = ["https://www.unica.it/unica/it/ateneo_s04_ss03_sss01.page"]  # primo link della lista

# MENU'
cho = 1

while cho != '0':
    cho = input('0 -> EXIT\n'
                '1 -> STAMP\n'
                '2 -> UPDATE\n'
                '3 -> LIST ALL ERRORS')
    if cho == '0':
        print('Chiusura')
    else:
        if cho == '1':  # STAMPA
            # stampa tutto l'albero.
            file1 = open("last_updated_tree.txt", "r")
            print(file1.read())
            file1.close()

        else:
            if cho == '2':  # UPDATE
                # elmino i vecchi backup
                delete_backups()

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
                update_tree(tree, 0)  # ripopola il file
                print("Sono state analizzati " + str(len(list_href)) + " pagine")

            else:
                if cho == '3':  # ricerca errori
                    print("\nLista delle pagine non aventi contenuto:")
                    # stampa tutti link.
                    file2 = open("list_empty_page.txt", "r")
                    print(file2.read())
                    file2.close()
                else:
                    print("Nessuna opzione per questa scelta")


# link ricorsivi
# vecchio layout pagine unica
#

# TODO creare un menu iniziale con la possibilità di caricare un log di dati precedentemente creato
