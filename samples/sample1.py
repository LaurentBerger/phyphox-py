
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
    print("POLLING DATA")
    my_phones = PhyphoxLogger("192.168.0.4", 8080, no_proxy=True)
                 
    my_phone.meta_cmd()
    my_phone.config_cmd()
    print(my_phone)
    my_phone.print_buffer_name()
    if my_phones[0].buffer_needed([(0, 0, 1, 2, 3, 4)]):
        my_phone.clear_cmd()
        my_phone.print_select_buffer()
        my_phone.clear_cmd()
        my_phone.start_cmd()
        time.sleep(1)
        for _ in range(10):
            my_phone.get_measure(full_data=True)
            print(my_phone.get_nb_measure())
            last_tab = my_phone.get_last_measure()
            if my_phone.new_data:
                if my_phone.overflow:
                    print("PhyphoxLogger overflow")
                for tabs in last_tab:
                    for tab in tabs:
                        print(len(tab), len(tab))
                my_phone.new_data = False
            time.sleep(1)
        my_phone.stop_cmd()
    else:
        print("Invalid buffer selected")
