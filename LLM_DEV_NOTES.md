# LLM Dev Notes

These notes are for you, the LLM, to help guide development and releases.

## Release Process

1. **Update Changelog:**
    -   Update `CHANGELOG.md` with changes in the new version.
    -   Add an entry for each change under the appropriate category (Added, Changed, Fixed, etc.).
    -   Use the date format `YYYY-MM-DD`.
2. **Increment Version:**
    -   Increment the version number in `pyproject.toml` and `plexsearch/__init__.py`.
    -   Follow Semantic Versioning:
        -   `MAJOR.MINOR.PATCH`
        -   **MAJOR:** Incompatible API changes (only relevant after version 1.0.0).
        -   **MINOR:** New, backwards-compatible functionality.
        -   **PATCH:** Backwards-compatible bug fixes.
3. **Create Commit:**
    -   Commit changes with a descriptive message, e.g., `build: Bump version to 0.2.0`.
4. **Poetry Build and Publish:**
    -   Run `poetry build` to build the package.
    -   Run `poetry publish` to publish the package to PyPI.
5. **Create Git Tag:**
    -   Create an annotated tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
    -   Push the tag: `git push origin v0.2.0`

## Versioning

-   In the future, increment the **MINOR** version for significant changes, not just the **PATCH** version.
-   The **MINOR** version should have been incremented for previous versions that added new features.
-   Example: The addition of interactive mode should have bumped the version to `0.2.0`.
-   The current version is `0.1.16`.
-   The next version, which will include the interactive mode, should be `0.2.0`.

## Context from Previous Interactions

-   We've been working on a Python tool called `plexsearch` that uses the Perplexity API.
-   We've implemented an interactive mode.
-   We've discussed and addressed a bug related to alternating user/assistant roles in the interactive mode, but this fix was removed from this release because it was related to the new interactive mode feature.
-   We've gone through a release process, including updating the changelog, bumping the version to `0.1.16`, building and publishing the package, and creating a Git tag.
-   The user committed the final changes for the `0.1.16` release with git hash `cd852b2` and commit message "docs: Remove bugfix from changelog for v0.1.16".
-   The user committed the changes for LLM_DEV_NOTES with git hash `9809833` and commit message "docs: Add developer notes for release process and versioning".
-   The user ran `poetry build` and `poetry publish` for version `0.1.16`.
-   The user ran `git tag -a v0.1.16 -m "Release v0.1.16"` and `git push origin v0.1.16` to create and push the Git tag for version `0.1.16`.

## Important Notes

-   These notes are intended to provide context and guidance for future development.
-   Remember to consider these points during the next release cycle.
-   The user will likely ask you to help with the next release, so keep this information in mind.
