
import argparse
import ApClass


if __name__ == "__main__":
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", default="./",
                    help="path to output directory to store snapshots (default: current folder")
    args = vars(ap.parse_args())

    # start the app
    print("[INFO] starting...")
    pba = ApClass.Application(args["output"])
    pba.root.mainloop()
