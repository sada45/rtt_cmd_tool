import Jlink
import argparse

if __name__ == '__main__':
    print("rtt viewer appiation")
    parser = argparse.ArgumentParser(prog='rttviewerapp', description='rtt command line')
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")
    parser.add_argument("-s", "--sn", dest="sn", nargs='*', required=True)
    parser.add_argument("-t", "--thread", dest="thread", action="store_true")
    parser.add_argument("-p", "--prefix", dest="prefix", default="rtt_view_default")
    parser.add_argument("-n", "--sntag", dest="sn_tag", action="store_true")
    args = parser.parse_args()
    if args.thread:
        if args.sn[0] == 'ALL':
            Jlink.rtt_terminal_thread(args.verbose, args.prefix, sn_list=None, all=True, sn_tag=args.sn_tag)
        else:
            flash_sn_list = [int(s) for s in args.sn]
            Jlink.rtt_terminal_thread(args.verbose, args.prefix, sn_list=flash_sn_list, all=False, sn_tag=args.sn_tag)
    else:
        if args.sn[0] == 'ALL':
            Jlink.rtt_terminal_serial(args.verbose, args.prefix, sn_list=None, all=True, sn_tag=args.sn_tag)
        else:
            flash_sn_list = [int(s) for s in args.sn]
            Jlink.rtt_terminal_serial(args.verbose, args.prefix, sn_list=flash_sn_list, all=False, sn_tag=args.sn_tag)


