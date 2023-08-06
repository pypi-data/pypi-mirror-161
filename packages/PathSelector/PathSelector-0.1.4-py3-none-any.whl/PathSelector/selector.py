import os
import re

class Selector:

    @staticmethod
    def selectPath(startPath : str =  os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'), filters : list = list(), showFolders : bool = True, regex_selector : re.Pattern = None, use_regex_on_folder = False) -> str:
        def add(count, i, folder = False):
            if not folder:
                print(f"[ {count} ] - {i}")
            else:
                print(f"[ {count} ] - {i} (folder)")
            items.append(i)
            count += 1
            return count

        tmpPath = startPath
        while(True):
            os.system('cls')
            count = 1
            items = list()
            print("Current folder: " + startPath + "\n")
            for i in os.listdir(startPath):
                if os.path.isdir(os.path.join(startPath, i)):
                    if showFolders:
                        if use_regex_on_folder:
                            if regex_selector != None:
                                if re.search(regex_selector, i):
                                    count = add(count, i, True)
                                    continue
                            else:
                                count = add(count, i, True)
                                continue
                        else:
                            count = add(count, i, True)
                            continue
                else:
                    if len(filters) <= 0:
                        if regex_selector != None:
                            if re.search(regex_selector, i):
                                count = add(count, i)
                                continue
                        else:
                            count = add(count, i)
                            continue
                    else:
                        ext = i.split('.')[-1]
                        if ext in filters:
                            if regex_selector != None:
                                if re.search(regex_selector, i):
                                    count = add(count, i)
                                    continue
                            else:
                                count = add(count, i)
                                continue
                    
            
            print("\n[ -1 ] - Cancel")
            print("[ -2 ] - .. ( Upper Folder )")
            print("[ -3 ] - Select Current Folder")
            if startPath != tmpPath: print("[ -4 ] - Previous Folder")
            try:
                choice = int(input("\nSelect a directory or a file: "))
            except Exception:
                print("\nSelect a NUMBER from the list.")
                input("Press enter to continue...")
                os.system('cls')
                continue
            
            if choice == -1:
                break

            if choice == -2:
                paths = startPath.split("\\")
                if len(paths) > 1:
                    tmpPath = startPath
                    startPath = "\\".join([path for path in paths if path != paths[-1]])
                    if len(startPath) == 2:
                        startPath = startPath + "\\"
                else:
                    print("You can't go upper folder from here.")
                    input("Press enter to continue...")
                os.system('cls')
                continue

            if choice == -3:
                return startPath

            if choice == -4:
                startPath, tmpPath = tmpPath, startPath
                os.system('cls')
                continue

            if choice <= 0 or choice >= count:
                print("\nInvalid operation\n")
                input("Press enter to continue...")

            else:
                selected = items[choice - 1]
                if not os.path.isdir(os.path.join(startPath, selected)):
                    print(f"\n\nYour choice: {selected}")
                    sure = input("\nDo you really want to select it [Y/n]: ")
                    if sure.lower().strip() == "" or sure.lower().strip() == "y":
                        return os.path.join(startPath, selected)
                    elif sure.lower().strip() == "n":
                        continue
                    else:
                        print("Wrong input.")
                        input("Press enter to continue...")
                        os.system('cls')
                        continue
                else:
                    tmpPath = startPath
                    startPath = os.path.join(startPath, selected)
                    os.system('cls')
                    continue