import Jlink
import argparse
import time
import traceback

if __name__ == '__main__':
    print("Log reader application")
    parser = argparse.ArgumentParser(prog="Log reader app", description="use for read RTT log")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")
    parser.add_argument("-s", "--sn", dest="sn", nargs='*', required=True)
    parser.add_argument("-p", "--prefix", dest="prefix")
    args = parser.parse_args()
    if args.sn[0] == "ALL":
        Jlink.log_start(args.verbose, args.prefix, None, all=True, sn_tag=False, reset=True)
    else:
        sn_list = [int(s) for s in args.sn]
        print(sn_list)
        for i in range(5):
            try:
                Jlink.log_start(False, args.prefix + "-" + str(i+1), sn_list, all=False, sn_tag=False, reset=True)
                Jlink.log_start(True, args.prefix + "-" + str(i+1), [1], all=False, sn_tag=False, reset=True)
                time.sleep(300)
                print("=================================================")
                print("*************************************************")
                Jlink.kill_all()
                time.sleep(5)
            except BaseException as e:
                print(traceback.format_exc())
                print("illegal sn!")
    count = 0
    # while True:  # 保持主线程开启 才能保证后台线程的运行
    #     try:
    #         time.sleep(5)
    #         if count == 12:
    #             count = 0
    #             # print("Still awake")
    #         count += 1
    #     except KeyboardInterrupt:
    #         Jlink.kill_all()
    #         exit()
