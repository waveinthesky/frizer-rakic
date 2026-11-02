# Frizer kuće Rakića – aplikacija za termine

Ovo je finalna verzija aplikacije. Radi na bilo kojem telefonu kao prava aplikacija,
termini se čuvaju u tvojoj Firebase bazi i vidiš ih na svim uređajima, a HCL vijesti
i datumi PS5 igara se sami osvježavaju preko GitHuba.

Sve skupa je besplatno: GitHub Pages i GitHub Actions za javni repozitorij,
Firebase na besplatnom planu (Spark).

## Šta je u paketu

| Fajl | Čemu služi |
|---|---|
| `index.html` | Cijela aplikacija |
| `firebase-config.js` | Ovdje upisuješ podatke svog Firebase projekta (korak 1.6) |
| `firestore.rules` | Pravila: samo ti, kad si prijavljen, vidiš svoje termine |
| `manifest.webmanifest`, `sw.js`, `img/` | Ikonica na telefonu, rad bez interneta, logo |
| `data/vijesti.json` | HCL vijesti (puni se samo, svaki sat) |
| `data/igre.json`, `data/posebno.json` | Datumi PS5 igara (puni se samo, svakog ponedjeljka) |
| `scripts/`, `.github/workflows/` | Automatika koja osvježava vijesti i igre |
| `igre.html` | Pregled kalendara igara, za provjeru da automatika radi |

---

## Korak 1: Firebase (baza i prijava), oko 15 minuta

Firebase konzola se povremeno malo promijeni. Ako neko dugme ne izgleda isto, traži sličan naziv.

**1.1 Napravi projekat**
Otvori console.firebase.google.com, prijavi se Google nalogom i klikni *Create a project*.
Ime: `frizer-rakic`. Google Analytics isključi, ne treba.

**1.2 Uključi prijavu e-mailom**
Lijevo *Build → Authentication → Get started*. Na kartici *Sign-in method* izaberi
*Email/Password*, uključi prvi prekidač (*Enable*) i sačuvaj.

**1.3 Napravi svoj nalog (PIN)**
U *Authentication → Users* klikni *Add user*.
- *Email:* tvoj pravi e-mail (na njega stiže link ako zaboraviš PIN).
- *Password:* tvoj PIN, tačno **6 cifara**, npr. `482915`. Ne koristi `123456` ni datum rođenja.

U aplikaciju se poslije prijavljuješ samo tim PIN-om. PIN nikome ne šalji, ni meni.

**1.4 Napravi bazu**
Lijevo *Build → Firestore Database → Create database*.
Ako pita za izdanje, izaberi *Standard*. Lokacija: `europe-west3 (Frankfurt)`.
Način: *Start in production mode*.

**1.5 Zalijepi pravila**
U Firestore otvori karticu *Rules*, obriši sve što piše i zalijepi cijeli sadržaj
fajla `firestore.rules`. Klikni *Publish*.

**1.6 Poveži aplikaciju s bazom**
Klikni zupčanik pored *Project Overview → Project settings*. Dolje kod *Your apps* klikni ikonu `</>` (Web).
Ime: `frizer-rakic-web`. *Firebase Hosting* ne uključuj. Klikni *Register app*.
Pojavit će se blok koji počinje s `const firebaseConfig = {`.
U fajlu `firebase-config.js` su već upisani podaci tvog projekta (`bfkr-d2268`).
Iz tog bloka prepiši još samo `apiKey` i `appId`, umjesto `UPISI_apiKey` i `UPISI_appId`.
U isti fajl, umjesto `UPISI_EMAIL`, upiši e-mail iz koraka 1.3.
Ako ti je lakše, pošalji mi taj blok i ja popunim fajl. Te vrijednosti nisu tajna.

**1.7 Dozvoli svoju adresu** (uradi poslije koraka 2)
*Authentication → Settings → Authorized domains → Add domain* i upiši
`TVOJE-IME.github.io` (tvoje GitHub ime, malim slovima). Bez ovoga prijava javlja grešku.

---

## Korak 2: GitHub, oko 10 minuta

**2.1** Napravi nalog na github.com i novi repozitorij `frizer-rakic`, tip *Public*.

**2.2 Ubaci fajlove.** U repozitoriju *Add file → Upload files* i prevuci sve iz ovog
paketa, zajedno s folderima, i to s već popunjenim `firebase-config.js`.
Folder `.github` je na nekim računarima sakriven: na Macu ga prikažeš s Cmd+Shift+tačka,
a na Windowsu u Exploreru uključiš *Hidden items*. Klikni *Commit changes*.

**2.3 Uključi stranicu.** *Settings → Pages →* Source: *Deploy from a branch*,
Branch: `main`, folder `/ (root)`, *Save*. Za minut-dva aplikacija je na adresi
`https://TVOJE-IME.github.io/frizer-rakic/`

