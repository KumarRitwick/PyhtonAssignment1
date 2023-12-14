from collections import defaultdict

# This function gets word scores from file.
def get_word_scores(values_file):
    """
    Reads a file containing letter scores and returns a dictionary mapping letters to scores.
    """
    scores = {}
    with open(values_file, 'r') as f:
        for line in f:
            letter, score = line.strip().split()
            scores[letter] = int(score)
    return scores

letterScores = get_word_scores('./values.txt')

# This function generates word score
def generate_word_score(word):
    first_char_idx = -1
    prev_char_idx = -1
    prev_char = '\0'
    score = []

    for i, c in enumerate(word.upper()):
        if not c.isalpha():
            score.append( -1)
            continue

        if first_char_idx == -1:
            first_char_idx = i
            score.append(0)
            continue

        prev_char_idx = i
        prev_char = c
        score.append( i + letterScores[c])

    # In case of words with one letter
    if prev_char_idx == -1:
        return score

    # Update the last character with respective value
    if prev_char == 'E':
        score[prev_char_idx] = 20
    else:
        score[prev_char_idx] = 5

    return score

# This function splits words
def splitWords(words):
    splitWords = words.split()
    if len(words) > 1:
        return splitWords
    else:
        return words

# This functon will selects first charcter and return index of that char
def getFirstCharacterIndex(firstWordWeight):
    for i in range(len(firstWordWeight)):
        if(firstWordWeight[i] != -1):
            return i
    return -1

# This function returns two smallest numbers in a given array
# And returns their indices in ascending order
def getLowestScores(weightArray):
    if len(weightArray) < 2:
        return -1, -1

    minIndex = secondMinIndex = -1
    minValue = secondMinValue = 69420

    for i, value in enumerate(weightArray):
        if value == -1:
            continue
        if value < minValue:
            secondMinIndex, secondMinValue = minIndex, minValue
            minIndex, minValue = i, value
        elif minValue < value < secondMinValue:
            secondMinIndex, secondMinValue = i, value

    if secondMinIndex < minIndex:
        return secondMinIndex, minIndex
    return minIndex, secondMinIndex

# This function prepares weight for the words
def prepareWeight(words):
    wordArray = splitWords(words)
    if not wordArray:
        wordArray = words
    wordsWeightArray = []
    for i in range(len(wordArray)):
        wordsWeightArray.append(generate_word_score(wordArray[i]))
    return wordsWeightArray, wordArray

# This functon will find other two characters
# And ensure the first charcter is not being used
def getAbbreviationWithScore(wordsWeightArray, wordArray):
    completeLetters = "".join(wordArray)
    completeWeight = [wght for wghts in wordsWeightArray for wght in wghts]

    firstCharacterIndex = getFirstCharacterIndex(completeWeight)
    if firstCharacterIndex == -1 :
        return None, None
    # firstCharacterIndex = getFirstCharacterIndex(wordsWeightArray[0])

    remainingCharacters = completeLetters[firstCharacterIndex + 1:]
    remainingWeight = completeWeight[firstCharacterIndex + 1:]

    secondCharIndex, thirdCharIndex = getLowestScores(remainingWeight)

    if secondCharIndex == -1 or thirdCharIndex == -1:
        return None, None
    
    abb = completeLetters[firstCharacterIndex] + remainingCharacters[secondCharIndex] + remainingCharacters[thirdCharIndex]
    abbScore = completeWeight[firstCharacterIndex] + remainingWeight[secondCharIndex] + remainingWeight[thirdCharIndex]

    return abb, abbScore

# This function gets all the indices and weight for the pair
def getAllAbbIndicesAndWgts(weights):
    pairs = []
    for i, w1 in enumerate(weights):
        for j, w2 in enumerate(weights):
            if j<=i or w1 == -1 or w2 == -1:
                continue
            pairs.append((i, j, w1 + w2))
    return pairs

# This function creates all the abb for the words.
# And creates a key pair value for each abb.
def createAllAbs(sentence):
    words = sentence.strip().split()
    weights = []
    for word in words:
        weights.append(generate_word_score(word))
    cmplLetters = "".join(words)
    cmplWeight = [ w for weight in weights for w in weight ]

    firstCharIdx = getFirstCharacterIndex(cmplWeight)

    rmnLetters = cmplLetters[firstCharIdx + 1:]
    rmnWeight = cmplWeight[firstCharIdx + 1:]

    allAbsSuffixes = getAllAbbIndicesAndWgts(rmnWeight)

    allAbs = []
    for each in allAbsSuffixes:
        abs = cmplLetters[firstCharIdx] + rmnLetters[each[0]] + rmnLetters[each[1]]
        score = each[2]
        allAbs.append({ "ABB": abs.upper(), "SCORE": score })

    allAbs.sort(key=lambda x: x['SCORE'])
    return allAbs

#This function returns the most optimal abb of a line
def getSelectedAbs(line, lineAbs, excludeAbs):
    if len(lineAbs) <= 0:
        return None, excludeAbs

    selectedAbsIndices = []
    selectedScore = None
    for i, abDict in enumerate(lineAbs):
        ab = abDict["ABB"]
        if ab in excludeAbs:
            continue
        
        score = abDict["SCORE"]
        if selectedScore is None:
            selectedScore = score

        if score > selectedScore:
            break

        excludeAbs[ab] = True
        selectedAbsIndices.append(i)
    
    return selectedAbsIndices, excludeAbs

#This function returns all optimal abb of all the lines
def selectOptimizedAbs(allAbs, allLines):
    selectedAbs = {}
    toExcludeAbs = {}
    
    for line in allLines:
        lineAbs = allAbs[line]
        selected, excludes = getSelectedAbs(line, lineAbs, toExcludeAbs)
        toExcludeAbs = excludes
        selectedAbs[line] = selected

    return selectedAbs

# This function returns values for the optimised indices
def getValuesForOptimisedIndicies(all_abs, index):
    return [all_abs[i] for i in index]

# This function generates Abbreviation and writes it in a file.
def generate_abbreviations(filename):
    all_abs = {}
    allLines = []
    with open(filename, 'r') as f_in:
        for line in f_in:
            allLines.append(line.strip())
            abList = createAllAbs(line)
            all_abs[line.strip()] = abList

    allOptimisedAbbs = selectOptimizedAbs(all_abs, allLines)
    selectedAbs = {}
    for line, scoreIndices in allOptimisedAbbs.items():
        if scoreIndices is None:
          selectedAbs[line] = None
        else:
          selectedAbs[line] = [ all_abs[line][scrIdx] for scrIdx in scoreIndices]
    
    with open(f'Kumar_{filename.split(".")[0]}_abbrevs.txt', 'w') as f_out:
        for line in allLines:
            f_out.write(f'{line}\n')
            if selectedAbs[line] != None:
                f_out.write(' '.join([abb["ABB"] for abb in selectedAbs[line]]))
            f_out.write('\n')
    print(selectedAbs)

names = 't1.txt'
trees = 'trees.txt'
values_file = 'values.txt'

# Prompt the user to enter a file path
file_path = input("Enter the path of the file: ")

# Check if the user entered a file path
if file_path:
    print(f"Selected file: {file_path}")
else:
    print("No file path entered")

generate_abbreviations(file_path)

# InCase the file path does not work.
# generate_abbreviations(names)
# generate_abbreviations(trees)
