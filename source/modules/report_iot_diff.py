#!usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'report.iot.diff'
        self.short_description = 'Generates diff report for 2 pieces of firmware.'
        self.references = [
            '',
        ]
        
        self.date = '2016-11-24'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'IoT',
            'Internet of Things',
            'CVE',
            'report',
            'diff',
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
            'TAG1': Parameter(mandatory=True, description='Tag of first firmware data in TB'),
            'TAG2': Parameter(mandatory=True, description='Tag of second firmware data in TB'),
            'OUTPUTFILE': Parameter(mandatory=True, description='Output file path'),
            'DESIRED': Parameter(value='new common old', mandatory=False, description='What CVEs to print (any combination of old, common, new)'),
        }
    

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        result = CHECK_SUCCESS
        outputfile = self.parameters['OUTPUTFILE'].value
        desired = self.parameters['DESIRED'].value.split(' ')

        # desired correct?
        for d in desired:
            if d.lower() not in ['old', 'new', 'common']:
                if not silent:
                    log.err('DESIRED cannot be %s.' % d)
                result = CHECK_FAILURE
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
        tag1 = self.parameters['TAG1'].value
        tag2 = self.parameters['TAG2'].value
        desired = self.parameters['DESIRED'].value.split(' ')

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
        samplestyle = styles['Heading1']
        headingstyle = styles['Heading2']
        textstyle = styles['BodyText']

        entries.append(Paragraph('<para align=center spaceAfter=20>FIRMWARE VULNERABILITY ANALYSIS REPORT</para>', titlestyle))
        
        for tag in [tag1, tag2]:
            # ADD GENERAL INFO
            entries.append(Paragraph('<para spaceBefore=30><i>%s</i> sample<para>' % (tag), samplestyle))
            data = [[x[0]+':', ', '.join(x[1]) if type(x[1]) in [list, tuple] else x[1]] for x in tb[tag+'_general']]
            data.append(['Vulnerable:', Paragraph('<para textColor=%s><b>%s</b></para>' % ('red', 'YES') if len(tb[tag+'_cves'])>0 else ('green', 'NO') , textstyle)])
            entries.append(Table(data, None, None, hAlign='LEFT'))
            
            
            
            # ADD SYSTEM INFO
            entries.append(Paragraph('<para spaceBefore=20>System info<para>', headingstyle))
            data = [[x[0]+':', ', '.join(x[1]) if type(x[1]) in [list, tuple] else x[1]] for x in tb[tag+'_system']]
            entries.append(Table(data, None, None, hAlign='LEFT'))
       
    
    
            # ADD VULNERABLE TABLE
            entries.append(Paragraph('<para spaceBefore=30>Vulnerable packages<para>', headingstyle))
            data = [['Package', 'Version', 'Vulnerabilities', '', ''], ['', '', Paragraph('<para textColor=red align=center><b>HIGH</b></para>', textstyle), Paragraph('<para textColor=orange align=center><b>MEDIUM</b></para>', textstyle), Paragraph('<para textColor=yellowgreen align=center><b>LOW</b></para>', textstyle)]]
            vulnerable = {}
            totals = [0, 0, 0]
            for x in tb[tag+'_cves']:
                #print(x)
                #print(x[13])
                key = (x[1], x[14])
                #print(key)
                if key not in vulnerable:
                    vulnerable[key] = [0, 0, 0]
                vulnerable[key][(0 if x[5] == 'High' else (1 if x[5] == 'Medium' else 2))] += 1
            notnull = lambda x: x if x > 0 else ''
            for x in sorted(vulnerable.keys(), key=lambda x: x[0]):
                data.append((x[0], x[1], notnull(vulnerable[x][0]), notnull(vulnerable[x][1]), notnull(vulnerable[x][2])))
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
            
        # ADD DESIRED CVEs
        for d in desired:
            cvedata = None
            title = ''
            
            if d.lower() == 'old':
                title = 'Fixed vulnerabilities'
                cvedata = [c for c in tb[tag1+'_cves'] if c[4] not in [x[4] for x in tb[tag2+'_cves']]]
            elif d.lower() == 'common':
                title = 'Vulnerabilities present in both samples'
                cvedata = [c for c in tb[tag1+'_cves'] if c[4] in [x[4] for x in tb[tag2+'_cves']]]
            elif d.lower() == 'new':
                title = 'New vulnerabilities'
                cvedata = [c for c in tb[tag2+'_cves'] if c[4] not in [x[4] for x in tb[tag1+'_cves']]]

            if cvedata is None:
                continue
            
            # ADD CVEs
            entries.append(Paragraph('<para spaceBefore=30>%s<para>' % (title), headingstyle))
            for c in cvedata:
                if len(c) < 14:
                    continue
                if c[6] == '2.0': # CVSS 2.0
                    data = [['', c[4], '%s %s\n(%s %s %s)\n' % (c[1], c[14], c[0], c[1], c[2]), 'Base:', c[8]], ['', '', '', 'Impact:', c[9]], ['', '', '', 'Exploitability:', c[10]], ['', c[11], '', 'Score:', c[7]], [Paragraph('<para align=justify>'+c[12]+'</para>', textstyle), '', '', '', ''], ['', '', '', '', '']]
                else:
                    data = []
                t = Table(data, colWidths=(0.5*cm, 8*cm, 5*cm, 2.5*cm, 1.5*cm))
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
    
lib.module_objects.append(Module())
