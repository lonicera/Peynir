#!/usr/bin/env python3
import os
import subprocess


def main():
	if not os.geteuid()==0:
		sys.exit("\nYou must be root to run this application, please use sudo and try again.\n")
	depend = "pacman -S --noconfirm python"
	subprocess.Popen(depend, shell=True).wait()
	if not os.path.exists('/var/cache/peynir'):
		os.mkdir('/var/cache/peynir')
	if not os.path.exists('/var/cache/peynir/packages'):
		os.mkdir('/var/cache/peynir/packages')
	os.system('cp peynir.py /usr/bin')
	print("Peynir is installed")

if __name__ == "__main__":
    main()
