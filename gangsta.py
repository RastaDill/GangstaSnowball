#!/usr/bin/python
#  gangsta.py
#  
#  Copyright (C) 2015 Voznesensky (WeedMan) Michael <weedman@opmbx.org>
#
#  Gangsta Snowball for Gamiron #11
#
#  This file is path of Gangsta Snowball
#  
#  Gangsta Snowball is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  Gangsta Snowball is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with Gangsta Snowball; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

import game

def main():
	game.director.run(game.list_level[0])

if __name__ == '__main__':
	main()
