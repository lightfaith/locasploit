#!usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
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
        self.version = '1.0'
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
        self.packathors = ['dpkg', 'opkg']

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

        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import KeepTogether, SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        styles = getSampleStyleSheet()

        doc = SimpleDocTemplate(outputfile, pagesize=A4)
        entries = []
        
        #print(styles.list())
        # PREPARE STYLES
        titlestyle = styles['Title']
        headingstyle = styles['Heading2']
        textstyle = styles['BodyText']

        entries.append(Paragraph('<para align=center spaceAfter=20>FIRMWARE VULNERABILITY ANALYSIS REPORT</para>', titlestyle))
        

        if tag+'_general' in tb:
            # ADD GENERAL INFO
            #entries.append(Paragraph('<para spaceBefore=30>General info<para>', headingstyle))
            data = [[x[0]+':', ', '.join(x[1]) if type(x[1]) in [list, tuple] else x[1]] for x in tb[tag+'_general']]
            if tag+'_cves' in tb:
                data.append(['Vulnerable:', Paragraph('<para textColor=%s><b>%s</b></para>' % (('red', 'YES') if len(tb[tag+'_cves'])>0 else ('green', 'NO')) , textstyle)])
            entries.append(Table(data, None, None, hAlign='LEFT'))
        
        
        
        # ADD SYSTEM INFO
        if tag+'_cves' in tb:
            entries.append(Paragraph('<para spaceBefore=20>System info<para>', headingstyle))
            data = [[x[0]+':', ', '.join(x[1]) if type(x[1]) in [list, tuple] else x[1]] for x in tb[tag+'_system']+tb[tag+'_os']]
            t = Table(data, None, None, hAlign='LEFT')
            t.setStyle(TableStyle([        
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            entries.append(t)
   

        # ADD CRON ENTRIES
        data = []
        tospan = []
        if tag+'_cron' in tb:
            for linec in range(len(tb[tag+'_cron'])):
                line = tb[tag+'_cron'][linec]
                if len(re.split('[ \t]+', line[0]))==1:
                    l = [line[0], '', '', '', '', line[1], Paragraph('<para>%s</para>' % (line[2]), textstyle)]
                    tospan.append(linec)
                else:
                    l = re.split('[ \t]+', line[0])[:5]+[line[1], Paragraph('<para>%s</para>' %(line[2]), textstyle)]
                data.append(l)
            if len(data)>0:
                entries.append(Paragraph('<para>Cron entries:<para>', headingstyle))
                #t=Table(data, (2*cm, 0.5*cm, 0.5*cm, 0.5*cm, 0.5*cm, 2*cm, 12*cm), [0.5*cm]*len(data), hAlign='LEFT')
                t=Table(data, (None, None, None, None, None, None, 11*cm), None, hAlign='LEFT')
                #t=Table(data, (None, None, None, None, None, None, 13*cm), None, hAlign='LEFT')
                t.setStyle(TableStyle([('SPAN', (0, x), (4, x)) for x in tospan]+
                [('%sPADDING' % x, (0, 0), (-1, -1), 0) for x in ['TOP', 'BOTTOM']]+
                [('%sPADDING' % x, (0, 0), (-1, -1), 2) for x in ['LEFT', 'RIGHT']]+
                [
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    #('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    #('LEFTPADDING', (0, 0), (-1, -1), 0),
                    #('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ]
                ))
                entries.append(t)


        # ADD VULNERABLE LIST
        entries.append(Paragraph('<para spaceBefore=30>Vulnerable packages</para>', headingstyle))
        data = [['Package', 'Version', 'Vulnerabilities', '', ''], ['', '', Paragraph('<para textColor=red align=center><b>HIGH</b></para>', textstyle), Paragraph('<para textColor=orange align=center><b>MEDIUM</b></para>', textstyle), Paragraph('<para textColor=yellowgreen align=center><b>LOW</b></para>', textstyle)]]
        vulnerable = {}
        totals = [0, 0, 0]
        if tag+'_cves' in tb:
            for x in tb[tag+'_cves']:
                key = (x[1], x[14])
                if key not in vulnerable:
                    vulnerable[key] = [0, 0, 0]
                vulnerable[key][(0 if x[5] == 'High' else (1 if x[5] == 'Medium' else 2))] += 1
            notnull = lambda x: x if x > 0 else ''
        for x in sorted(vulnerable.keys(), key=lambda x: x[0]):
            data.append((x[0], self.limit(x[1], 20), notnull(vulnerable[x][0]), notnull(vulnerable[x][1]), notnull(vulnerable[x][2])))
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
        
        # ADD CVEs
        if tag+'_cves' in tb:
            entries.append(Paragraph('<para spaceBefore=30>Detected vulnerabilities<para>', headingstyle))
            for c in tb[tag+'_cves']:
                if len(c) < 14:
                    continue
                if c[6] == '2.0': # CVSS 2.0
                    data = [['', c[4], '%s %s\n(%s %s %s)\n' % (c[1], self.limit(c[14], 20), c[0], c[1], c[2]), 'Base:', c[8]], ['', '', '', 'Impact:', c[9]], ['', '', '', 'Exploitability:', c[10]], ['', c[11], '', 'Score:', c[7]], [Paragraph('<para align=justify>'+c[12]+'</para>', textstyle), '', '', '', ''], ['', '', '', '', '']]
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
                    #('LINEBEFORE', (-1, 0), (-1, -3), 1, color),
                    #('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.black),
                    #('LINEABOVE', (0, -2), (-1, -2), 1, colors.black),
                    ('SPAN', (0, -2), (-1, -2)), # description
                    ('SPAN', (1, 0), (1, 2)), # cve
                    ('SPAN', (2, 0), (2, -3)), # package
                    ('ALIGN', (3, 0), (3, 4), 'RIGHT'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('FONTSIZE', (1, 0), (1, 0), 15), # cve
                ]))
                entries.append(KeepTogether(t))
        doc.build(entries)

        # # # # # # # #
        return None
    
    def limit(self, string, maxlen):
        if len(string)>maxlen-3:
            return string[:maxlen-3]+'...'
        return string

    
lib.module_objects.append(Module())
