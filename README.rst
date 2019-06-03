Simple library that validates the file and its contents.

Please note, one should keep a master Non-Conformance Rule sheet for each implementation. This document must be updated accordingly when code changes are applied.

During integration, follow directory structure as recommended. Refer tests/example directory to see framework integration.
- main.py # module name can be changed. Essentially this is where validation getters and runners sit.
- validator
  - Custom_Validator class (Optional)
  - Additional utils for custom rules (Optional)
  - Custom rules (Optional)
  - Custom messages (Optional)
- schema
  - Custom_FeatureSchema class that register custom rules
- reporter
  - Custom_Report class (Optional)
  - Custom_Writer class (Optional)
- reader
  - Custom_Reader class (Optional)
  - Custom messages (Optional)
- helper
  - Additional helper utilities (Optional)
- Additional exception classes (Optional)
- Custom messages and mapping
- Custom models (Optional)