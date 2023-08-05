import sys
from elf_to_shellcode.relocate import make_shellcode, Arches, ENDIANS, StartFiles
import logging
from argparse import ArgumentParser
from elf_to_shellcode.lib.consts import LoaderSupports
from elf_to_shellcode.lib import five

parser = ArgumentParser("ElfToShellcode")
parser.add_argument("--input", help="elf input file", required=True)
parser.add_argument("--arch",
                    required=True,
                    choices=Arches.__all__,
                    help="Elf file target architecture")
parser.add_argument("--endian",
                    required=True,
                    choices=ENDIANS,
                    help="Target elf file endian")
parser.add_argument("--output", default=None, help="Output file path")
parser.add_argument("--start-method", default=StartFiles.no_start_files,
                    choices=StartFiles.__all__, help="Start method required for full glibc usage")
parser.add_argument("--verbose", default=False, action="store_true", help="Verbose output")
parser.add_argument("--save-without-header", default=False, action="store_true",
                    help="Debug option, use only to store the elf without the mini loader and the relocation table")
parser.add_argument("--loader-supports",
                    choices=LoaderSupports.choices.keys(),
                    nargs="+",
                    required=False,
                    help="Loader additional features, this will increase the size of the static loader",
                    default=[])
parser.add_argument("--interactive",
                    default=False,
                    action="store_true",
                    help="Debug mode to open interactive cli with the shellcode class")
args = parser.parse_args()
sys.modules["global_args"] = args
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Verbose level: DEBUG")
if args.output:
    output_file = args.output
else:
    output_file = args.input + "{0}.out.shell".format(args.arch)

with open(output_file, "wb") as fp:
    shellcode = make_shellcode(args.input, arch=args.arch, endian=args.endian,
                               start_file_method=args.start_method)
    fp.write(five.to_file(shellcode))

print("Created: {}".format(output_file))
