

import sys, time

def main():

    names = ['Megan', 'Sam', 'Aaron', 'Jonah', 'Olivia', 'Max', 'Piper', 'Bailey', 'Kaiser', 'Otto']

    for name in names:

        i = names.index(name)

        # print '%d\t:\t%s' % (i, name)

        counter = 0
        maxCounter = 10

        while counter <= maxCounter:

            prefix_string = '%d : %s' %(names.index(name)+1, name)
            print_progress(counter, maxCounter, prefix=prefix_string)

            time.sleep(0.1)

            counter += 1

# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100, complete_symbol='#', incomplete_symbol='-'):

    """
    Call in a loop to create terminal progress bar
    @params:
        iteration           - Required  :   current iteration (Int)
        total               - Required  :   total iterations (Int)
        prefix              - Optional  :   prefix string (Str)
        suffix              - Optional  :   suffix string (Str)
        decimals            - Optional  :   positive number of decimals in percent complete (Int)
        bar_length          - Optional  :   character length of bar (Int)
        complete_symbol     - Optional  :   character used to display completion progress
        incomplete_symbol   - Optional  :   character used to display remaining progress
    """

    str_format = "{0:." + str(decimals) + "f}"
    if total > 0:
        percents = str_format.format(100 * (iteration / float(total)))
        filled_length = int(round(bar_length * iteration / float(total)))
    else:
        percents = str_format.format(100)
        filled_length = 100


    bar = complete_symbol * filled_length + incomplete_symbol * (bar_length - filled_length)

    if prefix == '':
        prefix_a = ' ' * (len(str(total)) - len(str(iteration))) + str(iteration)
        prefix_b = str(total)
        prefix = '%s of %s' % (prefix_a, prefix_b)


    sys.stdout.write('\r%s\t|%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()



if __name__ == '__main__':
    main()
