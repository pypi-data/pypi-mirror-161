# A ChaosToolkit package that lists some useful utility actions/probes/controls


## Probes

### check_site_content
This probe can be used to check if the content from a http get request matches a pattern.

#### Usage

      {
        "type": "probe",
        "name": "Check there are no errors...",
        "provider": {
          "arguments": {
            "url": "...",
            "pattern": "any pattern accepted by re...",
            "timeout": x # timeout in seconds, not mandatory...
          },
          "func": "check_site_content",
          "module": "chaostoolkit_utils.probes",
          "type": "python"
        },


