import sys

if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    lines = open(input_file).read().split("\n")
    split_lines = [l.split("\t") for l in lines]
    split_lines = [l for l in split_lines if len(l) == 10]
    all_edus = []
    i = 0
    current_index = split_lines[0][9]
    current_edu = []
    while i < len(split_lines):
        index = split_lines[i][9]
        word = split_lines[i][2]
        if index == current_index:
            current_edu.append(word)
        else:
            all_edus.append(current_edu)
            current_edu = [word]
        current_index = index
        i += 1
    all_edus = [' '.join(e) for e in all_edus]
    with open(output_file, 'wb') as f:
        for line in all_edus:
            f.write(line+"\n")
