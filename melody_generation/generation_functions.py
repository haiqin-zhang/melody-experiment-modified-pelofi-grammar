import numpy as np
import pandas as pd
import pickle
from music21 import *
from generation_functions import *

#organizes the artificial grammar (which is initially defined as a dictionary) into a pd.DataFrame
#matrix: a dictionary
def organize_matrix(matrix):
  matrix = pd.DataFrame(matrix, index = matrix.keys())
  return matrix

#Gives all the theoretical transition probabilities in the artificial grammar
#matrix: pd.DataFrame
def theo_trans_probs(matrix):
    list = []
    for column in matrix:
        for item in matrix.index:
            if matrix[column][item] != 0:
                list.append([str(item)+str(column), matrix[column][item]])

    df = pd.DataFrame(list, columns = ['Pitches', 'Transition probs'])
    df.set_index('Pitches')
    sorted_df = df.sort_values(by = 'Pitches')
    return sorted_df

#defining different transition matrices describing the artificial grammar

#some mistakes in the original matrix, this should be the one that has been corrected
matrix_pelofi = {
    'A3': [0, 0, 0, 0, 0, 0, 0], #probability of getting to a from starting points a, b, and c respectively
    'Bb3': [.6, 0, 0, 0, 0, 0, 0],
    'C4': [.2, .5, 0, 0, 0.2, 0, 0],
    'C#4': [0, 0, .6, 0, .2, .4, 0],
    'E4': [.2, .5, .2, 0, 0, 0, 0],
    'G4': [0, 0, .2, .4, .6, 0, 0],
    'A4':[0, 0, 0, .6, 0, .6, 1]
}
matrix_pelofi = organize_matrix(matrix_pelofi)
ttp_pelofi = theo_trans_probs(matrix_pelofi)

#modified for bigger distributions in info content
#starts on a low note - take note of this when generating melodies
matrix_lowstart = {
    'A3': [0, 0, 0, 0, 0, 0, 0], #probability of getting to a from starting points a, b, and c respectively
    'Bb3': [.6, 0, 0, 0, 0, 0, 0],
    'C4': [.2, .5, 0, 0, .05, 0, 0],
    'C#4': [0, 0, .9, 0, .9, .4, 0],
    'E4': [.2, .5, .05, 0, 0, 0, 0],
    'G4': [0, 0, .05, .4, .05, 0, 0],
    'A4':[0, 0, 0, .6, 0, .6, 1]
}
matrix_lowstart = organize_matrix(matrix_lowstart)
ttp_lowstart = theo_trans_probs(matrix_lowstart)

#same as matrix above but with A3 and A4 switched
matrix_highstart = {
    'A4': [0, 0, 0, 0, 0, 0, 0], #probability of getting to a from starting points a, b, and c respectively
    'Bb3': [.6, 0, 0, 0, 0, 0, 0],
    'C4': [.2, .5, 0, 0, .05, 0, 0],
    'C#4': [0, 0, .9, 0, .9, .4, 0],
    'E4': [.2, .5, .05, 0, 0, 0, 0],
    'G4': [0, 0, .05, .4, .05, 0, 0],
    'A3':[0, 0, 0, .6, 0, .6, 1]
}
matrix_highstart = organize_matrix(matrix_highstart)
ttp_highstart = theo_trans_probs(matrix_highstart)

####GENERATING MELODIES#############

#markov_melody generates a batch of melodies
#num_melodies: number of melodies to be generated
#length: length of each melody in number of notes
#returns a nested list: [[melody 1],[melody 2]] etc

def markov_melody_lowstart(num_melodies, matrix): #could also randomize lengths more later
  melody_list = []

  while len(melody_list) < num_melodies:
    #define the starting note
    results = ['A3']

    #appending new notes to the starting state until max number of notes reached
    #while len(results) < length:
    while 'A4' not in results:
      new_state = np.random.choice(matrix.index, p = matrix.loc[results[-1]])
      results.append(new_state)
    
    melody_list.append(results)
    file_name = "melody"+str(len(melody_list))+".pkl"
    open_file =open(file_name, "wb")
    pickle.dump(results, open_file)
    open_file.close()

  #melody_list = np.array(melody_list) 
    #can also change to pandas etc later for data analysis
  return melody_list

def markov_melody_highstart(num_melodies, matrix): #could also randomize lengths more later
  melody_list = []

  while len(melody_list) < num_melodies:
    #define the starting note
    results = ['A4']

    #appending new notes to the starting state until max number of notes reached
    #while len(results) < length:
    while 'A3' not in results:
      new_state = np.random.choice(matrix.index, p = matrix.loc[results[-1]])
      results.append(new_state)
    
    melody_list.append(results)
    file_name = "melody"+str(len(melody_list))+".pkl"
    open_file =open(file_name, "wb")
    pickle.dump(results, open_file)
    open_file.close()

  #melody_list = np.array(melody_list) 
    #can also change to pandas etc later for data analysis
  return melody_list
  

