from lib import *


def main():
    cdl = CDLParser(cdl1)
    cd = cdl.to_dict()

    for tmpl in tmpl1, tmpl2:
        td = yaml.load(tmpl, Loader=yaml.SafeLoader)
        print(td)
        print(cd)
        print("COMPARE", cd == td)

        check_compliance(cd, template=td)


if __name__ == "__main__":
    main()
