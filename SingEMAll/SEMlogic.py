from canoris import *
import time
import sys
import midi


class SequenceNotes():
    def __init__(self):
        self.pitch = self.velocity = self.deltaTime = self.restDuration = 0

class SEMprocess():
    def __init__(self, SingerSelected, SingText):  
        self.sequenceNotes = []
        self.singer = SingerSelected
        
        self.inputText = SingText
        self.stringSequence = ""
        
        if (self.singer == 'lara' ):
            self.language = 'english'
        elif (self.singer == 'ona' ):
            self.language = 'spanish'
        elif (self.singer == 'arnau' ):
            self.language = 'spanish'
            
        #replace <api_key> with your API key!
        Canoris.set_api_key('<api_key>') 

    def processMidiFile(self, MidifilePath):
        self.midiFilePath = MidifilePath
        midifile = midi.MidiFile()
        midifile.open(self.midiFilePath)
        midifile.read()
        midifile.close()

        self.ticklength = 6.0/midifile.ticksPerQuarterNote
        max_pitch = 0
        min_pitch = 47 #C3

        for i in range(len(midifile.tracks)):
            for j in range(len(midifile.tracks[i].events)):
                if(midifile.tracks[i].events[j].type == 'NOTE_ON'):
                    currentSequence = SequenceNotes()
                    if(midifile.tracks[i].events[j].velocity > 0):
                        currentSequence.pitch = midifile.tracks[i].events[j].pitch-12
                        currentSequence.velocity = midifile.tracks[i].events[j].velocity
                        currentSequence.deltaTime = midifile.tracks[i].events[j+1].time/10
                        if(currentSequence.pitch > max_pitch):
                            max_pitch = currentSequence.pitch 
                        if(currentSequence.pitch < min_pitch):
                            min_pitch = currentSequence.pitch 
                    if(midifile.tracks[i].events[j].velocity == 0):
                        currentSequence.restDuration = midifile.tracks[i].events[j+1].time/10
                    self.sequenceNotes.append(currentSequence)
                if(midifile.tracks[i].events[j].type == 'NOTE_OFF'):
                    currentSequence = SequenceNotes()
                    currentSequence.restDuration = midifile.tracks[i].events[j+1].time/10
                    self.sequenceNotes.append(currentSequence)

        #Arranging the pitch to human voice

        #if it is out of range we transpose it
        if (min_pitch<47): # C3 = 47 (MIDI note)
            pitch_shift = 0
            while (min_pitch<47):
                min_pitch = min_pitch + 12
                pitch_shift = pitch_shift+12
            print "pitch_shift =",pitch_shift
            for i in range(len(self.sequenceNotes)):
                if(self.sequenceNotes[i].pitch > 0):
                    self.sequenceNotes[i].pitch = self.sequenceNotes[i].pitch + pitch_shift

        if (max_pitch>84): #C6 = 84 (MIDI note)
            pitch_shift = 0
            while (max_pitch>84):
                max_pitch = min_pitch - 12 
                pitch_shift = pitch_shift+12
            print "pitch_shift =",pitch_shift
            for i in range(len(self.sequenceNotes)):
                if(self.sequenceNotes[i].pitch > 0):
                    self.sequenceNotes[i].pitch = self.sequenceNotes[i].pitch - pitch_shift

    def processRequest(self):
        print "Processing request..."     
        self.translation = Text2Phonemes.translate(self.inputText, self.singer, self.language)
        print self.translation

        self.stringSequence = "<melody ticklength='" + str (self.ticklength) + "'>"

        self.phonem_v = []
        for k in range(len(self.translation['phonemes'])):#First iterate thru words
            for l in range(len(self.translation['phonemes'][k])):#Then iterate thru phoneme group of the word
                phonemeString = " "
                for m in range(len(self.translation['phonemes'][k][l])):
                    phonemeString += self.translation['phonemes'][k][l][m]
                    if(m < len(self.translation['phonemes'][k][l])-1):
                        phonemeString += " "
                self.phonem_v.append(phonemeString)


        #build the sequence for the vocaloid tasks
        k=0
        for h in range(len(self.sequenceNotes)):
            if(self.sequenceNotes[h].velocity == 0):
                self.stringSequence += "<rest duration='" + str(self.sequenceNotes[h].restDuration) + "'/>"
            else:
                self.stringSequence += "<note duration='" + str(self.sequenceNotes[h].deltaTime) + "' " + "pitch='" + str(self.sequenceNotes[h].pitch) + "' velocity='" + str(self.sequenceNotes[h].velocity) + "' phonemes='" + self.phonem_v[k]  + "'/>"
                k = k+1
                if(k == len(self.phonem_v)):
                    k=0


        self.stringSequence += "</melody>"

        print(len(self.stringSequence))

        old = Template.get_template('vocaloid')
        #Delete the current template to update it at the server
        old.delete()
        
        #Operation steps
        steps = [{"operation": "vocaloid", "parameters": {"voice": self.singer, "sequence": "{{ substitute_this }}"}}]

        Template.create_template('vocaloid', steps)
        
        sequence = self.stringSequence
        print sequence
        
        t = Task.create_task('vocaloid', {"substitute_this": sequence})
        
        state = False
        
        #Pool while task is not complete
        while not state:
            time.sleep(1)
            t.update()
            state = t['complete']
            print state
        
        print t['output']
        
        resultFile = File.get_file(t['output'])
        print "Retrieving result"
        resultFile.retrieve(str(os.path.realpath(os.path.dirname(sys.argv[0]))), "workfile.wav")        
        resultFile.delete()#Once having the file, then delete it from the server
