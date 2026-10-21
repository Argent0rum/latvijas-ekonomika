# Latvijas ekonomika skaitļos

Interaktīvs panelis ar 29 galvenajiem ekonomikas rādītājiem Latvijai, Lietuvai, Igaunijai un ES vidējam. Dati nāk no Eurostat un tiek **automātiski atjaunināti katru dienu**.

**Panelis:** https://argent0rum.github.io/latvijas-ekonomika/

*English: an interactive dashboard of 29 key economic indicators for Latvia, the other Baltic states and the EU average, updated daily from Eurostat by GitHub Actions. Indicators and countries are set in two simple settings files.*

## Ko var darīt panelī

- Redzēt jaunāko vērtību katram rādītājam un **izmaiņu pret pagājušo gadu** — vai pret 2, 3, 5, 10, 15 vai 20 gadiem iepriekš (izvēlne „Salīdzināt ar”).
- Noklikšķināt uz rādītāja, lai redzētu **grafiku kopš 2000. gada**, salīdzinātu valstis un lejupielādētu datus CSV formātā.
- Pārslēgties uz **tabulas skatu**, meklēt rādītājus, mainīt valodu (LV/EN).
- Zaļš/sarkans izmaiņas krāsojums rāda, vai izmaiņa ir laba vai slikta (piem., zemāks bezdarbs = zaļš).

## Kā pievienot vai noņemt

Viss tiek iestatīts divos failos mapē `config/`. Pēc izmaiņu saglabāšanas GitHub pats lejupielādē jaunos datus (aptuveni 1 minūtē).

**Valsts pievienošana** — `config/valstis.yaml`, pievieno 3 rindas:
```yaml
- kods: FI
  lv: Somija
  en: Finland
```

**Rādītāja pievienošana** — `config/raditaji.yaml`: iekopē esošu bloku un nomaini datu kopu un filtrus. Lai uzzinātu pareizos kodus:
1. Atrodi datu kopu [Eurostat datu pārlūkā](https://ec.europa.eu/eurostat/databrowser) (kods ir adresē, piem. `une_rt_m`).
2. GitHub cilnē **Actions → Izpētīt Eurostat datu kopas → Run workflow** ieraksti kodu.
3. Rezultāts parādīsies failā `izpete/rezultats.txt` ar visiem iespējamajiem filtriem.

**Rādītāja noņemšana** — izdzēs tā bloku no `config/raditaji.yaml`.

Ja kāds rādītājs kādu dienu neielādējas (piem., Eurostat maina kodu), panelis turpina rādīt iepriekšējos datus, un problēma redzama failā `docs/data/statuss.json`.

## Faili

| Fails | Kas tas ir |
|---|---|
| `config/raditaji.yaml` | rādītāji, kategorijas, nosaukumi, apraksti |
| `config/valstis.yaml` | valstis |
| `scripts/atjaunot.py` | lejupielādē datus no Eurostat API → `docs/data/dati.json` |
| `scripts/izpete.py` | palīgrīks datu kopu izpētei |
| `docs/index.html` | pats panelis (HTML + JavaScript, bez papildu bibliotēkām) |
| `.github/workflows/atjaunot.yml` | ikdienas automātiskā atjaunināšana (katru rītu) |

## Piezīmes par datiem

- Inflācija ir Eurostat saskaņotais patēriņa cenu indekss (SPCI). CSP publicētais nacionālais PCI var nedaudz atšķirties.
- No 2026. gada Eurostat pāriet uz jauno patēriņa klasifikāciju (ECOICOP 2); agrākie gadi tiek ņemti no iepriekšējās datu kopas, lai laikrinda būtu nepārtraukta.
- Atzīmes pie skaitļiem: **p** — provizoriski dati, **e** — aplēse, **b** — laikrindas pārrāvums.