#to_midi_exposure takes the list of melodies generated above and converts into MIDI files for a set of exposure melodies (all notes the same length/volume)
#setsize: the number of melodies to be converted (if continuing from markov generation above, it can be len(melody_list))
#saves all the converted midi files
def to_midi_exposure(setsize):
  for i in range(1,setsize+1):
    file = open('melody'+str(i)+".pkl", 'rb')
    melody1 = pickle.load(file)

    stream_current = stream.Stream()

    for j in melody1: 
      newnote = note.Note(j)
      stream_current.append(newnote)

      stream_current.write("midi", "stream"+str(i)+".mid")


#generates 'correct' and 'incorrect' files for each melody. 
#number at end of function denotes which melody is supposed to be the correct answer
#A file is 'correct' if it has a longer duration on notes with high IC
#setsize: number of melodies to be converted, usually len(melody_list)
#target: the note that is supposed to have high IC
#off_target: the note that is supposed to have low IC (ie 'incorrect')
#rewriting the melody generation for forced choice
#first generate melodic examples that have both low and high-IC note|context combinations
#??? wut 2 do???
#for now the function just makes either G or C# the long note; the 'correct' choice is the first choice which makes G longer

def to_midi_forcedchoice_1(setsize, target, off_target):
  for number in range(1, setsize+1):
  #generates the first ('correct') melody
    file = open('melody'+str(number)+'.pkl', 'rb')
    test_melody = pickle.load(file)

    stream_correct = stream.Stream()

    for i in test_melody: 
      if i == target:
        newnote = note.Note(i, duration = duration.Duration(2))
        stream_correct.append(newnote)
      else:
        newnote = note.Note(i, duration = duration.Duration(1))
        stream_correct.append(newnote)

    #generates the second ('incorrect') melody

    stream_incorrect = stream.Stream()

    already_used = False
    for i in test_melody: 
      if i == off_target and already_used == False : #will have to randomize the off-target notes better
        newnote = note.Note(i, duration = duration.Duration(2))
        stream_incorrect.append(newnote)
        already_used = True
      else:
        newnote = note.Note(i, duration = duration.Duration(1))
        stream_incorrect.append(newnote)

    r = note.Rest(duration = duration.Duration(4))
    stream_correct.append(r)
    stream_correct.append(stream_incorrect)
    stream_correct.write('midi', 'test_1correct'+str(number)+'.mid')



#same as above but this time the 'incorrect' choice is the first melody
def to_midi_forcedchoice_2(setsize, target, off_target):
  for number in range(1, setsize+1):
  #generates the first ('correct') melody
    file = open('melody'+str(number)+'.pkl', 'rb')
    test_melody = pickle.load(file) #could make a version without pickle but then the melodies can't be stored...

    stream_incorrect = stream.Stream()

    for i in test_melody: 
      if i == off_target:
        newnote = note.Note(i, duration = duration.Duration(2))
        stream_incorrect.append(newnote)
      else:
        newnote = note.Note(i, duration = duration.Duration(1))
        stream_incorrect.append(newnote)

    #generates the second ('incorrect') melody

    stream_correct = stream.Stream()

    already_used = False
    for i in test_melody: 
      if i == target and already_used == False : #will have to randomize the off-target notes better
        newnote = note.Note(i, duration = duration.Duration(2))
        stream_correct.append(newnote)
        already_used = True
      else:
        newnote = note.Note(i, duration = duration.Duration(1))
        stream_correct.append(newnote)

    r = note.Rest(duration = duration.Duration(4))
    stream_incorrect.append(r)
    stream_incorrect.append(stream_correct)
    stream_incorrect.write('midi', 'test_2correct'+str(number)+'.mid')

#makes a set of melodies where the target note is either an eighth, quarter, half, or whole note.
#setsize: number of melodies (for every melody the function will make a set of 4 corresponding melodies)
#target: eiher a low- or high-IC note
#saves converted midi files
def to_midi_interpret(setsize, target):
  for number in range(1, setsize+1):
  #generates the first ('correct') melody
    file = open('melody'+str(number)+'.pkl', 'rb')
    test_melody = pickle.load(file) #could make a version without pickle but then the melodies can't be stored...

    notelengths = [0.5,1,2,4]
    for length in notelengths:
      stream_final = stream.Stream()
      for i in test_melody: 
        if i == target:
          newnote = note.Note(i, duration = duration.Duration(length))
          stream_final.append(newnote)
        else:
          newnote = note.Note(i, duration = duration.Duration(1))
          stream_final.append(newnote)


      stream_final.write('midi', 'test_interpret'+str(length)+'.mid')

to_midi_interpret(1, 'C#4')



#introducing stringmaker: a very, very stupid way (but it works! at least for linux) to batch convert midi to mp3 files by changing the string that is then fed into a cmd line
#title: a string giving the generic melody title of the midi file, e.g. 'test_correct' (number will be appended to it)
#length: how many melodies are being converted
#returns a big string with one line of command line code for each melody; copy paste into next section to run and convert
#example: stringmaker('test_incorrect', 5)

def stringmaker(title, length):
  newstring = ''
  for i in range(length+1):
    tempstring = '!fluidsynth -ni font.sf2 ' + title + str(i) + '.mid -F ' + title +str(i)+'.mp3 -r 44100'

    newstring = newstring+ '\n' +tempstring

  print(newstring)

