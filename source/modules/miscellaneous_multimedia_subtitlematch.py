#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'miscellaneous.multimedia.subtitlematch'
        self.short_description = 'Helps with syncing subtitles.'
        self.references = [
            '',
        ]
        
        self.date = '2016-01-28'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'multimedia',
            'subtitles',
            'srt',
            'sync', 'synchronization',
            'offset', 'delay', 'speed'
        ]
        self.description = """
This module can alter the time information in .srt files to provide the best experience. It can deal with delays and incorrect speeds in defined intervals. 

User must define:
    type of problem (delay, speed)
    file format
    input file
    output file
    time of sentence heard (in the same form as seen in input file)
    time of sentence seen in subtitles (in the same form as seen in input file)
    start of the bad part (in the same form as seen in input file, undefined = start)
    end of the bad part (in the same form as seen in input file, undefined = end)

If subtitle speed is incorrect, the delay will deteriorate through time. For the best precision, pick the sentence from the end of a movie.

Supported formats:
    .srt
"""
        
        
        self.dependencies = {
        }
        self.changelog = """
1.0: .srt support added
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'TYPE': Parameter(value='', mandatory=True, description='0 = offset, 1 = speed'),
            'FORMAT': Parameter(value='srt', mandatory=True, description='File format'),
            'INPUTFILE': Parameter(value='', mandatory=True, description='Input file'),
            'OUTPUTFILE': Parameter(value='', mandatory=True, description='Output file'),
            'HEARD': Parameter(value='', mandatory=True, description='Time a sentence has been heard'),
            'SEEN': Parameter(value='', mandatory=True, description='Time a sentence has been seen in subtitles'),
            'START': Parameter(value='', mandatory=False, description='Start of the bad part'),
            'END': Parameter(value='', mandatory=False, description='End of the bad part'),
        }

    def check(self, silent=None):
        result = CHECK_SUCCESS
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        # check type
        if self.parameters['TYPE'].value not in ['0', '1']:
            if not silent:
                log.err('Value for \'TYPE\' (%s) is not supported.' % self.parameters['TYPE'].value)    
            result = CHECK_FAILURE
        # check the files for readability/writability
        if not os.access(self.parameters['INPUTFILE'].value, os.R_OK):
            if not silent:
                log.err('File %s cannot be read.' % self.parameters['INPUFILE'].value)
            result = CHECK_FAILURE
        if not os.access(os.path.dirname(os.path.realpath(self.parameters['OUTPUTFILE'].value)), os.W_OK):
            if not silent:
                log.err('File %s cannot be written.' % self.parameters['OUTPUTFILE'].value)
            result = CHECK_FAILURE
        
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        # # # # # # # #     
        
        # for a specific format
        if self.parameters['FORMAT'].value == 'srt':
            # check parameters
            pattern = re.compile('^[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3}$')
            if not re.match(pattern, self.parameters['HEARD'].value):
                log.err('\'HEARD\' parameter is not in the correct form (%s).' % self.parameters['HEARD'].value)
                return None
            if not re.match(pattern, self.parameters['SEEN'].value):
                log.err('\'SEEN\' parameter is not in the correct form (%s).' % self.parameters['SEEN'].value)
                return None
            if not re.match(pattern, self.parameters['START'].value) and self.parameters['START'].value != '':
                log.err('\'START\' parameter is not in the correct form (%s).' % self.parameters['START'].value)
                return None
            
            # calculate delay and speed
            voice = self.parameters['HEARD'].value
            subti = self.parameters['SEEN'].value
            speed = float(self.getms(subti))/float(self.getms(voice))
            delay = self.getms(subti)-self.getms(voice)
            if not silent:
                if self.parameters['TYPE'].value == '0': # offset
                    log.info('Calculated subtitle delay: %d ms.' % delay)
                else:
                    log.info('Calculated relative subtitle speed: %f.' % speed)
            
            # do the magic
            with open(self.parameters['INPUTFILE'].value, 'r') as fin:
                with open(self.parameters['OUTPUTFILE'].value, 'w') as fout:
                    prevline = ''
                    lines = [x for x in fin.read().splitlines()]
                    for l in lines:
                        if '-->' in l and prevline.strip().isdigit():
                            parts = [x.strip() for x in l.split('-->')]
                            newparts = []
                            for p in parts:
                                if (self.parameters['START'].value == '' or getms(self.parameters['START'].value)<self.getms(p) and
                                self.parameters['END'].value == '' or getms(self.parameters['END'].value)>self.getms(p)): # in desired interval, recompute
                                    if self.parameters['TYPE'].value == '0':
                                        newval = self.getms(p) - delay
                                    elif self.parameters['TYPE'].value == '1':
                                        newval = self.getms(p) / speed
                                    else:
                                        log.err('TYPE %s undefined for %s format' % (self.parameters['TYPE'].value, self.parameters['FORMAT'].value))
                                        return None
                                else: # not in desired interval, leave it
                                    newval = self.getms(p)
                                # parse and prepare for writing
                                h = newval/3600000
                                newval %= 3600000
                                m = newval/60000
                                newval %= 60000
                                newval /= 1000
                                newparts.append(('%02d:%02d:%06.3f' % (h, m, newval)).replace('.', ','))
                            #print 'orig: %s --> %s' % (parts[0], parts[1])
                            #print 'new: %s --> %s' % (newparts[0], newparts[1])
                            #print 
                            fout.write('%s --> %s\r\n' % (newparts[0], newparts[1]))
                        else:
                            fout.write(l+'\r\n')
                        prevline = l
                if not silent:
                    log.ok('\'%s\' created successfuly.' % self.parameters['OUTPUTFILE'].value)
            # end of .srt parsing

        else: # unrecognized format
            if not silent:
                log.err('Format \'%s\' is not supported.' % self.parameters['FORMAT'].value)
        # # # # # # # #
        return None
    
    
    def getms(self, p):
        # get number of miliseconds from time in specified format
        if(self.parameters['FORMAT'].value) == 'srt': # hh:mm:ss,sss
            return int(p[-3:]) + int(p[-6:-4])*1000 + int(p[3:5])*60000 + int(p[:2])*3600000 
        else:
            return 0


lib.module_objects.append(Module())
