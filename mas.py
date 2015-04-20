"""
    MAC Address Spoof Configurator spoofs the MAC address on OS X machines and connects to defined network.  
    Copyright (C) 2015  Levi Muniz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse, getpass, os, random, subprocess, sys, time

def randomMAC():
	mac = [ 0x00, 0x16, 0x3e,
		random.randint(0x00, 0x7f),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff) ]
	return ':'.join(map(lambda x: "%02x" % x, mac))

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--interface", default="en0", help="set the interface to change the MAC address of (default=en0)")
parser.add_argument("-s", "--ssid", help="set the SSID to attempt to connect to after execution")
parser.add_argument("-p", "--password", action="store_true", help="prompt for password for the SSID you want to connect to (default = False)")
args = parser.parse_args()

isConnected = False
thePass = ""

if sys.platform != "darwin":
	sys.exit("Sorry, MAS is only written for the \"OS X\" platform!\nExiting....")

if os.geteuid() != 0:
    sys.exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting....")

if args.password and args.ssid:
	thePass = getpass.getpass("Wi-Fi Password: ")
elif args.password:
	print("Password input detected, but no SSID found. Ignoring....")


print("Restarting interface " + args.interface + "....")
	
try:
	os.system("sudo ifconfig  " + args.interface + " down")
except:
	pass
	
try:
	os.system("sudo ifconfig "  + args.interface + " up")
except:
	pass

print("Completed! Sleeping 3 to wait for " + args.interface + " to come online....")

time.sleep(3)

print("Assuming " + args.interface + " is online. Attempting to dissociate from network if connected.....")

try:
	os.system("sudo /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -z")
	print("Dissociated successfully.")
except:
	print("Could not dissociate. MAC spoof will NOT work while connected.\nAssuming you're already disconnected. Beginning to spoof MAC address....")

try:
	newMAC = randomMAC()
	print("New MAC address: " + str(newMAC))
	os.system("sudo ifconfig " + args.interface + " ether " + str(newMAC))
	print("Spoofing completed!")
except:
	print("Spoofing failed.")

print("Attempting to configure network to user-defined specifications (if any).....")

if args.ssid:
	try:
		os.system("networksetup -setairportnetwork " + args.interface + " " + args.ssid + " " + thePass)
		print("Connected to network successfully!\nAttempting to renew DHCP lease....")
		isConnected = True
	except:
		print("Could not connect to network! Bad SSID or password?")

	if isConnected == True:
		try:
			os.system("sudo ipconfig set " + args.interface + " BOOTP")
			time.sleep(1)
			os.system("sudo ipconfig set " + args.interface + " DHCP")
			print("Successfully renewed DHCP lease!")
		except:
			print("Could not get IP address automatically. Are you serving DHCP correctly?")

print("Completed. We hope you enjoyed your stay!\nExiting....")
