# check if the number of arguments is correct
if [ $# -ne 2 ]; then
    echo "Usage: $0 <program_file> <output_file>"
    echo "Example: $0 programs/simple_prog_gen.prog programs/simple_prog_gen.bin"
    exit 1
fi

PROGRAM_FILE=$1
OUTPUT_FILE=$2

# Compile the program
python3 programs/compiler.py $1 $2