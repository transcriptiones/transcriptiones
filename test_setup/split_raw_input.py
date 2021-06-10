lines_per_file = 50
smallfile = None
first_filename_number = 944
with open('raw_input_9.txt') as bigfile:
    for lineno, line in enumerate(bigfile):
        if lineno % lines_per_file == 0:
            first_filename_number += 1

            if smallfile:
                smallfile.close()
            small_filename = 'dummy_texts/{}.txt'.format(first_filename_number)
            smallfile = open(small_filename, "w")
        smallfile.write(line)
    if smallfile:
        smallfile.close()
