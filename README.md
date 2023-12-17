## Protocolul Shamir:
 - fiind dat Secret S , un numar n si un m impartim S in n si pentru al recompune folosim m parti.

**PRECONDITII**:
- fie *PRIME* un numar prim > Secret (Acest numar prim este folosit pentru a largi multimea probabilitatilor de determinare secretului, avand in vedere ca lucram cu multimi finite de elemente;

**PAS1**
 - construim un polinom de gradul m-1 cu coeficienti arbitrari din intervalul 1, PRIME -1, iar termenul liber fiind chiar Secretul.
   
**PAS2**:
- calculam *n* puncte folosind polinomul determinat anterior sub forma *f(x) mod PRIME*
(aceste puncte reprezinta defapt cele n parti in care am impartit secretul nostru, cum polinomul este de gradul m-1 vom vedea ca folosind doar m din acestea putem reconstrui secretul
 folosind Interpolarea Lagrage exemplificata in pasul urmator)

**PAS3**
 - pentru x oarecare calculculam m polinoame folosind *m* puncte:
  
l0(x) = x-x1/ x0 -x1 * x-x2/x0-x2 * ... x-xm/x0-xm


l1(x) = x- x0/x1-x0 * x-x2/x1-x2 * ... * x-xm/x1-xm


.....................................................................................


lm-1(x) = x-x0/ xm-1-x0 * .... x-xm-2/ xm-1 - xm-2


**PAS4**:
- pentru reconstructia polinomului folosim urmatoare formula:
  
*f(x) = suma din yj * lj(x) mod PRIME* , unde y este coordonata punctului j si lj este lagrange de j calculat mai sus



## Secret share pentru fisiere folosind protocolul Shamir:

**Clasa Shamir**:
- atributul *file_path* reprezinta locatia fisierului pe care vrem sa il impartim pentru a-l securiza;
- atributul *minim_paticipants* reprezinta numarul minim de fisiere din care vrem sa reconstruim fisierul impartit initial;
- atributul *n* reprezinta numarul de fisiere in care vom imparti secretul (continul fisierului);
  
- metoda *determinate_secret*: deschide fisierul cu care am initializat clasa si il citeste intr-un format binar creand un int din acesta (ultilizand metoda 'big' - adica bytes-ul cel mai semnificativ este primul)
 acest int este retinut in atributul clasei *secret* (acesta va fi impartit folosind protocolul shamir);

- metoda *coefficients_det* : determina coeficienti arbitrari intre 1 si PRIME (ce are o valoare default setata) si termenul liber fiind reprezentat de int-ul format din bitii fisierului, acesti coeficienti sunt retinuti in structura coefficients[] (*PAS1* din protocolul Shamir);

- metoda *_calc_function(x)* : pentru un x dat calculeaza valoarea polinomului determinat (!nu uitam de mod PRIME);

- metoda *compute_points*: folosind puncte de cu x de la 1 la n calculeaza valorile y pentru acestea folosind functia _calc_points (*PAS2* din protocolul Shamir);

- metoda *split_information* : creaza sau deschide n fisiere (cu denumire file_{i}.secret) si scrie in acestea valorile punctelor (informatia secreta este defapt impartita in aceste puncte sub forma de int-uri ce ar reprezenta bytes, insa fara vreun inteles luati separati);

**RECONSTRUCTIA**:
- functia *lagrange_basis* primeste ca parametri punctele din care vrem sa aflam secretul, un index si x: 
    - calculeaza pentru punctul cu indexul dat polinomul Lagrange, (*PAS3* din protocolul Shamir) , returnand rezultatul sub forma    [numitor, numarator]
      
        ( __cum secretul este reprezentat de termenul liber, putem sa l luam in considerare pe x ca fiind 0__)
- functia *lagrange_interpolation* , care primeste un x = 0 , punctele de interpolat si numarul prim:
    - calculeaza toti numitorii si numaratorii folosind functia lagrange_basis
    - calculeaza numitorul general ca produs de numitori
    - calculam polinomul:  sau mai exact termenul liber a polinomului
        - luand in calcul faptul ca diviziunea poate duce la pierdere de zecimale (pierderi de informatie in cazul nostru),vom folosi algoritmul extins a lui euclid care spune ca : impărțirea în numere întregi modulul p înseamnă găsirea inversului a numitorului modulo p și apoi înmulțirea numărătorului cu acest invers (lucru pe care il facem in functia *division_modulo* ce apeleaza *euclid_alg*) 
        - calculam suma (*PAS4* din protocolul Shamir) in felul urmator: la numitor vom avea numitorul general iar la numarator vom avea yj * numarator [j] * numitor_general / numitor[j] mod p (pe care il calculam cu ajutorul functiei exemplificate mai sus)
        - acum ne ramane sa calculam num = suma pentru orice j si apoi vom avea **Secretul** obtinut din num / numitor % PRIME ( +PRIME %PRIME de la final asigura pozitivitatea rezultatului)
    - aceasta functie returneaza **Secretul**
- functia *reconstruct_file*, primeste o lista de fisiere si numarul prim folosit in algoritm:
    - le deschide si isi ia din acestea cele m puncte pentru a reconstrui fisierul
    - aceasta apeleaza lagrange_interpolation care returneaza secretul
    - deschide sau creaza fisierul rezultat (result.txt) in modul binar si scrie in acelasi fel sub forma de bytes secretul, obtinand asadar informatia pe care a impartit-o intial;

