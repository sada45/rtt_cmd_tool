import Jlink
import argparse
import traceback

if __name__ == '__main__':
    print("mass flash appiation")
    parser = argparse.ArgumentParser(prog='rttapp', description='JLink mass flash')
    # parser.add_argument("-v", "--verbose", action='store_false')
    parser.add_argument("-f", "--file", dest='file', required=True)
    parser.add_argument("-s", "--sn", dest='sn', nargs='*', required=True)
    parser.add_argument("-d", "--softdevice", dest="sd", action="store_true")
    parser.add_argument("-e", "--erase", dest="erase", action="store_true")
    args = parser.parse_args()
    print(args)
    if args.sn[0] == 'ALL':
        Jlink.mass_flash(hex_file=args.file, sn=None, all=True, sd=args.sd, erase=args.erase)
    else:
        try:
            flash_sn_list = [int(s) for s in args.sn]
            Jlink.mass_flash(hex_file=args.file, sn=flash_sn_list, all=False, sd=args.sd, erase=args.erase)
        except BaseException:
            print(traceback.format_exc())
