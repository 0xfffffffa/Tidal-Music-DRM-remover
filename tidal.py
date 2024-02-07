#!/usr/bin/python


from tidalclient import tidal

tidal = tidal()
tidal.login("email","password")
artist = raw_input("[!] Which artist would you like to search for? ").encode("ascii","ignore")
tidal.search(artist)

