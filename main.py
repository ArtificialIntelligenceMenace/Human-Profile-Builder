

import linkage
import os


def main():
    os.system("00_initial_datasets_tables.sh")
    linkage.main()

if __name__=="__main__":
    main()