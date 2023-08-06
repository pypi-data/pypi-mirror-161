#this is pyckaged, a package manager made with python

import os
import sys
import colorama as clr
import requests as rq
import pyfiglet as fig
import platform as plt
#this is terminal-only

def main():
    fig.print_figlet("Pyckage'd")
    try:
        command = sys.argv[1]
    except IndexError:
        print(clr.Fore.RED + "Error: No command specified.")
        sys.exit(1)

    homedir = os.path.expanduser("~")

    #check if there is a ./pyckaged-packages directory
    if not os.path.exists(homedir + "/.pyckaged-packages"):
        #if not, create it
        os.system("mkdir " + homedir + "/.pyckaged-packages")
    
    if command == "install":
        #make sure there is an argument for the package name
        if len(sys.argv) < 3:
            print(clr.Fore.RED + "Error: No package name specified")
            clr.Fore.RED
            sys.exit(1)
        else:
            package = sys.argv[2]
            #make sure the package name is valid
            if package.find(" ") != -1:
                print(clr.Fore.RED + "Error: package name cannot contain spaces")
                sys.exit(1)
            elif package.find(".") != -1:
                print(clr.Fore.RED + "Error: package name cannot contain periods")
                sys.exit(1)
            elif package.find("/") != -1:
                print(clr.Fore.RED + "Error: package name cannot contain slashes")
                sys.exit(1)
            elif package.find("\\") != -1:
                print(clr.Fore.RED + "Error: package name cannot contain backslashes")
                sys.exit(1)
            elif package.find("|") != -1:
                print(clr.Fore.RED + "Error: package name cannot contain pipes")
                sys.exit(1)
            elif package.find("`") != -1:
                print(clr.Fore.RED + "Error: package name cannot contain backticks")
                sys.exit(1)
            elif package.find("~") != -1:
                print(clr.Fore.RED + "Error: package name cannot contain tildes")
                sys.exit(1)
            elif package.find("!") != -1:
                print(clr.Fore.RED + "Error: package name cannot contain exclamation points")
                sys.exit(1)
            #check the repository of package repositories
            if not os.path.exists(homedir + "/.pyckaged-repositories.txt"):
                #download the repository file
                #we can use requests to download the file
                repotext = rq.get("https://raw.githubusercontent.com/lewolfyt/pyckaged/master/pyckaged-repositories.txt")
                #save it to the user's home directory
                open(homedir + "/.pyckaged-repositories.txt", "x")
                #write the text to the file
                with open(homedir + "/.pyckaged-repositories.txt", "w") as f:
                    f.write(repotext.text)
            repos = open(homedir + "/.pyckaged-repositories.txt", "r")
            #check if the package is in the repository
            for line in repos:
                if line.find(package) != -1:
                    #get the repository
                    #file format: package name | repository url
                
                    #get the repository url
                    repo = line.split("|")[1]
                    #get the package name
                    name = line.split("|")[0]

                    #check if the package is already installed
                    if os.path.exists(homedir + "/.pyckaged-installed.txt"):
                        #check if the package is already installed
                        installed = open(homedir + "/.pyckaged-installed.txt", "r")
                        for line in installed:
                            if line.find(name) != -1:
                                print("Error: package already installed")
                                sys.exit(1)
                        else:
                            #create the installed file
                            open(homedir + "/.pyckaged-installed.txt", "x")
                            #write the package name to the file
                            with open(homedir + "/.pyckaged-installed.txt", "a") as f:
                                f.write(name)
                    #install the package
                    #if a package supports pyckaged it will have a pyckaged.py file
                    #clone the repository
                    reponame = name.split("/")[-1]
                    os.system("git clone " + repo + " " + homedir + "/.pyckaged-cache/" + reponame)
                    os.system("cd " + homedir +"/.pyckaged-cache/" + name + "/")
                    try:
                        os.system("python3 ~/.pyckaged-cache/"+reponame+"/pyckagedsetup.py")
                    except:
                       os.system("python ~/.pyckaged-cache/"+reponame+"/pyckagedsetup.py")
                    #add the package to the installed file
                    installed = open(homedir + "/.pyckaged-installed.txt", "a")
                    installed.write(name + "\n")
                    #print the package name
                    print(clr.Fore.LIGHTGREEN_EX + "Installed " + name + " successfully!")
                    #close the install file
                    installed.close()
                    #close the repositories file
                    repos.close()
                    #close the package file
                    sys.exit(0)
                else:
                    print(clr.Fore.RED + "Error: Package not found")
                    #close the repositories file
                    repos.close()
                    #close the package file
                    sys.exit(1)
    elif command == "pipinstall":
        try:
            package = sys.argv[2]
        except IndexError:
            print(clr.Fore.RED + "Error: No package name specified")
            sys.exit(1)
        try:
            os.system("pip install " + package)
        except:
            os.system("pip3 install " + package)
        else:
            print(clr.Fore.LIGHTCYAN_EX + "Installed " + package + " successfully!")
    elif command == "extpac":
        #this means it will use a different package manager
        try:
            pacman = sys.argv[2]
        except:
            print(clr.Fore.RED + "Error: No package manager specified")
            sys.exit(1)
        try:
            extpackage = sys.argv[3]
        except:
            print(clr.Fore.RED + "Error: No package name specified")
            sys.exit(1)
        if pacman == "pacman":
            if plt.system() == "Linux":
                #is pacman installed?
                if os.path.exists("/usr/bin/pacman"):
                    #install the package
                    os.system("pacman -Syu " + extpackage)
                else:
                    print(clr.Fore.RED + "Error: pacman is not installed")
                    sys.exit(1)
            else:
                print(clr.Fore.RED + "Error: pacman is not supported on this platform")
                sys.exit(1)
        elif pacman == "apt":
            if plt.system() == "Linux":
                os.system("apt-get update && apt-get install " + extpackage)
            else:
                print(clr.Fore.RED + "Error: apt is not supported on this platform")
                sys.exit(1)
        elif pacman == "yum":
            if plt.system() == "Linux":
                #is yum installed?
                if os.path.exists("/usr/bin/yum"):
                    os.system("yum install " + extpackage)
                else:
                    print(clr.Fore.RED + "Error: yum is not installed")
                    sys.exit(1)
            else:
                print(clr.Fore.RED + "Error: yum is not supported on this platform")
                sys.exit(1)
        elif pacman == "dnf":
            if plt.system() == "Linux":
                #check if it is installed
                if os.path.exists("/usr/bin/dnf"):
                    os.system("dnf install " + extpackage)
                else:
                    print(clr.Fore.RED + "Error: dnf is not installed")
                    sys.exit(1)
            else:
                print(clr.Fore.RED + "Error: dnf is not supported on this platform")
                sys.exit(1)
        elif pacman == "brew":
            if plt.system() == "Darwin" or plt.system() == "Linux":
                #check if brew is installed
                if not os.path.exists("/usr/local/bin/brew"):
                    print(clr.Fore.RED + "Error: brew is not installed")
                    sys.exit(1)
                else:
                    os.system("brew install " + extpackage)
            else:
                print(clr.Fore.RED + "Error: brew is not supported on this platform")
                sys.exit(1)
        elif pacman == "port":
            if plt.system() == "Darwin":
                #check if port is installed
                if os.path.exists("/opt/local/bin/port"):
                    os.system("port install " + extpackage)
                else:
                    print(clr.Fore.RED + "Error: port is not installed")
                    sys.exit(1)
            else:
                print(clr.Fore.RED + "Error: port is not supported on this platform")
                sys.exit(1)
        elif pacman == "emerge":
            if plt.system() == "Linux":
                #check if emerge is installed
                if os.path.exists("/usr/bin/emerge"):
                    os.system("emerge " + extpackage)
                else:
                    print(clr.Fore.RED + "Error: emerge is not installed")
                    sys.exit(1)
            else:
                print(clr.Fore.RED + "Error: emerge is not supported on this platform")
                sys.exit(1)
        else:
            print(clr.Fore.RED + "Error: Package manager not supported")
            sys.exit(1)
    elif command == "help":
        print(clr.Fore.LIGHTGREEN_EX + "Pyckage'd Help")
        print("Pyckage'd is a package manager made with python")
        print("Usage: pyckaged <command> <package>")
        print("Commands:")
        print("Install: Install a package")
        print("Update: Update all packages (Not yet implemented)")
        print("Pipinstall: Install a package using pip")
        print("Pipupdate: Update all packages using pip")
        print("Extpac: Install a package via another package manager")
        print("Extupdate: Update all packages via another package manager")
        print("Help: Show this help")
    elif command == "update":
        print(clr.Fore.RED + "Error: Updating isn't implemented yet")
        sys.exit(1)
    elif command == "pipupdate":
        os.system("pip3 install --upgrade pip")
        #update pip packages
        os.system("pip3 list --outdated --format=freeze | xargs -n1 pip3 install -U")
    elif command == "extupdate":
        #check if the package manager is installed
        try:
            pacman = sys.argv[2]
        except:
            print(clr.Fore.RED + "Error: No package manager specified")
            sys.exit(1)
        if pacman == "pacman":
            if plt.system() == "Linux":
                #is pacman installed?
                if os.path.exists("/usr/bin/pacman"):
                    #install the package
                    os.system("pacman -Syu")
                else:
                    print(clr.Fore.RED + "Error: pacman is not installed")
                    sys.exit(1)
            else:
                print(clr.Fore.RED + "Error: pacman is not supported on this platform")
                sys.exit(1)
        elif pacman == "apt":
            if plt.system() == "Linux":
                os.system("apt-get update && apt-get upgrade")
            else:
                print(clr.Fore.RED + "Error: apt is not supported on this platform")
                sys.exit(1)
        elif pacman == "yum":
            if plt.system() == "Linux":
                #is yum installed?
                if os.path.exists("/usr/bin/yum"):
                    os.system("yum update")
                else:
                    print(clr.Fore.RED + "Error: yum is not installed")
                    sys.exit(1)
            else:
                print(clr.Fore.RED + "Error: yum is not supported on this platform")
                sys.exit(1)
        elif pacman == "dnf":
            if plt.system() == "Linux":
                #check if it is installed
                if os.path.exists("/usr/bin/dnf"):
                    os.system("dnf update")
                else:
                    print(clr.Fore.RED + "Error: dnf is not installed")
                    sys.exit(1)
            else:
                print(clr.Fore.RED + "Error: dnf is not supported on this platform")
                sys.exit(1)
        elif pacman == "brew":
            if plt.system() == "Darwin" or plt.system() == "Linux":
                #check if brew is installed
                if not os.path.exists("/usr/local/bin/brew"):
                    print(clr.Fore.RED + "Error: brew is not installed")
                    sys.exit(1)
                else:
                    os.system("brew update")
                    os.system("brew upgrade")
            else:
                print(clr.Fore.RED + "Error: brew is not supported on this platform")
                sys.exit(1)
        elif pacman == "port":
            if plt.system() == "Darwin":
                #check if port is installed
                if os.path.exists("/opt/local/bin/port"):
                    os.system("port upgrade outdated")
                else:
                    print(clr.Fore.RED + "Error: port is not installed")
                    sys.exit(1)
            else:
                print(clr.Fore.RED + "Error: port is not supported on this platform")
                sys.exit(1)
        elif pacman == "emerge":
            if plt.system() == "Linux":
                #check if emerge is installed
                if os.path.exists("/usr/bin/emerge"):
                    os.system("emerge -uD world")
                else:
                    print(clr.Fore.RED + "Error: emerge is not installed")
                    sys.exit(1)
            else:
                print(clr.Fore.RED + "Error: emerge is not supported on this platform")
                sys.exit(1)
        else:
            print(clr.Fore.RED + "Error: Package manager not supported")
            sys.exit(1)
    else:
        print(clr.Fore.RED + "Error: Invalid command")
        sys.exit(1)

if __name__ == "__main__":
    main()
    sys.exit(0)