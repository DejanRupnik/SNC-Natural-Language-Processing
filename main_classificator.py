import partsOfSpeech as pos
import readabilityTests as rt
import featureSelection as fss
from partsOfSpeech import downloadLexicons
from partsOfSpeech import readFiles
from partsOfSpeech import PartsOfSpeechTagger
from partsOfSpeech import PartsOfSpeechReader
from partsOfSpeech import getFileByFileStatistics
import nltk
import csv
from emotionAnalysis import getEmotionsForCorpus



def fleschMediana(path):
    results=rt.readibility_test(path, "*.txt")
    sumOfValuesFLESCH = 0
    sumOfValuesKINCAID = 0

    #iteracija med rezultati
    counter = 0
    for result in results:
        sumOfValuesFLESCH += float(result[1])
        sumOfValuesKINCAID += float(result[2])
        counter += 1


    meanFLESCH = sumOfValuesFLESCH / counter
    meanKINCAID = sumOfValuesKINCAID / counter

    return meanFLESCH, meanKINCAID

def averageStat(path):
    stats = fss.splosnaStatistika(path)

    numWords = 0
    numSigns = 0
    numChars = 0
    numSentences = 0

    counter = len(stats)

    for i in range(0, len(stats)):
        stat = stats[i].split("|")

        numWords += float(stat[1])
        numSigns += float(stat[2])
        numChars += float(stat[3])
        numSentences += float(stat[4])

    meanWords = float(numWords / counter)
    meanSigns = float(numSigns / counter)
    meanChars = float(numChars / counter)
    meanSentences = float(numSentences / counter)

    return meanWords, meanSigns, meanChars, meanSentences


"""
saves CVS file of indiviual letter attribute values, for completers and elicitors
"""
def singleFileStatisticsCSV(completers_folder_pp, elicitors_folder_pp, statistics_folder, pos_folder, out_completers_filename,
                            out_elictors_filename, regular_completers_folder, regular_elicitors_folder):

    full_data_completers = []
    full_data_elicitors = []

    stats_completers = fss.splosnaStatistika(regular_completers_folder)
    stats_elicitors = fss.splosnaStatistika(regular_elicitors_folder)


    stat = stats_completers[len(stats_completers)-1].split("|")

    print(stats_completers[len(stats_completers)-1])     
    print(stat)
    paragraph_tag_name = ".//post"
    full_data_completers = getFileByFileStatistics(completers_folder_pp, pos_folder, statistics_folder, paragraph_tag_name)
    full_data_elicitors = getFileByFileStatistics(elicitors_folder_pp, pos_folder, statistics_folder, paragraph_tag_name)

    num_completers = len(full_data_completers)
    num_elicitors = len(full_data_elicitors)

    csv_out_completers = []
    csv_out_elicitors = []
    csv_attributes = []

    results=rt.readibility_test(regular_completers_folder, "*.txt")
    results_2=rt.readibility_test(regular_elicitors_folder, "*.txt")

    res_flesch_completers = []
    res_kincaid_completers = []  

    res_flesch_elicitors = []
    res_kincaid_elicitors = [] 

    csv_attributes.append("Ime_dat")

    for result in results:
        res_flesch_completers.append(result[1])
        res_kincaid_completers.append(result[2])

    for result in results_2:
        res_flesch_elicitors.append(result[1])
        res_kincaid_elicitors.append(result[2])   
    
    for i in range(0, num_completers):
        output = []
        path = full_data_completers[i][0][0]
        words = path.split("/")
        filename = words[-1]                # -1 = last element
        
        output.append(filename)
        
        dictionary = full_data_completers[i][0][1][0]
        for key in dictionary:
            if i == 0:
                csv_attributes.append(key)
                
            output.append(dictionary[key]) 
   
        if i == 0:
            csv_attributes.append("Flesch")
            csv_attributes.append("Kincaid")
            csv_attributes.append("Num_words")
            csv_attributes.append("Num_signs")
            csv_attributes.append("Num_chars")
            csv_attributes.append("Num_sentence")

        output.append(str(res_flesch_completers[i]))
        output.append(str(res_kincaid_completers[i]))

        stat = stats_completers[i].split("|")

        for j in range(1, (len(stat)-1)):
            output.append(stat[j])
        
        csv_out_completers.append(output)

    print(csv_attributes)    
    print(output)
    with open(out_completers_filename, 'wb') as fs:
        wr = csv.writer(fs, quoting=csv.QUOTE_NONE)
        wr.writerow(csv_attributes)
        for tag in csv_out_completers:
           wr.writerow(tag)

    for i in range(0, num_elicitors):
        output_2 = []
        path_2 = full_data_elicitors[i][0][0]
        words_2 = path_2.split("/")
        filename_2 = words_2[-1]                # -1 = last element
        
        output_2.append(filename_2)
        
        dictionary_2 = full_data_elicitors[i][0][1][0]
        for key in dictionary_2:
            output_2.append(dictionary_2[key])

        output_2.append(str(res_flesch_elicitors[i]))
        output_2.append(str(res_kincaid_elicitors[i]))

        stat_2 = stats_elicitors[i].split("|")

        for j in range(1, (len(stat_2)-1)):
            output_2.append(stat_2[j])

        csv_out_elicitors.append(output_2)


    with open(out_elictors_filename, 'wb') as fs:
        wr = csv.writer(fs, quoting=csv.QUOTE_NONE)
        wr.writerow(csv_attributes)
        for tag in csv_out_elicitors:
           wr.writerow(tag)        
    

