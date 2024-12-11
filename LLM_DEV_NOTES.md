# LLM Dev Notes

## Release-Prozess

1. **Changelog aktualisieren:**
    -   `CHANGELOG.md` mit den Änderungen der neuen Version aktualisieren.
    -   Für jede Änderung einen Eintrag unter der entsprechenden Kategorie (Added, Changed, Fixed, etc.) hinzufügen.
    -   Datum im Format `YYYY-MM-DD` angeben.
2. **Version erhöhen:**
    -   Versionsnummer in `pyproject.toml` und `plexsearch/__init__.py` erhöhen.
    -   Dabei Semantic Versioning beachten:
        -   `MAJOR.MINOR.PATCH`
        -   **MAJOR:** Inkompatible API-Änderungen (erst relevant ab Version 1.0.0).
        -   **MINOR:** Neue, abwärtskompatible Funktionalität.
        -   **PATCH:** Abwärtskompatible Bugfixes.
3. **Commit erstellen:**
    -   Änderungen mit einer aussagekräftigen Commit-Message committen, z.B. `build: Bump version to 0.2.0`.
4. **Poetry Build und Publish:**
    -   `poetry build` ausführen, um das Package zu bauen.
    -   `poetry publish` ausführen, um das Package auf PyPI zu veröffentlichen.
5. **Git Tag erstellen:**
    -   Annotiertes Tag erstellen: `git tag -a v0.2.0 -m "Release v0.2.0"`
    -   Tag pushen: `git push origin v0.2.0`

## Versionsnummerierung

-   In Zukunft bei größeren Änderungen die **MINOR**-Version erhöhen, nicht nur die **PATCH**-Version.
-   Die **MINOR**-Version hätte bereits für frühere Versionen erhöht werden sollen, in denen neue Features hinzugefügt wurden.
-   Beispiel: Der interaktive Modus hätte die Version auf `0.2.0` erhöhen sollen.

## Sonstiges

-   Diese Notizen dienen als Referenz für zukünftige Releases und Entwicklungsarbeiten.
-   Bitte beim nächsten Mal an diese Punkte denken.
-   Danke!
