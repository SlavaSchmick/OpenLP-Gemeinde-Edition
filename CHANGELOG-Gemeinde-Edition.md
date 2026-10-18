# Änderungen der OpenLP Gemeinde-Edition

Alle Versionen der Gemeinde-Edition, die neueste oben. Die Änderungen des offiziellen OpenLP stehen in `CHANGELOG.rst`.
Downloads: [Releases](https://github.com/SlavaSchmick/OpenLP-Gemeinde-Edition/releases)

## Noch nicht veröffentlicht

### Neu

- **Globales Tastenkürzel Strg+Alt+O:** holt OpenLP aus jedem anderen Programm in den Vordergrund (ein minimiertes
  Fenster wird wiederhergestellt). Änderbar unter *Einstellungen → Tastenkürzel konfigurieren… → „OpenLP in den
  Vordergrund holen“*.
- **Suche im Dialog „Tastenkürzel konfigurieren“:** filtert beim Tippen nach Aktion, Kategorie oder Tastenkürzel
  (z. B. „Lied“ oder „Strg+L“).
- **Liedsuche nach Varianten:** „d63“ findet alle Fassungen eines Liedes (D63A, D63B) als exakte Treffer oben,
  „d63a“ genau diese Fassung.

### Behoben

- **Projektoren mit PJLink Klasse 2** (z. B. Acer) verloren nach wenigen Sekunden die Verbindung: OpenLP fragte die
  Klasse-2-Befehle FILT und FREZ (und MVOL) mit dem Klasse-1-Präfix ab, worauf der Projektor nicht antwortet. Der
  Fehler steckt auch im offiziellen OpenLP.

## 3.1.7+gemeinde.3 – 15.10.2026

### Neu

- **Hilfe → Nach Updates suchen…**: prüft sofort, ob es eine neue Version gibt, und bietet sie zur Installation an –
  sonst kommt die Meldung, dass die neueste Version installiert ist.

### Geändert

- **Übersetzungen gründlich überarbeitet** (Deutsch, Russisch, Ukrainisch), Schwerpunkt Einheitlichkeit:
  - Standardknöpfe wie „Schließen“, „Abbrechen“, „Ja/Nein“ erscheinen jetzt in der gewählten Sprache (bisher englisch).
  - Texte, die trotz Übersetzung immer englisch blieben (Projektoren, Assistenten, Meldungen), werden jetzt übersetzt.
  - Einheitliche Begriffe und Anrede (Deutsch durchgehend „Sie“), Menüpfade in Hilfetexten passen zu den echten
    Menüs; zahlreiche Sinn- und Tippfehler behoben (z. B. vertauschte Einträge „Schwarz“/„Zurück“ im Russischen).
  - Neue deutsche Menünamen: *Einstellungen → Erweiterungen verwalten* und *→ OpenLP konfigurieren…*,
    *Extras → Liedprotokollierung → Protokollierung ein/aus*; Liedteil „Pre-Chorus“ heißt „Vorrefrain“.
- OpenLP prüft **bei jedem Start** auf ein Update (bisher nur einmal am Tag), damit ein neues Release sofort angeboten
  wird.

## 3.1.7+gemeinde.2 – 14.10.2026

### Neu

- **Liedstatistik „Meistgesungene Lieder“** (*Extras → Liedprotokollierung → Statistik anzeigen*): Tabelle aller gesungenen
  Lieder mit Platz, Nummer und Anzahl, das meistgesungene oben. Zeitraum (letzte 4 Wochen, 3 Monate, 12 Monate, dieses
  Jahr, gesamt, benutzerdefiniert), Liederbuch (D/R) und Suche (z. B. `d203`) wählbar; speichern als PDF oder CSV.
  Ein Lied zählt pro Tag einmal.

### Geändert

- Die **Liedprotokollierung ist von Anfang an eingeschaltet**. Auf Rechnern, auf denen sie bisher aus war, wird sie beim
  ersten Start nach dem Update einmalig eingeschaltet; danach bleibt die Wahl des Benutzers (F4) erhalten.

## 3.1.7+gemeinde.1 – 14.10.2026

Erste Ausgabe der Gemeinde-Edition, auf Grundlage von OpenLP 3.1.7.

### Neu

- **Live-Video:** neue Erweiterung für Kameras, HDMI-Capture und virtuelle Kameras (z. B. OBS) auf der Leinwand.
- **Audio-Ausgabe** für Live und Vorschau getrennt wählbar, z. B. Dante Via.
- **Bibel:** ganzes Kapitel ab dem gesuchten Vers, tolerante Eingabe (deutsch, russisch, ukrainisch), Enter = Vorschau,
  Umschalt+Enter = live mit Fokus in der Live-Liste, Strg+B; ein Vers steht immer ganz auf einer Folie, auch mit
  Vergleichstext.
- **Lieder:** Suche beim Tippen, Kennungen wie `r47`/`d203` mit exaktem Treffer oben, Enter/Umschalt+Enter, Strg+L.
- **Automatische Textgröße:** größte passende Schrift je Folie innerhalb einer Spanne im Design; Liedzeilen werden nicht
  umbrochen.
- **Sprachen:** Ukrainisch neu, Russisch vervollständigt.
- **Liederbücher** Deutsch (1310) und Russisch (800), bereinigt und im OpenLP-Format.
- **Updates** aus diesem GitHub-Repository statt von openlp.org; Download mit Prüfsumme und automatischer Installation.
- **Windows-Setup** mit VLC; ersetzt ein vorhandenes offizielles OpenLP.

### Behoben

- PowerPoint-Präsentationen lassen sich mit Microsoft 365 (Click-to-Run) öffnen.
- Leere Bibeln aus fehlgeschlagenen Importen werden aufgeräumt.

### Geändert

- Name „OpenLP Gemeinde-Edition“ im Fenstertitel und Hinweis auf die modifizierte Version im Info-Dialog.