"""
saves CVS file of means for completers and elicitors
"""
def saveMeanStatisticsCSV(output_csv_filename, pos_completers_folder, pos_elicitors_folder, pos_folder_path, statistics_folder_path, 
    paragraph_tag_name, readibility_completers_folder, readibility_elicitors_folder):
    
    csv_attributes = ["Attribute", "Completers Mean (SD)", "Elicitors Mean (SD)"]
    #cvs_mean_pos = [[key , completer_mean, elicitor_mean], ...]
    cvs_mean_pos = []

    ### POS statistics
    pos = PartsOfSpeechTagger(pos_folder_path)
    pos_reader = PartsOfSpeechReader(
        pos_folder_path,
        statistics_folder_path
        )
  
    ### COMPLETERS
    data = readFiles(pos_completers_folder, paragraph_tag_name)
    pos.partsOfSpeechTaggingMultiprocessed(data, 6)
    pos_reader.partsOfSpeechStatistics( pos_reader.readAnalyzedData() )
    statistics_completers = pos_reader.getMedianStatistics()

    ### ELICITORS
    data = readFiles(pos_elicitors_folder, paragraph_tag_name)
    pos.partsOfSpeechTaggingMultiprocessed(data, 6)
    pos_reader.partsOfSpeechStatistics( pos_reader.readAnalyzedData() )
    statistics_elicitors = pos_reader.getMedianStatistics()
    
    ### Flesch-ova metoda in metoda Flesch-Kincaid -> COMPLETERS
    flesch_completers, kincaid_completers = fleschMediana(readibility_completers_folder)

    ### Flesch-ova metoda in metoda Flesch-Kincaid -> ELICITORS
    flesch_elicitors, kincaid_elicitors = fleschMediana(readibility_elicitors_folder)

    cvs_mean_pos.append(["Flesch score", flesch_completers, flesch_elicitors])
    cvs_mean_pos.append(["Flesch-Kincaid grade", kincaid_completers, kincaid_elicitors])

    for key in statistics_elicitors:
        cvs_mean_pos.append([key, statistics_completers[key], statistics_elicitors[key]])

    meanWordsCompleters, meanSignsCompleters, meanCharsCompleters, meanSentencesCompleters = averageStat(readibility_completers_folder)
    meanWordsElicitors, meanSignsElicitors, meanCharsElicitors, meanSentencesElicitors = averageStat(readibility_elicitors_folder)

    cvs_mean_pos.append(["Words average", meanWordsCompleters, meanWordsElicitors])
    cvs_mean_pos.append(["Signs average", meanSignsCompleters, meanSignsElicitors])
    cvs_mean_pos.append(["Chars average", meanCharsCompleters, meanCharsElicitors])
    cvs_mean_pos.append(["Sentences average", meanSentencesCompleters, meanSentencesElicitors])

    with open(output_csv_filename, 'wb') as fs:
        wr = csv.writer(fs, quoting=csv.QUOTE_NONE) #, delimiter='|', quotechar='',escapechar='\\')
        wr.writerow(csv_attributes)
        for tag in cvs_mean_pos:
            wr.writerow(tag)
    


if __name__ == "__main__":
    #downloadLexicons()

    for result in getEmotionsForCorpus('./suicide-notes-database/elicitors-pp/','*.txt'):
        print result[0]
        for emo in result[1]:
            print emo[0]
            print emo[1]
        print '..................................'
    


    """
    # directories path names
    learning_completers = "./suicide-notes-database/completers/"
    learning_elicitors = "./suicide-notes-database/elicitors/"
    learning_completers_pp = "./suicide-notes-database/completers-pp/"
    learning_elicitors_pp = "./suicide-notes-database/elicitors-pp/"

    tester_completers = "./suicide-notes-database/TESTER/C-pp/"
    tester_elicitors = "./suicide-notes-database/TESTER/E-pp/"
    tester_completers_pp = "./suicide-notes-database/TESTER/C/"
    tester_elicitors_pp = "./suicide-notes-database/TESTER/E/"
     
    saveMeanStatisticsCSV("ml-database/means.csv", learning_completers_pp, learning_elicitors_pp,
        "./suicide-notes-database/parts_of_speech/", "./suicide-notes-database/parts_of_speech_statistics/", ".//post",
        learning_completers, learning_elicitors)
    

    singleFileStatisticsCSV(learning_completers_pp, learning_elicitors_pp,
        "./suicide-notes-database/parts_of_speech_statistics/", "./suicide-notes-database/parts_of_speech/",
        "ml-database/learning_set_completers.csv", "ml-database/learning_set_elicitors.csv",
        learning_completers, learning_elicitors)


    singleFileStatisticsCSV(tester_completers, tester_elicitors,
        "./suicide-notes-database/parts_of_speech_statistics/", "./suicide-notes-database/parts_of_speech/",
        "ml-database/tester_set_completers.csv", "ml-database/tester_set_elicitors.csv",
        tester_completers_pp, tester_elicitors_pp)
    
    """

