"""
sample1.py
connect to phyphone mobile app.
select buffer
start data sampling  for 10 seconds and stop
"""

import time
import logging
import argparse
import phyphox


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='phyphox.py',
        description='Python interface to phyphox REST API',
        epilog='Text at the bottom of help')
    parser.add_argument('-v', '--verbose',
                        action='store_true')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format="%(levelname)s: %(message)s",
                            level=logging.DEBUG)
        logging.info("Verbose output.")
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s")
    my_phone = phyphox.PhyphoxLogger("192.168.0.1", 8080, no_proxy=True)
    my_phone.get_meta()
    my_phone.get_config()
    print(my_phone)
    my_phone.print_buffer_name()
    if my_phone.buffer_needed([(0, (0, 1, 2, 3, 4))]):
        my_phone.clear_data()
        print("\nSelected buffer names")
        my_phone.print_select_buffer()
        my_phone.clear_data()
        print("\nStart sampling\n")
        my_phone.start()
        time.sleep(1)
        for _ in range(10):
            if my_phone.read_buffers(mode_data=phyphox.BufferMode.UPDATE):
                print(my_phone.get_nb_measure())
                last_tab = my_phone.get_last_buffer_read()
                if my_phone.new_data:
                    if my_phone.overflow:
                        print("PhyphoxLogger overflow")
                    idx_exp = 0
                    for tabs in last_tab:
                        idx_buffer = 0
                        for tab in tabs:
                            print(my_phone.get_buffer_name((idx_exp, idx_buffer)), len(tab), " values")
                            idx_buffer =  idx_buffer + 1
                    my_phone.new_data = False
                time.sleep(1)
            else:
                print("Cannot read buffer")
        my_phone.stop()
    else:
        print("Invalid buffer selected")
