#!usr/bin/env python3
"""
Generates PDF report of analysis.iot result.
"""
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        super().__init__()
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'report.iot'
        self.short_description = 'Generates report for analyzed firmware.'
        self.references = [
            '',
        ]
        
        self.date = '2016-11-14'
        self.license = 'GNU GPLv2'
        self.version = '1.1'
        self.tags = [
            'IoT',
            'Internet of Things',
            'CVE',
            'report',
        ]
        self.description = """This module uses reportlab library to generate report of gathered data. Report will be generated on local system."""
        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            #'ACTIVEROOT': Parameter(mandatory=True, description='System to work with'),
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'TAG': Parameter(mandatory=True, description='Tag of firmware data in TB'),
            'OUTPUTFILE': Parameter(mandatory=True, description='Output file path'),
        }
    

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        result = CHECK_SUCCESS
        outputfile = self.parameters['OUTPUTFILE'].value

        # can import reportlab?
        try:
            import reportlab
        except:
            if not silent:
                log.err('Cannot import \'reportlab\' library.')
            result = CHECK_FAILURE
        
        # can create file?
        if not io.can_write('/', outputfile) and not io.can_create('/', outputfile):
            if not silent:
                log.err('Cannot create \'%s\'.' % outputfile)
            result = CHECK_FAILURE
            
        return result
    
    def run(self):
        outputfile = self.parameters['OUTPUTFILE'].value
        tag = self.parameters['TAG'].value
        silent = positive(self.parameters['SILENT'].value)

        #from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import KeepTogether, SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet
        styles = getSampleStyleSheet()

        doc = SimpleDocTemplate(outputfile, pagesize=A4)
        entries = []
        
        #print(styles.list())
        # PREPARE STYLES
        titlestyle = styles['Title']
        heading1style = styles['Heading1']
        headingstyle = styles['Heading2']
        textstyle = styles['BodyText']

        # HEADING
        entries.append(Paragraph('<para align=center spaceAfter=20>VULNERABILITY ANALYSIS REPORT</para>', titlestyle))
        

        cves_lists = [x.get('cves') for x in tb[tag+'_filesystems']] if tag+'_filesystems' in tb else []
        exploits = {} if tag+'_exploits' not in tb else tb[tag+'_exploits']
        exploit_count = len(set([x for k,v in exploits.items() for x in v]))

        # ADD GENERAL INFO
        if tag+'_general' in tb:
            #entries.append(Paragraph('<para spaceBefore=30>General info<para>', headingstyle))
            data = [[x[0]+':', ', '.join(x[1]) if type(x[1]) in [list, tuple, set] else x[1]] for x in tb[tag+'_general']]
            if len(cves_lists) > 0:
                data.append(['Vulnerable:', Paragraph('<para><font color=%s><b>%s</b></font> (<i>%s</i> accuracy)</para>' % (('red', 'YES', tb[tag+'_accuracy']) if max([0]+[len(x) for x in cves_lists]) else ('green', 'NO', tb[tag+'_accuracy'])), textstyle)])
                data.append(['Known exploits:', Paragraph('<para><font color=%s><b>%s</b></font></para>' % (('red', exploit_count) if exploit_count>0 else ('green', exploit_count)), textstyle)])
            entries.append(Table(data, None, None, hAlign='LEFT'))
        
        # for each fs
        fscount = -1
        for fs in tb[tag+'_filesystems'] if tag+'_filesystems' in tb else []:
            fscount += 1
            entries.append(Paragraph('<para spaceBefore=20>File System #%d<para>' % (fscount), heading1style))
            data = [['Root:', fs['name']]]
            entries.append(Table(data, None, None, hAlign='LEFT'))
        
            # ADD SYSTEM INFO
            if 'system' in fs:
                entries.append(Paragraph('<para spaceBefore=20>System info<para>', headingstyle))
                data = [[x[0]+':', ', '.join(x[1]) if type(x[1]) in [list, tuple, set] else x[1]] for x in fs['system']+fs['os']]
                t = Table(data, None, None, hAlign='LEFT')
                t.setStyle(TableStyle([        
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                entries.append(t)
       

            # ADD CRON ENTRIES
            data = []
            tospan = []
            if 'cron' in fs:
                for linec in range(len(fs['cron'])):
                    line = fs['cron'][linec]
                    if len(re.split('[ \t]+', line[0]))==1:
                        l = [line[0], '', '', '', '', line[1], Paragraph('<para>%s</para>' % (line[2]), textstyle)]
                        tospan.append(linec)
                    else:
                        l = re.split('[ \t]+', line[0])[:5]+[line[1], Paragraph('<para>%s</para>' %(line[2]), textstyle)]
                    data.append(l)
                if len(data)>0:
                    entries.append(Paragraph('<para>Cron entries:<para>', headingstyle))
                    t=Table(data, (None, None, None, None, None, None, 11*cm), None, hAlign='LEFT')
                    t.setStyle(TableStyle([('SPAN', (0, x), (4, x)) for x in tospan]+
                                          [('%sPADDING' % x, (0, 0), (-1, -1), 0) for x in ['TOP', 'BOTTOM']]+
                                          [('%sPADDING' % x, (0, 0), (-1, -1), 2) for x in ['LEFT', 'RIGHT']]+
                                          [
                                              ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                              #('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                          ]
                                         ))
                    entries.append(t)


            # ADD CVE SUMMARY
            entries.append(Paragraph('<para spaceBefore=30>Vulnerable packages</para>', headingstyle))
            data = [['Package', 'Version', 'Vulnerabilities', '', ''], ['', '', Paragraph('<para textColor=red align=center><b>HIGH</b></para>', textstyle), Paragraph('<para textColor=orange align=center><b>MEDIUM</b></para>', textstyle), Paragraph('<para textColor=yellowgreen align=center><b>LOW</b></para>', textstyle)]]
            vulnerable = {}
            totals = [0, 0, 0]
            if 'cves' in fs:
                for x in fs['cves']:
                    key = (x[1], x[14])
                    if key not in vulnerable:
                        vulnerable[key] = [0, 0, 0]
                    vulnerable[key][(0 if x[5] == 'High' else (1 if x[5] == 'Medium' else 2))] += 1
                notnull = lambda x: x if x > 0 else ''
            for x in sorted(vulnerable.keys(), key=lambda x: x[0]):
                name = self.get_name_with_origin(x[0])
                data.append((name, self.limit(x[1], 20), notnull(vulnerable[x][0]), notnull(vulnerable[x][1]), notnull(vulnerable[x][2])))
                for i in range(0, 3):
                    totals[i] += vulnerable[x][i]
            data.append(['Total:', '', totals[0], totals[1], totals[2]])
            data.append(['', '', sum(totals), '', ''])
            
            tvulnerable = Table(data, (6*cm, 4*cm, 2*cm, 2*cm, 2*cm), None, hAlign='LEFT')
            tvulnerable.setStyle(TableStyle([
                ('SPAN', (0, 0), (0, 1)), # product
                ('SPAN', (1, 0), (1, 1)), # version
                ('SPAN', (-3, 0), (-1, 0)), # vulnerabilities
                ('SPAN', (0, -2), (1, -1)), # total
                ('SPAN', (-3, -1), (-1, -1)), # grand total
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            entries.append(tvulnerable)
            
            # ADD SPECIFIC CVEs
            if 'cves' in fs and len(fs['cves'])>0:
                entries.append(Paragraph('<para spaceBefore=30>Detected vulnerabilities<para>', headingstyle))
                # exploitable first
                for c in sorted(fs['cves'], key=lambda x: x[4] not in exploits): 
                    if len(c) < 14:
                        continue
                    if c[6] == '2.0': # CVSS 2.0
                        description = c[12].replace('<', '&lt;').replace('>', '&gt;')
                        para_exploits = '' if c[4] not in exploits.keys() else Paragraph('<para align=justify>Exploits: '+', '.join(exploits[c[4]])+'</para>', textstyle)
                        data = [['', c[4], '%s %s\n(%s %s %s)\n' % (self.get_name_with_origin(c[1]), self.limit(c[14], 20), c[0], c[1], c[2]), 'Base:', c[8]], ['', '', '', 'Impact:', c[9]], ['', '', '', 'Exploitability:', c[10]], ['', c[11], '', 'Score:', c[7]], [Paragraph('<para align=justify>'+description+'</para>', textstyle), '', '', '', ''], [para_exploits, '', '', '', '']]
                    else:
                        data = []
                    t = Table(data, colWidths=(0.5*cm, 6*cm, 7*cm, 2.5*cm, 1.5*cm))
                    color = colors.yellow # low severity
                    if c[5] == 'Medium':
                        color = colors.orange
                    elif c[5] == 'High':
                        color = colors.salmon
                    t.setStyle(TableStyle([
                        #('GRID', (0, -2), (-1, -2), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        #('BACKGROUND', (0, 0), (-1, 3), color),
                        ('BACKGROUND', (0, 0), (0, 3), color),
                        ('SPAN', (0, -1), (-1, -1)), # exploit
                        ('SPAN', (0, -2), (-1, -2)), # description
                        ('SPAN', (1, 0), (1, 2)), # cve
                        ('SPAN', (2, 0), (2, -3)), # package
                        ('ALIGN', (3, 0), (3, 4), 'RIGHT'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('FONTSIZE', (1, 0), (1, 0), 15), # cve
                    ]))
                    entries.append(KeepTogether(t))
            entries.append(PageBreak()) # for every FS
        doc.build(entries)
        if not silent:
            log.ok('Report generated.')

        return None
    
    def get_name_with_origin(self,  name):
        tag = self.parameters['TAG'].value
        if name in tb[tag+'_fake_packages']:
            name += ' (detected)'
        elif name in tb[tag+'_alias_packages']:
            name += ' (alias)'
        return name
        
    
    def limit(self, string, maxlen):
        if len(string)>maxlen-3:
            return string[:maxlen-3]+'...'
        return string

    
lib.module_objects.append(Module())
