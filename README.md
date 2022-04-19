# Getting Started

Rename `exmaple.configurations.py` to `configurations.py`.  Then change the settings within `configurations.py` to meet your needs.

You may need to install the `requests` and `dnspython` modules in your environment to get this script to work.
```
pip3 install requests
pip3 install dnspython
```


# Overview

This application is meant to automatically update the IP address for an `A` and `AAAA` record maintained by name.com.

## How it works

The application checks your current public IP address which is used by the host that's running this application.  It does this by using the API of a "what's my IP" provider.  By default `https://api.myip.com` is used.

Once your public IP address is found, this application does a `NSLOOKUP` on the configured FQDN.  If the IP address from the lookup is different from the current public IP, the application then communicates with name.com API and updates the `A` or `AAAA` record (whichever is relevant).

## TODO

1) Configure proper logging to file or console.  Currently uses `print()` function.
2) Implement the ability to use CLI arguments instead of a `configurations.py` file.
