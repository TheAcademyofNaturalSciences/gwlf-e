import os
import re

def Distiller():
    fileout = open("gwlfe\combined.py", 'w')
    fileout.writelines(["# coding: utf-8\n",
                        "import logging\n",
                        "import numpy as np\n",
                        "from Memoization import memoize\n",
                        "from Timer import time_function\n",
                        "import json\n",
                        "import uuid\n",
                        "import csv\n",
                        "import re\n"])
    for root, dirs, files in os.walk("gwlfe"):
        for file in files:
            if (file.endswith(".py") and not file.endswith("_inner.py") and not file == "combined.py"):
                with open(os.path.join(root, file), 'r') as file_in:
                    print(file)
                    lines = file_in.readlines()
                    for line in lines:
                        if(re.match("^(import|from)",line,re.MULTILINE)):
                            pass
                        else:
                            # if(line.find("\xe2")):
                            #     print(line)
                            fileout.write(line.replace("\xe2",""))
                print(fileout.write("\n"))
    fileout.close()


if __name__ == "__main__":
    Distiller()
