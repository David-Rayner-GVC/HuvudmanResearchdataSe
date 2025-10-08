import sys

def jsonl_to_json(infile_path, outfile_path):
    with open(infile_path, 'r', encoding='utf-8') as infile, \
         open(outfile_path, 'w', encoding='utf-8') as outfile:
        
        outfile.write('[\n')
        first_line = True

        for line in infile:
            line = line.strip()
            if not line:
                continue  # skip empty lines
            if not first_line:
                outfile.write(',\n')
            else:
                first_line = False
            outfile.write(line)
        
        outfile.write('\n]\n')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python jsonl_to_json.py input.jsonl output.json")
        sys.exit(1)

    jsonl_to_json(sys.argv[1], sys.argv[2])
