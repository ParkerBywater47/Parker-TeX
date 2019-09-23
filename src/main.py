from commands import *


def main():
    os.chdir(r".\inputs")
    print("\nYour current directory: " + os.getcwd())

    running = True
    while running:
        while True:
            in_file_path = input("\nEnter a Parker-TeX file directory (or type quit to exit): ")
            # Check that the file exists and run the parser if it does
            if os.path.isfile(in_file_path):
                out_file_path = os.pardir + "\\out\\" + in_file_path[:in_file_path.find(".txt")] + "-out.txt"

                # Give a little message to the user about what the program is doing
                print("\ninput file:", os.path.abspath(in_file_path))
                print("writing output to: " + os.path.abspath(out_file_path))

                # Run parser on the input file
                with open(in_file_path, 'r') as input_file:
                    source_string = ''
                    for line in input_file:
                        source_string += line
                with open(out_file_path, "w") as out_file:
                    out_file.write(escape_commands(main_parser(source_string)))
            # check to see if the user typed quit and quit if true
            elif in_file_path.lower().strip() == 'quit':
                running = False
                break
            # report to the user that the file couldn't be found
            else:
                print("Couldn't find " + str(in_file_path) + " in " + os.getcwd() + "\nTry another directory")


main()
