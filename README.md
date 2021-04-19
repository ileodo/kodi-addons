# Introduction
This Kodi addons repo provides some personal use addons. Some of the addons are inspired by [xbmc-addons-chinese](https://github.com/taxigps/xbmc-addons-chinese)

# Installation
**All the addons here are in python3, hence only Kodi 19+ is supported.**

Please download [repository.ileodo-kodi-addons-0.0.1.zip](https://github.com/ileodo/kodi-addons/raw/main/dest/repository.ileodo-kodi-addons/repository.ileodo-kodi-addons-0.0.1.zip), and choose "install from zip" in Kodi.


# Addons

## repository.ileodo-kodi-addons
This addon repo

## service.subtitles.a4k
Search and download subtitles from [www.a4k.net](www.a4k.net) 
- Support .zip/.rar file
- Recusively searching subtitle files in .zip/.rar file
- Show file extension as prefix in the result list

> For developers:  
> This addon provided an extensible framework, so you can easily develop new subtitle addon. 
> Please check [base_adapter.py](https://github.com/ileodo/kodi-addons/blob/main/service.subtitles.a4k/base_adapter.py) for more details.
> I'm considering to make this framework as an seperate module.


# Issue
Please enter an issue if you enter any problem.

# Contribution
This project is open for contribution, please open PR if you'd like to.

Check list before raising PR:
- has an descriptive commit message
- had run `make release` and `make publish`
- has minimal unittest

