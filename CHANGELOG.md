# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-12-22

### Added
- Added interactive mode for multi-turn conversations
- Added markdown file output for interactive mode
- Added conversation context management
- Refactored code into modules for API interaction, configuration, and context management
- Improved terminal output handling, including screen clearing
- Improved update checker with better feedback
- Added extensive debug logging
- Added many new tests
- Improved error handling with specific exceptions

### Changed
- Updated interactive mode prompt prefix to ">"

## [0.2.2] - 2025-01-15

### Added
- Enabled citations by default (use --no-citations to disable)

### Fixed
- Fixed test_log_conversation_file_write_error to match stderr implementation
- Improved error handling in log_conversation function

## [0.2.1] - 2024-12-22

### Fixed
- Correctly handle log file errors to prevent program termination


## [0.1.17] - 2024-12-11

### Changed
- Updated interactive mode prompt prefix to ">"

## [0.1.15] - 2024-12-11

### Added
- Fixed issue with update checker not properly handling mock responses.
- Improved error handling and output capture in update process.

### Changed
- Fixed flake8 code style issues in core.py
- Improved code formatting and readability
- Removed unused imports and variables
- Fixed line length issues
- Added proper spacing between functions

## [0.1.13] - 2024-12-08

### Fixed
- Made spinner transient while keeping streamed output visible
- Improved terminal output handling for search results

## [0.1.12] - 2024-12-08

### Fixed
- Improved visibility of searching animation in all terminal environments

## [0.1.11] - 2024-12-08

### Added
- Progress indicator for package updates
- More detailed API error messages for common error codes
- Test coverage for error handling scenarios

### Changed
- Update message now indicates new version will be used on next execution
- Program continues execution after update instead of exiting

## [0.1.10] - 2024-12-08

### Added
- Improved error handling for API responses
- Progress indicator during package updates
- Tests for continuous execution after updates

### Changed
- Update process now continues with search after updating
- Better user feedback during update process

## [0.1.9] and earlier

- Initial releases with basic functionality
- Search capabilities using Perplexity API
- Command-line interface
- Automatic update checking
