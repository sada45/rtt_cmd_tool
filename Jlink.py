import pylink
import time
import threading

connected_sn_list = [i for i in range(1, 14)]  # 目前所有jlink的序列号
jlink_thread_pool = []
term_thread_pool = []
soft_device_path = "E:/JLink/s140_nrf52_7.0.1_softdevice.hex"  # 必须为绝对路径
soft_device_end_addr = 0x27000


class JLink_IF:  # RTT输出的接口
    BUFFER_MAXLEN = 100
    log_file = None  # log存储文件对象
    jlink = None  # 用于连接的jlink对象
    sn = 0
    log_buffer = ''
    _is_running = True

    def __init__(self, sn, log_file_name=None, buffer_len=100):
        self.BUFFER_MAXLEN = buffer_len
        self.sn = sn
        if log_file_name is not None:
            print("SN = ", self.sn, " log file writing enabled")
            self.log_file = open("/home/sada45/JLink/logs/" + log_file_name + "_" + str(self.sn) + ".log", 'w+')

    def jlink_connect(self):  # 连接jink
        print("SN = ", self.sn, " Connecting...")
        lib = pylink.library.Library('/home/sada45/JLink/libjlinkarm.so')
        self.jlink = pylink.JLink(lib)
        self.jlink.open(self.sn)
        self.jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
        self.jlink.connect("nRF52840_xxAA")
        if self.jlink.connected():
            print("SN = ", self.sn, " Connected")
        else:
            print("SN = ", self.sn, " Connection failed")
        return self.jlink.connected()

    def jlink_reset(self):
        self.jlink.reset(0, False)

    def rtt_start(self):
        self.jlink.rtt_start()

    def rtt_close(self):
        self.jlink.rtt_stop()

    def log_updates(self, append_log_str):
        # print("update=====", append_log_str)
        self.log_buffer += append_log_str  # 将log加到目前的buffer中
        if len(self.log_buffer) > self.BUFFER_MAXLEN:
            if self.log_file is not None:
                self.log_file.write(self.log_buffer)
                self.log_file.flush()
            self.log_buffer = ''

    def log_flush(self):  # 将当前缓存中所有的数据写入文件
        if self.log_file is not None and len(self.log_buffer) > 0:
            self.log_file.write(self.log_buffer)
            self.log_file.flush()
            self.log_buffer = ''

    def rtt_read_contious(self, console_output=False, sn_tag=False):  # 连续对log进行读取
        while self.jlink.connected():
            read_data = ''.join([chr(c) for c in self.jlink.rtt_read(0, 500)])
            if len(read_data) != 0:
                if console_output:
                    if sn_tag:
                        print("SN = ", self.sn)
                    print(read_data, end='')
                self.log_updates(read_data)
            time.sleep(0.1)

    def rtt_read_once(self, verbose=False, sn_tag=False):  # 一次性读取所有缓存中内容
        read_data = ''.join([chr(c) for c in self.jlink.rtt_read(0, 100)])
        while len(read_data) != 0:
            self.log_updates(read_data)  # 写入缓存
            if verbose:  # 输出log
                if sn_tag:
                    print("SN = ", self.sn)
                print(read_data, end='')
            read_data = ''.join([chr(c) for c in self.jlink.rtt_read(0, 100)])

    def flash(self, hex_file_name, has_sd=True, erase=False):
        print("SN = ", self.sn, " Flashing...")
        if erase:
            self.jlink.erase()
        if has_sd:
            self.jlink.flash_file(soft_device_path, 0)  # 首先烧写s140协议栈
            self.jlink.flash_file(hex_file_name, soft_device_end_addr)  # 从0x27000的地址开始烧写用户代码
        else:
            self.jlink.flash_file(hex_file_name, 0)
        self.jlink.reset(0, False)
        print("SN = ", self.sn, " Flash done")

    def rtt_write(self, verbose, input_str, sn_tag=False, end=b'\r\n'):
        # self.rtt_read_once(verbose, sn_tag)
        writedata = list(bytearray(input_str, "utf-8") + end)
        writeindex = 0
        while writeindex < len(writedata):
            bytes_written = self.jlink.rtt_write(0, writedata[writeindex:])
            writeindex = writeindex + bytes_written
            time.sleep(0.01)
        self.log_updates(input_str + bytes.decode(end))
        time.sleep(0.1)
        self.rtt_read_once(verbose, sn_tag)

    def outside_interrupt(self):
        self._is_running = False

    def jlink_close(self):
        self.jlink.close()

    def __del__(self):
        print("Flushing")
        self.log_flush()  # 清空文件写入缓存
        if self.jlink.connected():  # 将Jlink连接关闭
            self.jlink.close()


def kill_all():
    if len(term_thread_pool) != 0:
        for t in term_thread_pool:
            t.stop()
            t.__del__()
            del t
        term_thread_pool.clear()
    if len(jlink_thread_pool) != 0:
        for t in jlink_thread_pool:
            t.stop()
            t.__del__()
            del t
        jlink_thread_pool.clear()


