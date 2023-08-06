<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[Contributors][contributors-url]
[Stargazers][stars-url]
[Issues][issues-url]
[License][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/AnomeGAP/seqslab-cli">
    <img src="https://static.wixstatic.com/media/f7a6a5_1ad70ed05af04d7eb45ee5e2df347a32~mv2_d_4266_4449_s_4_2.gif" alt="Logo" width="80" height="80">
  </a>

<h2 align="center">Atgenomix SeqsLab V3 platform CLI</h2>

  <p align="center">
    Command Line Interface application in the Atgenomix SeqsLab platform, a cloud-first and enterprise BioMed-IT infrastructure.
    <br />
    <a href="https://docs.atgenomix.com"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/AnomeGAP/seqslab-cli/issues">Report Bug</a>
    ·
    <a href="https://github.com/AnomeGAP/seqslab-cli/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#run-interactive-mode">Run interactive mode</a></li>
      </ul>
    </li>
    <li><a href="#develop">Develop</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project


SeqsLab CLI is the advanced user facing interface to interactively and automatically access SeqsLab cloud platform via
SeqsLab RESTful APIs. Complementary with the web-based SeqsLab Console, the command line application allows bioinformaticians
and investigators to easily build custom scripts and automate own workflows powered by the SeqsLab platform infrastructure
technologies.

Typical use cases:

* Build automated data production that uploads and downloads sequencing datasets to/from the SeqsLab Data Hub cloud storage.
* Submit workflow runs on demand via SeqsLab WES APIs and integrate with local downstream analysis.
* Use as audit log device to view platform use activities.

SeqsLab CLI shall be the standard framework to develop command toolkits and provide as the SeqsLab platform utility.

### Built With

SeqsLab CLI is built with the following major frameworks:

* [SeqsLab APIs](https://api.seqslab.net/)
* [Python-Nubia](https://github.com/facebookincubator/python-nubia)
* [MSAL Python](https://msal-python.readthedocs.io/en/latest/)
* [Azure SDK](https://github.com/Azure/azure-sdk)
* [aiohttp](https://docs.aiohttp.org/en/stable/index.html)

Security information protection is secured and built with a system keyring service:

* [Keyring](https://pypi.org/project/keyring/)

<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

These recommended [keyring](https://pypi.org/project/keyring/) backends are supported in this package:

* macOS [Keychain](https://en.wikipedia.org/wiki/Keychain_%28software%29)
* Freedesktop [Secret Service](http://standards.freedesktop.org/secret-service/) supports many DE including GNOME (
  requires [secretstorage](https://pypi.python.org/pypi/secretstorage))
* KDE4 & KDE5 [KWallet](https://en.wikipedia.org/wiki/KWallet) (
  requires [dbus](https://pypi.python.org/pypi/dbus-python))
* [Windows Credential Locker](https://docs.microsoft.com/en-us/windows/uwp/security/credential-locker)

#### MacOS

##### For MacOS devices, you should first install the following packages:

* [pkg-config](https://formulae.brew.sh/formula/pkg-config)
* [dbus](https://formulae.brew.sh/formula/dbus)
* [glib](https://formulae.brew.sh/formula/glib)

or

```bash
# install packages:
brew install dbus

brew install pkg-config 
brew install glib

```

The following is an example of how to list the things you need to use the software and how to install them.

* Using Keyring on headless Linux systems in a Docker container

  Check out [Keyring](https://pypi.org/project/keyring/) for information on how to use Keyring on a headless Linux system as well as in a Docker
  container.

* Python Version 3.8+
* Python virtual environment

  ```bash
  pip3 install seqslabcli
  ```

### Run interactive mode

* Display available commands
  ```bash
  seqslab> help
  ```

### Run non-interactive mode

The non-interactive mode works exactly like any traditional Linux-based command line utility.

### Authenticate with SeqsLab API

* Set platform backend to use when launching SeqsLab CLI. The default value is "azure".

  ```bash
  seqslab --backend azure
  ```

* Single command to sign in to SeqsLab API and obtain API tokens. By default, signin command uses device code flow for
  browserless system.

  ```bash
  auth signin
  ```

  Set `device-code` argument to True for device authorization grant flow. By default, signin uses the auth code flow.

  ```bash
  auth signin device-code=True
  ```

* Get API access token to interact with SeqsLab API apps in your commands.

  ```python
  from seqslab.auth.commands import Auth
  
  token = Auth.get_token()
  access = token.get("tokens").get("access")
  # use token in your request header, ex: Authorization: Bearer {access}
  attrs = token.get("attrs")
  # attrs is a dictionary containing the information about the signing-in user.
  ```

  `Auth.get_token()` will automatically refresh the access token if expired. When refresh token expires, the function
  returns None if users need to sign back in to SeqsLab API.

  The tokens are persistently cached in the system-supported secret service, such as Freedesktop Secret Service and
  macOS Keychain. As a result, the valid access token can be used across multiple CLI sessions.

<!-- ROADMAP -->

## Roadmap

See the [open issues](https://github.com/AnomeGAP/seqslab-cli/issues) for a list of proposed features (and known issues)
.



<!-- CONTRIBUTING -->

## Contributing

We don't currently open to the community for contribution, but will in the future.


<!-- LICENSE -->

## License

See `LICENSE` for more information.



<!-- CONTACT -->

## Contact

Allen Chang - [LinkedIn](https://www.linkedin.com/in/allen-chang/) - allen.chang@atgenomix.com

Project Link: [https://github.com/atgenomix](https://github.com/atgenomix)



<!-- ACKNOWLEDGEMENTS -->

## Acknowledgements

* [Facebook Incubator](https://github.com/facebookincubator)
* [Microsoft identity platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-v2-protocols)
* [GA4GH](https://www.ga4gh.org/)
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-url]: https://github.com/AnomeGAP/seqslab-cli/graphs/contributors

[stars-url]: https://github.com/AnomeGAP/seqslab-cli/stargazers

[issues-url]: https://github.com/AnomeGAP/seqslab-cli/issues

[license-url]: https://github.com/AnomeGAP/seqslab-cli/blob/main/LICENSE.txt

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555

[linkedin-url]: https://www.linkedin.com/company/atgenomix

[product-screenshot]: https://github.com/AnomeGAP/seqslab-cli/blob/main/Atgenomix%20SeqsLab%20V3.png
