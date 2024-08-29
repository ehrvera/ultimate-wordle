import random

global basicHint_chosen, advancedHint_chosen, basicHint_available, advancedHint_available
basicHint_chosen, advancedHint_chosen, basicHint_available, advancedHint_available = 0, 0, True, True

class wordleAlgorithm():
    C_PREFIX, W_PREFIX, N_PREFIX = '-c-', '-w-', '-n-'  # -c- -w-
    PREFIX_LIST = C_PREFIX, W_PREFIX, N_PREFIX    

    def __init__(self, correct_answer):
        self.word_length = len(correct_answer)
        self.letterWithin_dict = {}
        self.letterCorrect_dict = {}
        self.letterNonwithin_dict = {}
        self.conLetters_answer = list(correct_answer)
        self.conLetters_answer__basicHint = self.conLetters_answer.copy()

        self.settings_LettersLength = len(self.conLetters_answer)
        
        #make a keyboard list and a round list 
        letter_count= {}

        for letter in self.conLetters_answer:
            if letter in letter_count:
                letter_count[letter] += 1
            else:
                letter_count[letter] = 1
        self.letterDuplicate_dict = {letter: count for letter, count in letter_count.items() if count > 1}
        self.unedited_letterDuplicate = self.letterDuplicate_dict.copy()

    def analyse(self, user_input):
        self.conLetters_input = list(user_input)
        self.conLetters_input__basicHint = self.conLetters_input.copy()

        for completeMatchIndex in range(self.settings_LettersLength):
            if self.conLetters_answer[completeMatchIndex] == self.conLetters_input[completeMatchIndex]:
                self.letterCorrect_dict[self.conLetters_input[completeMatchIndex]] = completeMatchIndex
                if self.letterDuplicate_dict.get(self.conLetters_input[completeMatchIndex]) != None:
                    if self.letterDuplicate_dict.get(self.conLetters_input[completeMatchIndex]) < 2:
                        del self.letterDuplicate_dict[self.conLetters_input[completeMatchIndex]]
                    else:
                        self.letterDuplicate_dict[self.conLetters_input[completeMatchIndex]] -= 1
                self.conLetters_input[completeMatchIndex], self.conLetters_answer[completeMatchIndex] = self.C_PREFIX, self.C_PREFIX

        for answerIndex in range(self.settings_LettersLength):   # use the correct word compare with the user input
            for inputIndex in range(self.settings_LettersLength):
                if answerIndex != inputIndex and self.conLetters_answer[answerIndex] not in self.PREFIX_LIST and self.conLetters_answer[answerIndex] == self.conLetters_input[inputIndex]:
                    self.letterWithin_dict[self.conLetters_answer[answerIndex]] = inputIndex # previously = [answerIndex, inputIndex]
                    self.conLetters_input[inputIndex], self.conLetters_answer[answerIndex] = self.W_PREFIX, self.W_PREFIX

        for nonWithinIndex in range(self.settings_LettersLength):
            if self.conLetters_input[nonWithinIndex] not in self.PREFIX_LIST:
                self.letterNonwithin_dict[self.conLetters_input[nonWithinIndex]] = nonWithinIndex
                self.conLetters_input[nonWithinIndex] = self.N_PREFIX

        print('within', self.letterWithin_dict)
        print('correct', self.letterCorrect_dict)
        print('nonwithin', self.letterNonwithin_dict)
        
        word_matched = False
        if self.letterNonwithin_dict == {} and self.letterWithin_dict == {}:
            word_matched = True

        #if len(self.letterCorrect_dict) == self.word_length:
        #    word_matched = True


        #print('correct chosen', self.letterCorrect_dict.get('h', None))
        print(self.conLetters_answer)
        print(self.conLetters_input)

        return self.letterCorrect_dict, self.letterWithin_dict, self.letterNonwithin_dict, self.conLetters_input, word_matched


    def dupe_basicHint(self): # dupe letter is deleted if user has already found both
        edited_letterDuplicate = [*self.letterDuplicate_dict]
        basicHint = {}
        basicHint_available = True
        key_prev = None
        dupe_smartHint = []
        

        print('edited', edited_letterDuplicate)
        print('unedited', self.unedited_letterDuplicate)
        if self.unedited_letterDuplicate != {}: 
            for basicHintIndex in range(len(edited_letterDuplicate)):
                basicHint[edited_letterDuplicate[basicHintIndex]] = self.unedited_letterDuplicate[edited_letterDuplicate[basicHintIndex]]
             
            for key in basicHint: #filter all duplicate same letters that have >= than the correct answer if any of its letters are in the incorrect position
                answer_occurrence_int = self.conLetters_input__basicHint.count(key)

                if key_prev != key:
                    index = basicHint.get(key)

                for _ in range(answer_occurrence_int):
                    for checkIndex in range(self.settings_LettersLength):
                        if self.conLetters_answer__basicHint[checkIndex] == key:
                            index -= 1
                            self.conLetters_answer__basicHint[checkIndex] = '-cut-'
                            break
                if index < 1:
                    dupe_smartHint.append(key)        

            if dupe_smartHint != []:
                for actionIndex in range(len(dupe_smartHint)):
                    del basicHint[dupe_smartHint[actionIndex]]

        
        #else:
           # basicHint_available = False
        
        print('smart hint', dupe_smartHint)  # letter appears 1+ times in the word, and at least 1 letter placed incorrectly
        print('basic hint', basicHint)

        if self.unedited_letterDuplicate != []:
            if False:
                if len(edited_letterDuplicate) > 1:  # test how many different duplicate letters there are
                    if hardHint_chosenIndex < len(edited_letterDuplicate):
                        print('\nhard hint 1', edited_letterDuplicate, self.unedited_letterDuplicate)
                        #global hardHint_chosenIndex
                        hardHint_chosenIndex += 1
                    else:
                        nextHardHintAvailable = False
                else:
                    keys_results = ''.join(edited_letterDuplicate)
                    print(keys_results)
                print('\nhard hint 2', edited_letterDuplicate, self.unedited_letterDuplicate)

        #return nextHardHintAvailable, hardHint_chosenIndex
        #self.letterDuplicate_dict.get(str('k'), None)
        
        # make keys and values into a dictionary
        # remove it after it's accseed / showed
        # return the value if it's avaliable next

    def dupe_advancedHint(self):
        letterDupeAmount_list = []
        for select in range(self.settings_LettersLength):
            for index in range(1, self.settings_LettersLength):
                if select < index and self.conLetters_answer[select] == self.conLetters_answer[index] and self.conLetters_answer[select] not in self.PREFIX_LIST:
                    letterDupeAmount_list.append([select, index, self.conLetters_answer[select]])
        print('\nadvanced hint', letterDupeAmount_list)

if True:
    wordle_algorithm = wordleAlgorithm("llxxx")

    print(wordle_algorithm.analyse("zzzzz"))
    wordle_algorithm.dupe_basicHint()
    wordle_algorithm.dupe_advancedHint()


# give hint in order: basic > smart (if avalible, sometimes not) > advanced
# if no hints, say "Title: out of hints. Desc:You already used hints in this round. Try typing new words with letters you haven't tried before!"

# create randomisation sequence
# easy mode - dupicate vraiable for text input
# keyboard support
# connect to txt files


