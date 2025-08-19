#!/usr/bin/env python

import pypandoc

def markdown(schedule, semester, year, templatedir):
    course = ['## ' + d + '\n' for d in schedule]
    course = [d + '[Fill in class plan]\n\n' if 'NO CLASS' not in d else d for d in course]
    md_args = ['--template=' + templatedir + '/syllabus.md', '--to=markdown',
            '--variable=semester:' + semester.capitalize(), '--variable=year:' + year]
    return pypandoc.convert('\n'.join(course), 'md', 'md', md_args)

def output(schedule, semester, year, fmt, templatedir, outfile):
    md = markdown(schedule, semester, year, templatedir)
    template = templatedir + '/syllabus.' + fmt if templatedir else ""
    if fmt == 'docx':
        template_arg = '--reference-docx=' + template
    else:
        template_arg = '--template=' + template
    pandoc_args = ['--standalone']
    pandoc_args.append(template_arg)
    output = pypandoc.convert(md, fmt, 'md', pandoc_args, outputfile=outfile)
    assert output == ''