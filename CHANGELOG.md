# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Compose/Helm WES, TES, and oauth2-proxy images are version-pinned (Sapporo 2.2.6, Funnel 0.10.1, oauth2-proxy v7.15.4). `:latest` is not a pin.

### Added

- `lab-stack grade-helixtest`: grade a HelixTest OverallReport JSON. Skip is not a pass; `all_passed` is true only when at least one non-skipped test ran and none failed.

### Changed

- Weekly HelixTest Phase 1 / Phase 2 (WES) schedules paused. `workflow_dispatch` remains.

### Fixed

- HelixTest Phase 1/2 no longer `exit 0` after a real Fail. The job now uses `lab-stack grade-helixtest`. Skip-only JSON is `verdict=not_evaluated` / `all_passed=false`.
- HelixTest wait steps fail the job if Beacon or Sapporo never become ready, instead of skipping HelixTest and staying green.

### Security
