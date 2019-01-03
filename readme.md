# Development Charities Data Explorer

Data tool to help international development NGOs to navigate charity commission data.

## Project partners:

- [The Sheffield Institute for International Development](http://siid.group.shef.ac.uk/)
- [David Kane](https://dkane.net/)
- [CharityBase](https://charitybase.uk/)

## About this app

This app uses [Dash by plotly](https://dash.plot.ly/) to fetch and display data from the
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
```
