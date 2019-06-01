# MXIM download tool

## Usage

```sh
./mximdl.py -h
```

When installing packages, mximdl keeps a list of downloaded packages in `mximpkgs.json` which can later also be updated.

## How to get the URLs from the installer

First, you need to get the installer:
```sh
curl 'https://www.maximintegrated.com/bin/downloadpackage' \
    --data 'swpackageparameter=ARMCortexToolchain.exe&swpartnumber=SFW0001500A&%3Acq_csrf_token=undefined' \
    -o ARMCortexToolchain.exe
```

Then set up `mitmproxy` and run the installer with `wine`:
```sh
wine ARMCortexToolchain.exe
```

The installer presents you with a small button in the left bottom corner where you can set the
proxy information. Set this to the mitmproxy (defaults to 127.0.0.1:8080).
When this is set click next and then back again. This initially parses the repository information
and gives you a nice list of the different repositories in the settings page from before.
