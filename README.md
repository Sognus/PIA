# Konfigurace

V rámci KIV/PIA byl výsledný systém navržen tak, aby vyžadoval co nejméně konfigurace. Změna defaultní konfigurace pro běh systému tak není nutná, je však možná. 

## Docker compose

Soubor docker-compose.yaml nabízí možnost změny defaultního uživatele postgres databáze a jeho hesla.

- -POSTGRES_PASSWORD=\<heslo>
- -POSTGRES_USER=\<jmeno>

Následně zde lze změnit heslo pro defautního superuživatele výsledné webové aplikace:

- -DJANGO_SUPERUSER_PASSWORD=\<admin>

## Konfigurace django

V souboru **application/pia/settings.py** lze změnit údaje k e-mailu, ze kterého budou odesílány e-maily aplikací (například při obnovení hesla). V současné době je zdě nastaven e-mail u poskytovatele seznam.cz vytvořený pouze pro tuto příležitost

V případě změny defaultního jména či hesla uživatele postgres databáze je třeba upravit konfiguraci dictionary DATABASE. 

# Instalace a spuštění

1. Ujistěte se, že na cílovém počítači je nainstalován docker a docker-compose
2. Stáhněte obsah tohoto repozitáře do cílového počítače
3. Ujistěte se, že na portu 80 neběží žádná jiná aplikace
4. Ve složce kam jste rozbalili projekt spusťte příkaz **docker-compose up --build**
    - Projekt je složen ze čtyř různých kontejnerů -> nginx, asgi, redis, postgres
    - Dockerfile pro nginx a asgi jsou umístěny ve složce **docker/\<kontejner>**
    - Redis kontejner vychází z redis:alpine
    - PostgreSQL kontejner vychází z postgres:12.4-alpine
5. Příkaz spustí vše potřebné k běhu aplikace, která je nyní dostupná na http://\<ip host počítače>

# Uživatelská příručka

Aplikace by nyní měla být dostupná na adrese http://\<ip host počítače>. 

## Defaultní administrační účet 

- EMAIL: admin@admin.cz
- HESLO: admin

## Registrace, příhlášení, obnovení hesla

Defaultní stránka webové aplikace je stránka pro příhlášení, která má pod formulářem odkaz na registraci. Přihlašovací stránka má taktéž odkaz na obnovení zapomenutého hesla.

Registrace neposílá žádné ověření na e-mail uživatele, po registraci je možné se přihlásit platnou kombinací e-mail a hesla.

### Obnovení hesla

Pro obnovení hesla zadejte e-mail. V případě, že v databázi existuje uživatel s daným e-mailem, je na e-mail odeslán token. Důležitý je pouze text za localhost/ čili password-reset/\<token>. V případě, že na server přistupujete odjinud než z localhost počítače, je potřeba odkaz s tokenem zadat ručně.

## Lobby

Lobby je složeno z horního navigačního menu, které obsahuje informace o aktuálně přihlášeném uživateli a tlačítko pro odhlášení. V případě, že je uživatel administrátorem, zobrazuje navigace i odkaz na administraci 

V Lobby dále existuje obsahová část rozdělená na větší levý a menší pravý panel. 

Levý panel obsahuje události v aplikaci, například, zda se někteří z uživatelů stali přáteli či zda někdo začal či skončil hru. Levá část také obsahuje globální chat pro komunikaci se všemi aktuálně přihlášenými uživateli.

Pravý panel je převážně informační. V jednotlivých blocích lze nalézt aktuální požadavky na aktuálně přihlášeného uživatele, seznam všech online účtů, seznam přátel aktuálního účtu a jako poslední seznam všech her společně s indikací, zda již hra byla odehrána a případně kdo vyhrál. Všechny tyto bloky mají v sobě relevatní tlačítka na spuštění akcí (např. přidání/odebrání přítele, potvrzení/odmítnutí požadavku, atd.)

### Odeslání a potvrzení požadavku na uživatele

Z pravého panelu je v různých blocích možné tlačítky odeslat požadavek na uživatele (přátelství, vyzvání he hře). Tyto požadavky lze potvrdit nebo odmítnout v bloku **Požadavky**. V případě že si dva uživatelé navzájem odešlou stejný požadavek, požadavek je automaticky spojen a proveden (například uživatel A odešle uživateli B požadavek o přátelství, uživatel B požadavek ignoruje a odešle vlastní požadavek na přátelství s uživatelem A, výsledkem pak je přátelství mezi uživateli A a B).

## Herní místnost

Přijetím požadavku na hru s jiným uživatelem je uživatel přesmerování do herní místnosti. Toto přesměrování proběhne i v případě ztráty spojení a opětovného přihlášení do lobby. Tolerance na ztrátu spojení je 3 minuty. Následně je hra ukončena. V případě že uživatel zůstane v herní místnosti po skončení hry, stačí obnovit stránku a uživatel je přesmerován zpět do lobby.

Herní místnost obsahuje stejné rozložení jako Lobby. Levá část je částí herní a obsahuje nakonečnou mřízku herního pole s vepsanými souřadnicemi jednotlivých políček. Nad touto mřížkou je indikátor, zda je uživatel právě na tahu alternující mezi červeným a zeleným pozadím. Pro zabrání políček uživatel kliká na jednotlivá políčka na mřížce. 

Pravá část obsahuje blok základních informací o hře, například kdo s kým hraje a který symbol uživatel má přidělen. Lobby dále obsahuje chat omezený na aktuální herní místnost. 

Uživatel je na všechny situace upozorněn javascript alerty. 

## Administrace

Administrace obsahuje základní hlavičku a aktuální seznam uživatelů v databázi. Uživatele lze prohlásit administrátorem (zelené tlačítko) či mu administrátorská práva odebrat (červené tlačítko). Dále je možné vynutit změnu hesla. Nové heslo je vygenerováno a odesláno na uživatelům e-mail. 

Superuživatelům nelze vynutit nové heslo ani odebrat jejich administrátorský status. 

