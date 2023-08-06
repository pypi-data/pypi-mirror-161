# hoppr_cyclonedx_models

## Purpose
The `model-gen.sh` script pulls a user-specified release from the [CycloneDX SBOM Specification](https://github.com/CycloneDX) that operates under the SBOM guidelines.  It then utilizes the [datamodel code generator](https://koxudaxi.github.io/datamodel-code-generator/) to generate Pydantic models from the input SBOM schema file.  These Pydantic models are available as a public package in PyPI under `hoppr_cyclonedx_models`.
## Usage 
### Install `datamodel-code-generator`:
-----------------------------------------
`pip install datamodel-code-generator`

For further reference see the [documentation](https://koxudaxi.github.io/datamodel-code-generator/).

### Create your model:
-----------------------------------------
`./model-gen.sh x.y` 

Where x and y refer to the applicable major and minor revisons respectively.

* Example Usage: `./model-gen.sh 1.4`

To see all current releases visit [CycloneDX Specification Releases](https://github.com/CycloneDX/specification/releases)