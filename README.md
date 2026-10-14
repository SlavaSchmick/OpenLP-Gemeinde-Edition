# OpenLP Gemeinde-Edition

Die **OpenLP Gemeinde-Edition** ist eine **modifizierte Version** von [OpenLP](https://openlp.org/) 3.1.7.
Sie enthält Ergänzungen und Änderungen, die nicht von den OpenLP-Entwicklern stammen und von ihnen nicht
unterstützt werden. Wie OpenLP steht sie unter der GNU General Public License Version 3 (siehe `LICENSE`).
Die englische Original-Beschreibung von OpenLP steht in `README.rst`.

Repository, Quellcode und Updates: <https://github.com/SlavaSchmick/OpenLP-Gemeinde-Edition>

## Download und Installation

Unter [Releases](https://github.com/SlavaSchmick/OpenLP-Gemeinde-Edition/releases/latest) beim neuesten Release
unter *Assets*:

- **`OpenLP-Gemeinde-Edition-…-Setup-x64.exe`** – das Setup (Windows 10/11, 64 Bit, VLC enthalten). Ein vorhandenes
  OpenLP wird ersetzt; Lieder, Bibeln, Designs und Einstellungen bleiben erhalten.
- **`OpenLP-Gemeinde-Edition-Liederbuecher.zip`** – die Liederbücher Deutsch (1310 Lieder) und Russisch (800 Lieder).
  Entpacken, dann in OpenLP *Datei → Importieren → Lied → „OpenLyrics oder OpenLP 2 exportierte Lieder“*, mit
  *Hinzufügen...* alle Dateien der Ordner `Deutsch` und `Russisch` wählen (Strg+A). Nur einmal importieren.
  Danach findet die Liedsuche die Lieder z. B. mit `d203` oder `r47`.

Die ausführliche Beschreibung aller Ergänzungen für Anwender steht in
[`documentation/gemeinde-edition/dokumentation.html`](documentation/gemeinde-edition/dokumentation.html).

## Ergänzungen und Änderungen im Überblick

- **Live-Video:** neue Erweiterung, zeigt Kameras, HDMI-Capture und virtuelle Kameras (z. B. OBS) auf der Leinwand
  (`openlp/plugins/livevideo`).
- **Audio-Ausgabe:** Ton von Videos getrennt für Live und Vorschau auf ein Gerät legen, z. B. Dante Via.
- **Bibel:** ganzes Kapitel ab dem gesuchten Vers, tolerante Eingabe (deutsch, russisch, ukrainisch),
  Enter = Vorschau, Umschalt+Enter = live mit Fokus in der Live-Liste, Strg+B, ein Vers wird nie auf zwei Folien
  geteilt (auch mit Vergleichstext), leere Bibeln aus fehlgeschlagenen Importen werden aufgeräumt.
- **Lieder:** Suche während der Eingabe, Kennungen wie `r47` / `d203` mit exaktem Treffer oben,
  Enter / Umschalt+Enter, Strg+L.
- **Liedstatistik:** Rangliste der meistgesungenen Lieder (Zeitraum, Liederbuch, Suche), speicherbar als PDF oder
  CSV; die Liedprotokollierung ist von Anfang an eingeschaltet.
- **Automatische Textgröße:** größte passende Schrift je Folie innerhalb einer Spanne im Design; Liedzeilen werden
  nicht umbrochen, Bibelverse immer ganz gezeigt.
- **Präsentationen:** PowerPoint funktioniert auch mit Microsoft 365 (Click-to-Run).
- **Sprachen:** Englisch, Deutsch, Russisch (vervollständigt) und Ukrainisch (neu).
- **Kennzeichnung und Updates:** Name „OpenLP Gemeinde-Edition“, Version `3.1.7+gemeinde.N`, Updates kommen aus den
  Releases dieses Repositorys statt von openlp.org (`openlp/core/edition.py`, `openlp/core/ui/editionupdate.py`).
- **Windows-Setup:** `packaging/windows` (PyInstaller und Inno Setup, mit VLC).

## Aufbau des Repositorys

- Der erste Commit (Tag `openlp-3.1.7`, Branch `upstream`) ist der **unveränderte offizielle Quellcode** von
  OpenLP 3.1.7. Alle Änderungen der Gemeinde-Edition liegen in den Commits danach auf `main`. So zeigt
  `git diff openlp-3.1.7 main` jederzeit genau, was geändert wurde.
- `sources/OpenLP/Deutsch` und `sources/OpenLP/Russisch`: die bereinigten Liederbücher im OpenLP-Format
  (OpenLyrics). Import in OpenLP: *Datei → Importieren → Lied → „OpenLyrics oder OpenLP 2 exportierte Lieder“*.

## Entwicklung

Voraussetzungen: Windows 10/11 (64 Bit), Python 3.11, VLC (64 Bit), Inno Setup 6.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[test]   # oder die Pakete aus setup.py
.\.venv\Scripts\python.exe run_openlp.py               # OpenLP starten
.\.venv\Scripts\python.exe -m pytest tests --ignore=tests/functional
```

## Setup bauen

```powershell
powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1
```

Das Ergebnis liegt in `packaging\windows\output`, z. B. `OpenLP-Gemeinde-Edition-3.1.7-gemeinde.1-Setup-x64.exe`.
Das Skript übernimmt das auf dem Bau-Rechner installierte VLC – für eine neuere VLC-Version VLC aktualisieren und neu
bauen.

## Ein Update veröffentlichen

Installierte Gemeinde-Editionen prüfen beim Start (einmal täglich) das **neueste Release** dieses Repositorys und
bieten es zum Herunterladen und Installieren an. Dafür muss in `openlp/core/edition.py` das Repository eingetragen
sein (`EDITION_REPOSITORY = 'besitzer/name'`) und das Repository öffentlich sein.

1. Version in `openlp/.version` erhöhen, z. B. `3.1.7+gemeinde.2`.
2. Tests laufen lassen und das Setup bauen (siehe oben).
3. Committen, taggen und hochladen:
   ```powershell
   git commit -am "Gemeinde-Edition 3.1.7+gemeinde.2"
   git tag v3.1.7+gemeinde.2
   git push origin main --tags
   ```
4. Auf GitHub unter **Releases → Draft a new release** den Tag `v3.1.7+gemeinde.2` wählen, die Setup-Datei
   (`…-Setup-x64.exe`) und die Liederbücher (`OpenLP-Gemeinde-Edition-Liederbuecher.zip`, aus `sources/OpenLP`)
   als Dateien anhängen und **veröffentlichen** – nicht als Entwurf und nicht als Vorabversion,
   sonst wird es nicht als Update angeboten.

Die Versionen werden so verglichen: `3.1.7+gemeinde.2` ist neuer als `3.1.7+gemeinde.1`, und `3.1.8+gemeinde.1` ist
neuer als jede `3.1.7+gemeinde.N`. GitHub prüft die Datei beim Herunterladen mit einer Prüfsumme; eine beschädigte
Datei wird nicht gestartet.

## Eine neue offizielle OpenLP-Version einarbeiten

1. Den offiziellen Quellcode der neuen Version herunterladen, z. B.
   `https://gitlab.com/openlp/openlp/-/archive/3.1.8/openlp-3.1.8.zip`.
2. Auf dem Branch `upstream` den Inhalt durch die neue Version ersetzen und festhalten:
   ```powershell
   git switch upstream
   git rm -r -q .            # alle Dateien entfernen (die neue Version wird gleich hineinkopiert)
   # ... Inhalt von openlp-3.1.8 in den Projektordner kopieren ...
   git add -A
   git commit -m "OpenLP 3.1.8 (offizieller Quellcode)"
   git tag openlp-3.1.8
   ```
3. Auf `main` zusammenführen, Konflikte lösen, Version auf `3.1.8+gemeinde.1` setzen, testen:
   ```powershell
   git switch main
   git merge upstream
   ```
4. Wie oben ein Update veröffentlichen.
