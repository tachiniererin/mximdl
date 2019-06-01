#!/usr/bin/env python3

import argparse
import json
import shutil
import urllib.request
import xml.etree.ElementTree as ET


current_pkgs = {}
repos = []
pkgs = {}


def update_pkgs():
    global current_pkgs, pkgs
    try:
        with open('mximpkgs.json') as f:
            current_pkgs = json.load(f)
    except EnvironmentError:
        pass

    if len(current_pkgs) == 0:
        print("No mximpkgs.json file found, download some packages first")
        exit(1)

    init_repo()

    updated = False

    for ident, pkg in current_pkgs.items():
        version = pkg['version']
        if version < pkgs[ident]['version']:
            updated = True
            install_pkg([ident], initialised=True)

    if not updated:
        print('All packages up-to-date')


# download and install the package
def install_pkg(names, initialised=False):
    global current_pkgs, pkgs
    if not initialised:
        init_repo()
        try:
            with open('mximpkgs.json') as f:
                current_pkgs = json.load(f)
        except EnvironmentError:
            pass  # we'll write one if we can't load it

    for ident in names:
        pkg = pkgs[ident]
        version = pkg['version']
        print('Downloading {} {}'.format(ident, version))
        url = '{}/{}/{}{}'.format(pkg['repo'], ident, version, pkg['archive'])
        with urllib.request.urlopen(url) as u:
            fn = '{}_{}_{}'.format(pkg['name'], version, pkg['archive'])
            with open(fn, 'w+b') as f:
                shutil.copyfileobj(u, f)
                current_pkgs[ident] = pkg  # add the downloaded pkg to our list

    # write our updated list of packages
    if len(current_pkgs) > 0:
        with open('mximpkgs.json', 'w+') as f:
            json.dump(current_pkgs, f, indent=4, sort_keys=True)


def list_pkgs():
    global pkgs
    init_repo()
    fmt_str = '{:<40}{:<10}{:<13}{}'
    print(fmt_str.format(
        'Name', 'Version', 'Released', 'Package identifier'))
    for ident, p in pkgs.items():
        print(fmt_str.format(
            p['name'], p['version'], p['released'], ident))


def init_repo():
    global pkgs
    print('Loading repositories...')
    # get available repositories
    with urllib.request.urlopen('http://www.mxim.net/product/dist/Updates.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        for child in root.find('RepositoryUpdate'):
            repos.append(child.attrib['url'])

    # get packages in repositories
    for repo in repos:
        with urllib.request.urlopen(repo + '/Updates.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            for child in root.findall('PackageUpdate'):
                name = child.find('DisplayName').text.replace(
                    ' (REQUIRES extra license agreement)', '')
                ident = child.find('Name').text
                released = child.find('ReleaseDate').text
                version = child.find('Version').text
                sha1 = child.find('SHA1').text
                # from the name, this could potentially mean that it can
                # reference more than one archive, but it hasn't been seen yet.
                e = child.find('DownloadableArchives')
                ar = e.text if e is not None else ''

                pkgs[ident] = {
                    'name': name, 'released': released,
                    'version': version, 'sha1': sha1,
                    'repo': repo, 'archive': ar,
                }


parser = argparse.ArgumentParser(description='Maxim MCU SDK Downloader')
group = parser.add_mutually_exclusive_group()

group.add_argument(
    '-l', '--list', help="list available packages", action="store_true")
group.add_argument(
    '-u', '--update', help="update installed packages", action="store_true")
group.add_argument('-i', '--install',
                   help="install package(s)", nargs='+', metavar='pkg')

args = parser.parse_args()

if args.list:
    list_pkgs()
elif args.update:
    update_pkgs()
elif args.install:
    install_pkg(args.install)
