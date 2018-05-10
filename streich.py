#!/usr/bin/env python3

import os
import sh

def main():
    junge = set()
    spezial = {}
    with open('data.csv') as f:
        anfang = True
        for line in f:
            parts = line.strip().split(',')
            if anfang:
                if 'Nimmt nur am Freitagmorgen teil.' in parts[3]:
                    spezial[parts[2]] = (parts[:3], parts[3].split()[-1][:-1])
                if parts[0] == 'Kindergarten':
                    anfang = False
                else:
                    continue
            if ''.join(parts).strip().startswith(''.join(map(str, range(1, 22)))):
                continue
            if ''.join(parts).strip() == '':
                continue
            jung = parts[-1] == '1'
            if jung:
                code = parts[4]
                junge.add(code)
    print(spezial)

    sh.rm('-r', '-f', 'out_streich')
    sh.mkdir('out_streich')
    sh.mkdir('out_streich/lehrer')
    sh.mkdir('out_streich/schueler')
    for fn in os.listdir('out/lehrer'):
        lehrer = fn[3:-4]
        sh.mkdir(f'out_streich/schueler/{lehrer}')
        titleline = ''
        with open(f'out/lehrer/{fn}') as f, open(f'out_streich/lehrer/{fn}', 'w') as of:
            for line in f:
                if line.startswith('Nachname'):
                    of.write(line)
                    titleline = line
                    continue
                parts = line.strip().split(',')
                code = parts[2]
                for s in spezial:
                    if s[:3] == code[:3]:
                        l = spezial[s][0]
                        if len(l) == 3:
                            l.append(lehrer)
                            l.append('Kindergarten')
                            sparts = l[:3] + [''] * 4 + [spezial[s][1]]
                            of.write(','.join(sparts) + '\n')
                            with open(f'out_streich/schueler/{lehrer}/{s}.csv', 'w') as sof:
                                sof.write(titleline)
                                sof.write(','.join(sparts) + '\n')

                if code in junge:
                    parts[4] = ''
                    parts[6] = ''
                of.write(','.join(parts) + '\n')
                with open(f'out/schueler/{lehrer}/{code}.csv') as sf, open(f'out_streich/schueler/{lehrer}/{code}.csv', 'w') as sof:
                    fline = False
                    for sline in sf:
                        if not fline:
                            sof.write(sline)
                            fline = True
                        else:
                            sof.write(','.join(parts) + '\n')
    sh.mkdir('out_streich/kurse')
    for fn in os.listdir('out/kurse'):
        with open(f'out/kurse/{fn}') as f, open(f'out_streich/kurse/{fn}', 'w') as of:
            for line in f:
                parts = line.strip().split(',')
                if parts[0] == 'Dienstag' or parts[0] == 'Donnerstag':
                    if parts[3] in junge:
                        continue
                of.write(line)
            kn = fn.split()[1].split('.')[0]
            for s in spezial.values():
                if s[1] == kn:
                    sparts = ['Freitag'] + s[0]
                    of.write(','.join(sparts) + '\n')





if __name__ == '__main__':
    main()
