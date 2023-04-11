# iLeoDo Kodi Addons
[![Python application](https://github.com/ileodo/kodi-addons/actions/workflows/python-app.yml/badge.svg)](https://github.com/ileodo/kodi-addons/actions/workflows/python-app.yml)
![Python version](https://img.shields.io/badge/Python-3.10-blue?logo=python)

![Kodi Nexus](https://img.shields.io/badge/Kodi-Nexus-blue?logo=kodi)
![Kodi Matrix](https://img.shields.io/badge/Kodi-Matrix-blue?logo=kodi)

<a href="https://www.buymeacoffee.com/Ileodo" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

## Introduction
This Kodi addons repo provides some personal use addons. Some of the addons are inspired by [xbmc-addons-chinese](https://github.com/taxigps/xbmc-addons-chinese)

## Installation
**All the addons here are in python3, hence only Kodi 19+ is supported.**

Please download from [Release](https://github.com/ileodo/kodi-addons/releases) page, and choose "install from zip" in Kodi.


## Addons

### repository.ileodo-kodi-addons
This addon repository.

### service.subtitles.a4k
Search and download subtitles from [www.a4k.net](www.a4k.net) 
- Support .zip/.rar file
- Recusively searching subtitle files in .zip/.rar file
- Show file extension as prefix in the result list

> For developers:  
> This addon provided an extensible framework, so you can easily develop new subtitle addon. 
> Please check [base_adapter.py](https://github.com/ileodo/kodi-addons/blob/main/service.subtitles.a4k/base_adapter.py) for more details.
> I'm considering to make this framework as an seperate module.


## Issue
Please enter an issue if you enter any problem.

## Contribution
This project is open for contribution, please open PR if you'd like to.

Check list before raising PR:
- has an descriptive commit message
- had run `make release` and `make publish`
- has minimal unittest

