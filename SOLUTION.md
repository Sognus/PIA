# Projekt

Projekt je složen ze čtyřech základních částí:

1. NGINX HTTP server
2. PostgreSQL databáze
3. Daphne ASGI server
4. Redis 

PostgreSQL a Redis jsou standardními kontejnery s takřka defaultní konfigurací. U PostgreSQL je pouze nastaven defaultní uživatel a jeho heslo. Data PostgreSQL databáze jsou umístěna ve složce **data/**

NGINX a Daphne ASGI docker kontejner sdílejí složku application připojenou jako VOLUME. 

## NGINX

NGINX je nastaven tak, aby poskytoval statické soubory jako javascript soubory, css styly či obrázky. Pro všechny ostatní požadavky funguje NGINX jako PROXY server, který předává požadavky Daphne ASGI kontejneru.

Přesun statických souborů do složky static řeší framework django v Daphne ASGI kontejneru

## Daphne ASGI server

Kontejner obsahující daphne server, který spouští a poskytuje přístup k DJANGO ASGI aplikaci na portu 8000. Kontejner obsahuje všechny potřebné závislosti pro spuštění aplikace

## Redis

Redis je použit pro komunikaci mezi různými Consumer objekty použitými pro zpracování WebSocketů

# BACKEND

Pro backend webové aplikace je použit python framework Django. Framework byl doplněn o knihovnu Django Channels pro zajištění asynchronosti (hlavně implementace WebSocketů).

Django je vysoce modulární. Aktuální řešení proto obsahuje větší množství menších projektů. Prakticky každá stránka je svojí vlastní aplikací. 

Každá aplikace má svojí definici databázových modelů, routeru pro websockety, routeru pro HTTP požadavky, pohledy, statické soubory a šablony a dalšího

### Aplikace:

1. administration (stránka pro administraci)
2. api (imitace REST API pro administraci)
3. game (herní routing a herní místnost)
4. lobby (stránka pro lobby)
5. pia (jádro-aplikace agregující všechny ostatní)

## Cesta požadavku - HTTP

- Nejprve je určeno, zda požadavek uživatele je požadavek na statický soubor, v takovém případě NGINX poskytne daný soubor pokud existuje
- Zbylé požadavky jsou odeslány na daphne ASGI server a zjištuje se jejich protokol HTTP vs WebSocket
- Je zjišťováno zda HTTP požadavek vede na definovanou cestu, pokud ano je zavolána příslušná CONTROL/VIEW funkce
- Příslušná VIEW funkce volá načtení dat z modelu a předává data pro render šablony
- Výsledná šablona je vrácena uživateli

## Cesta požadavku - WEBSOCKET

- Nejprve je určeno, zda požadavek uživatele je požadavek na statický soubor, v takovém případě NGINX poskytne daný soubor pokud existuje
- Zbylé požadavky jsou odeslány na daphne ASGI server a zjištuje se jejich protokol HTTP vs WebSocket
- Je zjišťováno zda požadavek vede na definovanou cestu, pokud ano je zavolána RECEIVE funkce příslušného CONSUMERU
- Receive funkce buď odesílá zpět uživatelskému websocketu odpověď nebo notifikuje ostatní uživatele

# Frontend

Frontend je vytvořen kombinací základních HTML5, CSS3, základního Javascriptu, JQuery a Bootstrap technologií.

Základní layout stránky byl vytvořen pomocí HTML a Bootstrap. Veškeré specifické úpravy byli docíleny custom CSS nebo kombinací základního javascriptu a JQUERY. 

Veškeré zpracování událostí a dynamičnost stránky funguje na základě JQUERY událostí. Ajax požadavky a jejich zpracování je také provedeno pomocí JQuery. 

Pro Websockety je použita základní websocket objekt s přiřazenými obslužnými funkcemi. JQuery události mají za následek odeslání WebSocket dat. Websocket komunikace je
vytvořena ve stylu téměř na každý požadavek existuje odpověď od serveru, ten však může poslat data samovolně. Příchozí data zpracuje obslužná funkce, která na základě custom JSON komunikačního protokolu provádí akce.

Nekonečný canvas ve hře byl vytvořen za použití knihovny KonvaJS, která dovoluje na canvas vytvářet jednotlivé tvary a obrázky a přidělit jim události. Veškerá další herní funkčnost je docílena pomocí obslužných funkcí těchto událostí. 
Obslužné funkce obsahují odesílání WebSocket dat JSON protokolu.




