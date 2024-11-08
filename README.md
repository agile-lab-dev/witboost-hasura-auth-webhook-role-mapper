<br/>
<p align="center">
    <a href="https://www.witboost.com/">
        <img src="docs/img/witboost_logo.svg" alt="witboost" width=600 >
    </a>
</p>
<br/>

Designed by [Agile Lab](https://www.agilelab.it/), Witboost is a versatile platform that addresses a wide range of sophisticated data engineering challenges. It enables businesses to discover, enhance, and productize their data, fostering the creation of automated data platforms that adhere to the highest standards of data governance. Want to know more about Witboost? Check it out [here](https://www.witboost.com/) or [contact us!](https://witboost.com/contact-us)

This repository is part of our [Starter Kit](https://github.com/agile-lab-dev/witboost-starter-kit) meant to showcase Witboost's integration capabilities and provide a "batteries-included" product.

# Hasura Authentication Webhook and Role Mapper

- [Overview](#overview)
- [Building](#building)
- [Running](#running)
- [Configuring](#configuring)
- [Deploying](#deploying)
- [HLD](#hld)
- [API specification](hasura-authenticationwebhook-rolemapping-service/openapi-specification.yml)

## Overview

This Python microservice implements an Authentication Webhook and Role Mapping service for GraphQL Output Ports based on Hasura. It is used by the corresponding [Hasura Specific Provisioner](https://github.com/agile-lab-dev/witboost-hasura-specific-provisioner).

### Hasura

[Hasura](https://hasura.io/) is an open-source, real-time GraphQL engine that simplifies and accelerates API development for web and mobile applications. It connects to your data sources like databases or REST services and automatically generates a GraphQL API, making it easier to query and manipulate data. Hasura's real-time capabilities enable instant updates to clients when data changes, enhancing the responsiveness of applications. It's a popular tool for developers looking to streamline the process of building dynamic and interactive applications by providing a unified and efficient way to access, manage, and synchronize data.

### Software stack

This microservice is written in Python 3.11, using FastAPI for the HTTP layer. Project is built with Poetry and supports packaging as Wheel and Docker image, ideal for Kubernetes deployments (which is the preferred option).

### Repository structure

The Python project for the microservice is in the `hasura-authenticationwebhook-rolemapping-service` subdirectory; this is probably what you're interested in. It contains the code, the tests, the docs, etc.

The rest of the contents of the root of the repository are mostly support scripts and configuration files for the GitLab CI, gitignore, etc.

## Building

**Requirements:**

- Python 3.11
- Poetry

### Setup the Python environment

To set up a Python environment we use [Poetry](https://python-poetry.org/):
```
curl -sSL https://install.python-poetry.org | python3 -
```

> 📝 If you are on Windows, you probably want to use pipx instead:
> ```
> pipx install poetry
> ```

Once Poetry is installed and in your `$PATH`, you can execute the following:
```
poetry --version
```
If you see something like `Poetry (version x.x.x)`, your install is ready to use!

Install the dependencies defined in `hasura-authenticationwebhook-rolemapping-service/pyproject.toml`:
```
cd hasura-authenticationwebhook-rolemapping-service
poetry install
```
Poetry automatically creates a Python virtual environment in which the packages are installed; make sure to read the next section to enable it.

> 📝 If you are on Windows, you may get an error about Visual C++ missing; follow the instructions provided by Poetry to fix it.

### Use the Python environment

You just need to enable the Python virtual environment (venv) generated by Poetry:
```
source $(poetry env info --path)/bin/activate
```
As with any Python venv, your shell prompt will change to reflect the active venv.

You can also use:
```
poetry shell
```
Which spawns a subshell in the virtual environment; it is slighly different than the command above as this is not a login shell, hence your shell's profile file will likely be ignored.

### Setup the pre-commit hooks

Simply run:
```
pre-commit install
```
In case you need to commit and skip the pre-commit checks (eg, to push WIP code, or to test that the CI catches formatting issues), you can pass the `--no-verify` flag to `git commit`.

### Setup PyCharm

The recommended IDE is PyCharm, though other ones should work just fine.

In order to import the project, use the standard "Open..." dialog and point PyCharm to the `hasura-authenticationwebhook-rolemapping-service` subdirectory, *not the repository root*. This ensures that PyCharm correctly identifies this as a Poetry project and prompts you to set it up as such.

### Docker build

The Docker image can be built with:

```
docker build .
```

More details can be found [here](hasura-authenticationwebhook-rolemapping-service/docs/docker.md).

### Additional notes

**Application version:** the version for the project is automatically computed using information gathered from Git, using branch name and tags. Unless you are on a release branch `1.2.x` or a tag `v1.2.3` it will end up being `0.0.0`. You can follow this branch/tag convention or update the version computation to match your preferred strategy.

**CI/CD:** the pipeline is based on GitLab CI as that's what we use internally. It's configured by the `.gitlab-ci.yaml` file in the root of the repository. You can use that as a starting point for your customizations.

## Running

To run the server locally, use:

```bash
cd hasura-authenticationwebhook-rolemapping-service
source $(poetry env info --path)/bin/activate # only needed if venv is not already enabled
uvicorn src.main:app --host 127.0.0.1 --port 8092
```

By default, the server binds to port 8092 on localhost. After it's up and running you can make provisioning requests to this address. You can also check the API documentation served [here](http://127.0.0.1:8092/docs).

## Configuring

Application configurations are handled with environment variables:

| Environment Variable             | Description                                                                        |
|----------------------------------|------------------------------------------------------------------------------------|
| GRAPHQL_URL                      | URL of the Hasura instance                                                         |
 | GRAPHQL_ROLE                     | Role to use when performing actions on Hasura                                      |
| GRAPHQL_ADMIN_SECRET             | Admin secret for the Hasura instance                                               |          
| JWKS_URL                         | JWKS URL, eg "https://login.microsoftonline.com/common/discovery/v2.0/keys"        |
 | JWT_AUDIENCE                     | JWT audience, eg "https://management.core.windows.net/"                            |
 | JWT_ALGORITHMS                   | JWT algorithms, eg `[\"RS256\", \"RS512\"]                                         |
 | JWT_OPTIONS                      | JWT options, eg `"{\"verify_exp\": true,\"require\": [\"exp\", \"iat\"]}"`         |
 | AZURE_SCOPES                     | For Azure AD JWTs; the JWT scopes, eg `[\"https://graph.microsoft.com/.default\"]` |
| AZURE_TENANT_ID                  | For Azure AD JWTs; the tenant id                                                   |                
| AZURE_CLIENT_ID                  | For Azure AD JWTs; the client id                                                   |              
| AZURE_CLIENT_SECRET              | For Azure AD JWTs; the client secret                                               |
 | AUTHORIZATION_HEADER_FIELD_NAMES | List of headers fields to use, eg: `"[\"authorization\", \"Authorization\"]"`      |
 | ROLEMAPPING_TABLE_SCHEMA         | Schema for the role mapping table on the database, eg "rolemapping"                |

Those environment variables are already templated in the Helm chart (see below). Customize them according to your needs.

Logging is handled with the native Python logging module. The Helm chart provides a default [logging.yaml](helm/files/logging.yaml) that you can override. Check out the [Helm docs](helm/README.md) for details.

To configure the `OpenTelemetry framework` refer to the [OpenTelemetry Setup](hasura-authenticationwebhook-rolemapping-service/docs/opentelemetry.md).

## Deploying

This microservice is meant to be deployed to a Kubernetes cluster with the included Helm chart and the scripts that can be found in the `helm` subdirectory. You can find more details [here](helm/README.md).

## HLD

Refer to the HLD for the corresponding Specific Provisioner [here](https://github.com/agile-lab-dev/witboost-hasura-specific-provisioner/docs/HLD.md).

## License

This project is available under the [Apache License, Version 2.0](https://opensource.org/licenses/Apache-2.0); see [LICENSE](LICENSE) for full details.

## About Witboost

[Witboost](https://witboost.com/) is a cutting-edge Data Experience platform, that streamlines complex data projects across various platforms, enabling seamless data production and consumption. This unified approach empowers you to fully utilize your data without platform-specific hurdles, fostering smoother collaboration across teams.

It seamlessly blends business-relevant information, data governance processes, and IT delivery, ensuring technically sound data projects aligned with strategic objectives. Witboost facilitates data-driven decision-making while maintaining data security, ethics, and regulatory compliance.

Moreover, Witboost maximizes data potential through automation, freeing resources for strategic initiatives. Apply your data for growth, innovation and competitive advantage.

[Contact us](https://witboost.com/contact-us) or follow us on:

- [LinkedIn](https://www.linkedin.com/showcase/witboost/)
- [YouTube](https://www.youtube.com/@witboost-platform)

