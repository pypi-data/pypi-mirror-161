class EditDistance:


    def __init__(self, reference, hypothesis, unit="word"):
        """
        Convert the strings into lists
        If the strings are phrases with more than one word, split by space;
        if the strings have no space, split into a list of chars;
        """
        if unit == "word":
            self.reference = reference.split(' ')
            self.hypothesis= hypothesis.split(' ')
        elif unit == "char":
            self.reference = list(reference)
            self.hypothesis = list(hypothesis)
        else:
            print("ERROR: invalid name of unit")
        self.ref_len = len(self.reference)


    def __get_matrix__(self):

        #get a list of token, preceded by a placeholder matching the beginning of a phrase;
        string1 = ['*'] + self.reference
        string2 = ['*'] + self.hypothesis

        # set up a (len(string1) + 1) * (len(string2) + 1) matrix
        matrix = [[0] * len(string1) for x in range(len(string2))]

        #set up the first column and row
        for i in range(len(string1)):
            matrix[0][i] = i
        for j in range(len(string2)):
            matrix[j][0] = j

        #loop through the array
        for i in range(1, len(string2)):
            for j in range(1, len(string1)):

                UP = matrix[i-1][j]
                LEFT = matrix[i][j-1]
                DIA = matrix[i-1][j-1]

                previous_number = min(#find the smallest number among top, left, corner
                        UP,
                        LEFT,
                        DIA
                        )

                char2 = string2[i]
                char1 = string1[j]

                if char2 != char1 or UP < DIA or LEFT < DIA:

                    matrix[i][j] = previous_number + 1
                else:
                    matrix[i][j] = previous_number

        return matrix


    def error_count(self):
        '''
        return number of errors
        '''
        return self.__get_matrix__()[-1][-1]


    def get_movement(self):
        matrix = self.__get_matrix__()
        #traceback initial position
        string1 = ['*'] + self.reference
        string2 = ['*'] + self.hypothesis


        x = len(string2) - 1
        y = len(string1) - 1

        movement = []
        while x > 0 and y > 0:


            up = int(matrix[x-1][y])
            diagonal = int(matrix[x-1][y-1])
            left = int(matrix[x][y-1])
            current = int(matrix[x][y])


            if up < diagonal and up < left: #up is the smallest number, meaning it moved down
                x -= 1
                movement = [['down', up - current]] + movement #up-current: if the number changed

            elif diagonal < up and diagonal < left:
                x -= 1
                y -= 1
                movement = [['diagonal', diagonal - current]] + movement

            elif left < diagonal and left < up:
                y -= 1
                movement = [['right', left - current]] + movement

            elif up == diagonal and up < left: #up and diagonal cell the same
                if string1[y] == string2[x]: #if the chars are the same, it must be from diagonal, cause no movement happened
                    x -= 1
                    y -= 1
                    movement = [['diagonal', diagonal - current]] + movement
                else:
                    x -= 1
                    movement = [['down', up - current]] + movement
            elif diagonal == left and diagonal < up:
                if string1[y] == string2[x]:
                    x -= 1
                    y -= 1
                    movement = [['diagonal', diagonal - current]] + movement
                else:
                    y -= 1
                    movement = [['right', left - current]] + movement
            else: #it should be impossible that the left and top cells are both the smallest
                    x -= 1
                    y -= 1
                    movement = [['diagonal', diagonal - current]] + movement

        #in case the loop has stopped but we have not reached the top left corner
        if y == 0 and x != 0:
            for i in range(x):
                movement = [['down', -1]] + movement
        elif x == 0 and y != 0:
            for j in range(y):
                movement = [['right', -1]] + movement

        return movement


    def generate_change(self, alignment=False):

        changes = self.get_movement()

        tracker = []

        string1 = self.reference
        string2 = self.hypothesis

        delete_num = 0
        insert_num = 0

        index_list_1 = []
        index_list_2 = []

        for i in range(len(changes)):
            move = changes[i]
            if move[0] == 'right':
                tracker.append([string1[i], 'deleted', i - insert_num])
                delete_num += 1
                #index_list_1.append(i - insert_num)
                string2 = string2[:i] + ['*'] + string2[i:]
                # string1 = string1[:i] + ['*'] + string1[i+1:]

            elif move[0] == 'down':
                tracker.append([string2[i], 'inserted', i - delete_num])
                insert_num += 1
                #index_list_2.append(i -  delete_num)
                string1 = string1[:i] + ['*'] + string1[i:]

            elif move[0] == 'diagonal' and move[1] == -1:
                tracker.append([string1[i], 'substituted', string2[i],i - insert_num,i - delete_num])
        if alignment:
            return string1, string2
        return tracker


    def get_deleted_and_substituted(self):
        errored_words = []
        tracker = self.generate_change()
        for change in tracker:
            if change[1] in ['deleted', 'substituted']:
                errored_words.append(change[0])
        return errored_words
