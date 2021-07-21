# Detect Python dependencies

Scans through python files, collects all imports and filters out internal ones. Can be used to guess dependencies of projects, but every dependency should be manually examined, because of potential false positives like optional or fallback dependencies and dependencies only meant for specific python versions.

# Examples


# TODO

- [ ] handle `import a as b`
- [ ] filter out internal modules
