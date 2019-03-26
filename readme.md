# Development Charities Data Explorer

Data tool to help international development NGOs to navigate charity commission data.

[![CircleCI](https://circleci.com/gh/drkane/ngo-explorer.svg?style=shield)](https://circleci.com/gh/drkane/ngo-explorer)
[![Github Issues](https://img.shields.io/github/issues/drkane/ngo-explorer.svg)](https://github.com/drkane/ngo-explorer/issues)
[![Licence](https://img.shields.io/github/last-commit/drkane/ngo-explorer.svg)](https://github.com/drkane/ngo-explorer)

## Project partners:

- [Global Development Institute (GDI, University of Manchester)](http://siid.group.shef.ac.uk/)
- [Sheffield Institute for International Development (SIID, University of Sheffield)](https://www.gdi.manchester.ac.uk/)
- [David Kane](https://dkane.net/)
- [CharityBase](https://charitybase.uk/)

## About this app

This app uses [Flask](http://flask.pocoo.org/) to fetch and display data from the
[CharityBase API](https://charity-base.github.io/charity-base-docs).

## Installing app using dokku

On dokku server:

```bash
# create app
dokku apps:create ngo-explorer

# enable domains
dokku domains:enable ngo-explorer
dokku domains:add ngo-explorer example.com

# letsencrypt
dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
dokku config:set --no-restart ngo-explorer DOKKU_LETSENCRYPT_EMAIL=your@email.tld
dokku letsencrypt ngo-explorer

# add charitybase api key
dokku config:set ngo-explorer CHARITYBASE_API_KEY=123456789

# setup volume storage
mkdir -p /var/lib/dokku/data/storage/ngo-explorer
chown -R dokku:dokku /var/lib/dokku/data/storage/ngo-explorer
chown -R 32767:32767 /var/lib/dokku/data/storage/ngo-explorer
dokku storage:mount ngo-explorer /var/lib/dokku/data/storage/ngo-explorer:/app/storage
dokku config:set --no-restart ngo-explorer DATA_CONTAINER=/app/storage
```

## Styles

A custom build of tachyons is maintained in <https://github.com/drkane/ngo-explorer-tachyons>.

Colours used include:

 - yellow: `#f9af42` ![](https://dummyimage.com/50x20/f9b042/000&text=+)    
 - dark-green: `#043942` ![](https://dummyimage.com/50x20/043942/000&text=+) 
 - green: `#237756` ![](https://dummyimage.com/50x20/237756/000&text=+) 
 - light-green: `#0ca777` ![](https://dummyimage.com/50x20/0ca777/000&text=+) 

 ## Translations

Update translations if base text changes 

```
pybabel extract -F babel.cfg --copyright-holder="NGO Explorer" --project="NGO Explorer" --msgid-bugs-address="email@example.net" -o messages.pot .
pybabel update -i messages.pot -d translations
```

Create a file for translations

```
pybabel init -i messages.pot -d translations -l de
```

Compile the new transations

```
pybabel compile -d translations
```

## Run tests

```
python -m pytest -p no:warnings
```