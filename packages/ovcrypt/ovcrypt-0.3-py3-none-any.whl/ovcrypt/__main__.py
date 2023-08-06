from ovcrypt import cfg_class, cfg
import sys


if len(sys.argv) < 2 or sys.argv[1] == '-h':
    print("Usage python3 -m ovcrypt --update-config key value")
    sys.exit(0)

if sys.argv[1] == '--update-config':
    if len(sys.argv) < 4:
        print('Please specify key and value (-h for help)')
        sys.exit(0)

    key = sys.argv[2]
    value = sys.argv[3]

    if key in cfg:
        cfg[key] = value

        cfg_class.update_config(cfg)
    else:
        print("Key %s not found in cfg" % (key, ))
