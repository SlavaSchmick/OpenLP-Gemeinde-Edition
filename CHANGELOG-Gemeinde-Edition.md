# Änderungen der OpenLP Gemeinde-Edition

Alle Versionen der Gemeinde-Edition, die neueste oben. Die Änderungen des offiziellen OpenLP stehen in `CHANGELOG.rst`.
Downloads: [Releases](https://github.com/SlavaSchmick/OpenLP-Gemeinde-Edition/releases)

## Noch nicht veröffentlicht

### Geändert

- **Projektor-Steuerung übersichtlicher:** Unter dem Namen des Beamers steht sein Zustand im Klartext („Standby“,
  „Eingeschaltet“, „Eingeschaltet – abgedunkelt“, „Nicht verbunden – verbinde erneut …“). Die Bedienknöpfe stehen
  beschriftet in einer eigenen Zeile, und es werden nur die gezeigt, die gerade passen: „Einschalten“ oder „Standby“,
  „Abdunkeln“ oder „Bild zeigen“.
- Trennt der Beamer die Verbindung (z. B. im Standby), verbindet OpenLP sich selbst wieder, damit er sich jederzeit
  einschalten lässt. Wer von Hand trennt, bleibt getrennt.

### Behoben

- **Beamer (z. B. Acer) ließ sich nicht abdunkeln und nicht aus dem Standby einschalten:** Der Beamer hängt an seine
  Antworten ein unsichtbares NUL-Zeichen an. OpenLP verstand die Antworten dadurch nicht, kannte weder den
  Verschluss- noch den Stromzustand und ließ „Abdunkeln“ und „Einschalten“ gesperrt.

## 3.1.7+gemeinde.5 – 18.10.2026

### Behoben

- **Automatisches Update konnte OpenLP unbrauchbar hinterlassen:** Hatte sich OpenLP beim Update noch nicht beendet,
  brach das Setup mitten in der Installation ab – nachdem es die alten Programmdateien schon gelöscht hatte. OpenLP
  startete danach nicht mehr. Das Setup wartet jetzt, bis OpenLP beendet ist, und beendet ein hängendes OpenLP nach
  einer Minute selbst; gelöscht wird erst danach. Von Hand gestartet, bittet es darum, OpenLP zu schließen.
- Vor einem Update fragt OpenLP jetzt **vor** dem Start des Setups, ob ein geänderter Ablauf gespeichert werden soll
  (bei „Abbrechen“ wird nicht aktualisiert); danach schließt es ohne weitere Rückfragen.

## 3.1.7+gemeinde.4 – 18.10.2026

### Neu

- **Globales Tastenkürzel Strg+Alt+O:** holt OpenLP aus jedem anderen Programm in den Vordergrund (ein minimiertes
  Fenster wird wiederhergestellt). Änderbar unter *Einstellungen → Tastenkürzel konfigurieren… → „OpenLP in den
  Vordergrund holen“*.
- **Suche im Dialog „Tastenkürzel konfigurieren“:** filtert beim Tippen nach Aktion, Kategorie oder Tastenkürzel
  (z. B. „Lied“ oder „Strg+L“).
- **Liedsuche nach Varianten:** „d63“ findet alle Fassungen eines Liedes (D63A, D63B) als exakte Treffer oben,
  „d63a“ genau diese Fassung.
- **Neues deutsches Liederbuch:** das Gemeinde-Gesangbuch (698 Lieder, D1–D695, mit Varianten wie D63A/D63B) ersetzt
  das bisherige deutsche Liederbuch, jetzt mit Textautoren, Übersetzern, Copyright, Melodie und Bibelstellen. Es wird
  wegen urheberrechtlich geschützter Lieder nur intern weitergegeben; der öffentliche Download enthält nur noch das
  russische Liederbuch.

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
