import pysvn
import sys
import os
import datetime
import asciitable

TIME_FORMAT = "%I:%M%p"
DATE_FORMAT = "%a %d/%m/%y"

def format_timestamp(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    timestr = dt.strftime(TIME_FORMAT)
    daydelta = datetime.datetime.now().date() - dt.date()
    if daydelta.days == 0:
        # today, so just show the time
        return timestr
    if daydelta.days == 1:
        return "Yesterday %s" % timestr
    else:
        return timestr + " " + dt.strftime(DATE_FORMAT)

def get_status_entry_tuple(status_entry, from_path):
    timestamp = os.path.getmtime(status_entry["path"])

    return (str(status_entry["text_status"]), 
            os.path.relpath(status_entry["path"],
                from_path),
            timestamp)

def get_status(status_list, from_path):
    printable = (s for s in status_list if s["text_status"] not in 
            { pysvn.wc_status_kind.normal, 
              pysvn.wc_status_kind.ignored })

    tuples = [get_status_entry_tuple(status, from_path)
        for status in printable]

    def status_cmp(status_a, status_b):
        # by timestamp
        return int(status_a[2] - status_b[2])

    tuples.sort(cmp=status_cmp)

    return tuples

def process_stat(args):
    client = pysvn.Client()
    status = client.status(args.path)
    asciitable.write(
            get_status(status, args.path), 
            sys.stdout, 
            names=("status", "file", "modified"),
            Writer=asciitable.FixedWidthTwoLine,
            bookend=False,
            formats={
                "modified": format_timestamp, 
                "status": str
            })

def main():
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    stat_parser = subparsers.add_parser("status", help="Print the status of"
            "working copy files and directories.")
    stat_parser.set_defaults(func=process_stat, path=os.getcwd())
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