class Log_Thread(threading.Thread):
    jif = None
    verbose = False
    sn = 0
    reset = False
    sn_tag = False

    def __init__(self, sn, verbose=False, log_file_name="jlink_log", sn_tag=False, reset=False):
        super(Log_Thread, self).__init__()
        self.sn = sn
        self.verbose = verbose
        self.sn_tag = sn_tag
        self.reset = reset
        self.jif = JLink_IF(sn, log_file_name)
        self.jif.jlink_connect()

    def run(self):
        if self.reset:
            self.jif.jlink_reset()
        self.jif.rtt_start()
        try:
            self.jif.rtt_read_contious(self.verbose, self.sn_tag)
        except AttributeError:
            print(self.sn, " stopped")

    def stop(self):
        self.jif.outside_interrupt()

    def __del__(self):
        try:
            self.jif.log_flush()
            self.jif.rtt_close()
            self.jif.jlink_close()
        except:
            pass


class Term_Thread(threading.Thread):
    jif = None
    verbose = True
    sn_tag = False
    sn = 0
    run_signal = None
    output_signal = None
    output_str = None
    first_read_done = False

    def __init__(self, sn, prefix, verbose=True, sn_tag=False):
        super(Term_Thread, self).__init__()
        self.jif = JLink_IF(sn, prefix)
        self.sn = sn
        self.verbose = verbose
        self.sn_tag = sn_tag
        self.jif.jlink_connect()
        self.jif.jlink_reset()
        self.jif.rtt_start()
        self.run_signal = threading.Event()
        self.output_signal = threading.Event()
        self.run_signal.set()
        self.output_signal.clear()

    def run(self):
        time.sleep(0.5)
        self.jif.rtt_read_once(self.verbose, self.sn_tag)
        self.first_read_done = True
        while True:
            self.run_signal.wait()
            # self.output_signal.clear()
            try:
                self.jif.rtt_read_once(self.verbose, self.sn_tag)
            except AttributeError:
                print(self.sn, " stopped")
            # self.output_signal.set()
            time.sleep(0.05)

    def output_event(self, output_str):
        self.run_signal.clear()
        self.output_str = output_str[:]
        self.jif.rtt_write(self.verbose, self.output_str, self.sn_tag)
        self.jif.log_flush()
        self.run_signal.set()

    def stop(self):
        self.run_signal.clear()
        time.sleep(0.06)

    def __del__(self):
        print("del")
        self.jif.log_flush()
        self.jif.rtt_close()
        self.jif.jlink_close()
        del self.jif


def mass_flash(hex_file, sn=None, all=False, sd=True, erase=False):  # hex_file路径必须为绝对路径！！！！！
    flash_sn_list = None
    if all:
        flash_sn_list = connected_sn_list[:]
        print("Programming ALL nodes")
    else:
        flash_sn_list = sn
        print("Programming ", flash_sn_list)
    for sn in flash_sn_list:
        print("Programming JLink sn = ", sn)
        jlink_if = JLink_IF(sn)
        jlink_if.jlink_connect()
        try:
            jlink_if.flash(hex_file, sd, erase)
            jlink_if.jlink_reset()
        except BaseException:
            jlink_if.close()
            del jlink_if


def log_start(verbose, log_file_prefix, sn_list=None, all=False, sn_tag=False, reset=False):
    # jlink_thread_pool = []
    if all:
        for sn in connected_sn_list:
            log_thread = Log_Thread(sn, verbose, log_file_prefix, sn_tag, reset)
            log_thread.daemon = True
            jlink_thread_pool.append(log_thread)
            log_thread.start()
    elif sn_list is not None:
        for sn in sn_list:
            log_thread = Log_Thread(sn, verbose, log_file_prefix, sn_tag, reset)
            log_thread.daemon = True
            jlink_thread_pool.append(log_thread)
            log_thread.start()
    else:
        print("No sn inputted")
        return


def rtt_terminal_thread(verbose, prefix, sn_list=None, all=False, sn_tag=False):
    # term_thread_pool = []
    term_sn_list = None
    if all:
        term_sn_list = connected_sn_list[:]
    elif sn_list is not None:
        term_sn_list = sn_list[:]
    else:
        print("No sn inputted")
        return
    for sn in term_sn_list:
        print("Connectiong to sn:", sn)
        tthread = Term_Thread(sn, prefix, verbose, sn_tag)
        tthread.daemon = True
        term_thread_pool.append(tthread)
        tthread.start()
    all_done = False
    while not all_done:
        all_done = True
        for t in term_thread_pool:
            if not t.first_read_done:
                all_done = False
                break
        time.sleep(0.1)
    while True:
        try:
            command_str = input()
            for tthread in term_thread_pool:
                tthread.output_event(command_str)
        except KeyboardInterrupt:
            kill_all()
            exit()


def rtt_terminal_serial(verbose, prefix, sn_list=None, all=False, sn_tag=False):
    jif_pool = []
    term_sn_list = None
    if all:
        term_sn_list = connected_sn_list[:]
        term_sn_list = connected_sn_list[:]
    elif sn_list is not None:
        term_sn_list = sn_list[:]
    else:
        print("No sn inputted")
    for sn in term_sn_list:
        print("Connecting to sn:", sn)
        jif = JLink_IF(sn, prefix)
        jif.jlink_connect()
        jif.jlink_reset()
        jif.rtt_start()
        jif_pool.append(jif)
    time.sleep(1)
    for jif in jif_pool:
        jif.rtt_read_once(verbose, sn_tag)
    while True:
        print(">>>", end='')
        command_str = input()
        for jif in jif_pool:
            jif.rtt_write(verbose, command_str, sn_tag)


if __name__ == '__main__':
    print("view")
    jif = JLink_IF('1')
    jif.jlink_connect()
    jif.jlink_reset()
    jif.rtt_start()
    jif.rtt_read_contious(True)
