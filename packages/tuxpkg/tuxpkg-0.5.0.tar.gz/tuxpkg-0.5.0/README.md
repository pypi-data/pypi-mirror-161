# tuxpkg - release automation tool for Python projects

## gitlab CI pipeline

How to use:

```yaml
include:
  - https://gitlab.com/Linaro/tuxpkg/raw/main/gitlab-ci-pipeline.yml
variables:
  # ... override variables here (see below)
```

Variables that can be overriden locally:

- `TUXPKG`: how to call tuxpkg. Default: `tuxpkg`.

The following protected variables need to be set in the CI/CD configuration:

- `TUXPKG_RELEASE_KEY`: a variable of type "file", containing an ascii-armored
  export of gnupg private key to sign the package repositories.
- `TUXPKG_RELEASE_KEYID`: the public gnupg key ID used to sign the package
  repositories.
- `FLIT_PASSWORD`: password to authenticate to PyPI with. Generate a
  project-specific token. `FLIT_USERNAME` will be automatically set to
  `__token__`.
