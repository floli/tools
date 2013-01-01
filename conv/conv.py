import argparse, os, queue, shlex, sys, threading, time
from subprocess import Popen, PIPE, STDOUT
from os import path
THREADS = 4


def execute(cmd):
    print(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        raise Exception("%s returned with return code %i.\nstdout: %s\nstderr: %s " % (cmd, proc.returncode, stdout.decode(), stderr.decode()))
    return (stdout.decode(), stderr.decode())

    
class FLACFile():
    mapping = {"title":"TITLE", "artist":"ARTIST", "date":"DATE", "genre":"GENRE",
               "track":"TRACKNUMBER", "tracktotal":"TRACKTOTAL", "disc":"DISCNUMBER", "disctotal":"DISCTOTAL"}
    
    def __init__(self, filename):
        self.filename = filename

    def get_field(self, fieldname):
        out, err = execute([ "metaflac", "--show-tag=%s" % fieldname, self.filename ])
        return out.split("=")[1]

    def set_field(self, fieldname, value):
        cmd = [ "metaflac", "--set-tag=%s=%s"% (fieldname, value), self.filename ]
        print(cmd)
        execute( ["metaflac", "--remove-tag=%s" % fieldname, self.filename] )
        execute(cmd)

        
    def __getitem__(self, key):
        if key in self.mapping:
            return self.get_field(self.mapping[key])
        else:
            raise IndexError

    def __setitem__(self, key, value):
        if key in self.mapping:
            self.set_field(self.mapping[key], value)
        else:
            raise IndexError


class MP3File():
    def __init__(self, filename):
        self.filename = filename
        
    mapping = {"title":"--song", "artist":"--artist", "date":"--year", "genre":"--TCON",
               "track":"--track", "disc":"--TPOS"}
    
    def set_field(self, fieldname, value):
        execute([ "id3v2", "%s=%s" % (fieldname, value), self.filename ])

        
    def __setitem__(self, key, value):
        if key in self.mapping:
            self.set_field(self.mapping[key], value)
        else:
            raise IndexError

        
abort = threading.Event()

def generate_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["test", "convert"], help="Action to perform")
    parser.add_argument("MP3", help="Basedir for the mp3 files.")
    parser.add_argument("FLAC", help="Basedir for the flac files")
    return parser

def generate_filelist(basemp3, baseflac):
    q = queue.Queue()
    for dirpath, dirnames, filenames in os.walk(baseflac):
        for filename in filenames:
            if path.splitext(filename)[1] == ".flac":
                flac = os.path.join(dirpath, filename)
                plainpath = path.splitext(flac)[0]
                mp3 = os.path.join(basemp3, plainpath[len(baseflac)+1:]) + ".mp3"
                q.put( (flac, mp3) )
    return q


def test(queue):
    while not queue.empty() and not abort.is_set():
        temp = queue.get()
        f = temp[0]
        cmd = ["flac", "-t", f ]
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        print(stderr.decode())

        if proc.returncode != 0:
            print("%s returned %i." % (cmd, proc.returncode))
            abort.set()
            break

def convert(queue):
    cmd_flac = ["flac", "--decode", "--silent", "--stdout"]
    cmd_lame = ["lame", "-h" "--preset", "224"]

    while not queue.empty() and not abort.is_set():
        f = queue.get()
        pFlac = Popen( cmd_flac + [ f[0] ], stdout=PIPE)
        pLame = Popen( cmd_lame + [ f[1] ], stdout=PIPE, stdin=pFlac.stdout, stderr=STDOUT )
        stdout, stderr = pLame.communicate()
        
        
def start_threads(target_fun, *args):
    for t in range(THREADS):
        thread = threading.Thread(target = test, args=args)
        thread.daemon = True
        thread.start()

        
def main():
    parser = generate_argparser()
    args = parser.parse_args()
    print(args)

    queue = generate_filelist(path.normpath(args.MP3), path.normpath(args.FLAC) )

    if args.action == "test":
        print("TESTING FLACS")
        fun = test
    elif args.action == "convert":
        convert(queue)

    try:
        start_threads(fun, queue)
        while True: time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        abort.set()
        print("\nQuitting!")
        pass

if __name__ == "__main__":
    main()