**2.4 Dozvoli automatici da upisuje.** *Settings → Actions → General →
Workflow permissions →* *Read and write permissions*, *Save*.

**2.5 Ključ za igre.** Na rawg.io/apidocs napravi besplatan nalog i kopiraj *API key*.
Onda u repozitoriju *Settings → Secrets and variables → Actions → New repository secret*:
ime `RAWG_KEY`, vrijednost tvoj ključ.

**2.6 Prvo pokretanje.** Kartica *Actions*: otvori *Osvježi HCL vijesti → Run workflow*,
pa *Osvježi datume igara (PS5) → Run workflow*. Kad oba dobiju zelenu kvačicu,
automatika radi. Provjera: `https://TVOJE-IME.github.io/frizer-rakic/igre.html`

**2.7** Vrati se na korak 1.7 i dodaj svoju adresu u Firebase.

---

## Korak 3: Na telefonu

1. Otvori `https://TVOJE-IME.github.io/frizer-rakic/` i ukucaj svoj PIN od 6 cifara.
2. Napravi ikonicu:
   - **iPhone:** u Safariju dugme *Dijeli* (kvadrat sa strelicom) → *Dodaj na početni ekran*.
   - **Android:** u Chromeu meni ⋮ → *Instaliraj aplikaciju* (ili *Dodaj na početni ekran*).
3. Ostaješ prijavljen i PIN ne kucaš svaki put, nego samo na novom telefonu ili poslije odjave.
4. PIN mijenjaš u *Postavke → Salon → PIN za prijavu → Promijeni*.

Isti nalog možeš koristiti na više telefona i na računaru, a termini su svuda isti.

---

## Korak 4: Prebaci postojeće termine

1. U staroj aplikaciji (Claude link): *Postavke → Salon → Izvoz svih podataka → Izvezi* i sačuvaj fajl.
2. U novoj aplikaciji: *Postavke → Salon → Uvezi podatke → Uvezi* i izaberi taj fajl.

Prebace se termini, klijentske bilješke i sve postavke: usluge, cijene, radno vrijeme i neradni dani.

---

## Kako radi u pozadini

- **Bez interneta:** aplikacija se otvara i radi. Izmjene se čuvaju na telefonu i same
  pošalju u bazu kad se internet vrati. Gore desno piše *Bez interneta* dok veze nema.
- **Štednja baze:** termini su složeni po mjesecima (jedan zapis po mjesecu), pa jedno
  otvaranje aplikacije potroši tek desetak čitanja. Besplatni plan dozvoljava desetine
  hiljada čitanja dnevno, pa se ne može potrošiti ni uz stalno korištenje.
- **Vijesti:** svaki sat GitHub pokupi naslove s HCL-a i spremi ih u `data/vijesti.json`.
- **Igre:** svakog ponedjeljka GitHub pokupi PS5 igre za narednih godinu dana i izračuna im boje iz slike.
- **Probna verzija:** dugme *Isprobaj bez prijave* na ekranu za prijavu. Sve se tada čuva
  samo na tom telefonu, pa je zgodno da drug proba aplikaciju.

## Održavanje

- **Rezervna kopija:** jednom mjesečno *Postavke → Salon → Izvezi rezervnu kopiju*.
- **Kad mijenjaš `index.html`:** u `sw.js` povećaj broj u `frizer-rakic-v1` (npr. na `v2`), da se nova verzija sigurno učita na telefonima.
- **Posebne igre:** u `data/posebno.json` dodaj igru s datumom i bojama. Oznaka `"tip": "gta"` taj dan boji cijelu aplikaciju.

## Ako nešto ne radi

| Poruka ili problem | Rješenje |
|---|---|
| Ova adresa nije dozvoljena (Authorized domains) | Uradi korak 1.7 |
| U Firebase konzoli uključite prijavu e-mailom | Uradi korak 1.2 |
| Pogrešan PIN | Dodirni „Zaboravili ste PIN?“, otvori link iz e-maila i kao novu lozinku upiši 6 cifara |
| Na ekranu za PIN traži e-mail | U `firebase-config.js` nije upisan `SALON_EMAIL` |
| Previše pokušaja | Firebase je privremeno blokirao prijavu zbog više pogrešnih PIN-ova. Sačekaj par minuta. |
| Nemate dozvolu za ovu izmjenu | Provjeri da su pravila iz koraka 1.5 objavljena |
| Piše „Probna verzija“, a ne treba | `firebase-config.js` nije popunjen (korak 1.6) |
| Actions: „Nedostaje RAWG_KEY“ | Uradi korak 2.5 |
| Actions: greška kod `git push` | Uradi korak 2.4 |
| Vijesti ili igre se ne mijenjaju | Kartica *Actions*: pogledaj zadnje pokretanje i pošalji mi screenshot greške |

Podaci o igrama dolaze s RAWG.io, a vijesti s HCL.hr.
