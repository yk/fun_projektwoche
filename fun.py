#!/usr/bin/env python3

import logging
from collections import namedtuple
import random
from matplotlib import pyplot as plt
from tqdm import trange
import sh
import itertools as itt


Kind = namedtuple('Kind', 'vname nname code kprio kstreich lehrer stufe grobstufe')
NK = 21
NT = 5
KMAX = 15
TAGE = ('Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag')
NITERS = 1000


def generate(kinder):
    klist = []
    for k in kinder.values():
        kprio = list(k.kprio)
        kother = list(set(range(NK)) - k.kprio - k.kstreich)

        random.shuffle(kprio)
        random.shuffle(kother)
        klist.append((k.code, kprio + kother))


    tage = [[set() for _ in range(NK)] for _ in range(NT)]

    for _ in range(5):
        random.shuffle(klist)
        for code, possible in klist:
            for p in possible:
                random.shuffle(tage)
                zugeteilt = False
                for t in tage:
                    kurs = t[p]
                    if len(kurs) >= KMAX:
                        continue
                    if len(kurs) > 0:
                        if kinder[code].grobstufe != kinder[next(iter(kurs))].grobstufe:
                            continue
                    kurs.add(code)
                    possible.remove(p)
                    zugeteilt = True
                    break

                if zugeteilt:
                    break

            assert zugeteilt

    random.shuffle(tage)

    zuteil = {k: [] for k in kinder}

    min_kg = KMAX+1
    for t, tname in zip(tage, TAGE):
        for kidx, k in enumerate(t):
            kg = len(k)
            assert kg <= KMAX
            min_kg = min(kg, min_kg)
            for c in k:
                zuteil[c].append(kidx)

    for z in zuteil.values():
        assert len(set(z)) == len(z)

    min_np = 4
    for k in kinder.values():
        zt = zuteil[k.code]
        np = sum(p in zt for p in k.kprio)
        assert np >= 1
        min_np = min(np, min_np)
        if k.code == 'PMa12':
            assert np >= 2
        ns = sum(p in zt for p in k.kstreich)
        assert ns == 0

    return tage, zuteil, min_kg, min_np

def main():
    anfang = True
    klassenlehrer = ''
    stufe = ''
    grobstufe = ''
    kinder = dict()
    with open('data.csv') as f:
        for line in f:
            elements = line.strip().split(',')

            if elements[0] == 'Kindergarten':
                anfang = False

            if anfang:
                continue
            if len(''.join(elements)) == 0:
                continue
            if ''.join(elements) == ''.join(map(str, range(1,22))):
                continue

            if elements[0] != '':
                stufe = elements[0]
                grobstufe = 'alt' if stufe in ('Oberstufe', 'Mittelstufe') else 'jung'
            if elements[1] != '':
                klassenlehrer = elements[1]

            nname, vname, code = elements[2:5]

            kprio = set()
            kstreich = set()

            for idx, e in enumerate(elements[5:]):
                if e == '0':
                    kstreich.add(idx)
                elif e == '1':
                    kprio.add(idx)

            if len(kprio) > 3:
                logging.warn(f'{vname} {nname} hat mehr als 3 prio')
            if len(kstreich) > 5:
                logging.warn(f'{vname} {nname} hat mehr als 5 streich')

            kinder[code] = Kind(vname, nname, code, kprio, kstreich, klassenlehrer, stufe, grobstufe)

    sols = []
    for _ in trange(NITERS):
        try:
            sol = generate(kinder)
            sols.append(sol)
        except AssertionError:
            pass
    print(f'{len(sols)} valid solutions computed')

    bs = sols[0]
    for s in sols[1:]:
        if s[-1] > bs[-1]:
            bs = s
            continue
        if s[-1] == bs[-1] and s[-2] > bs[-2]:
            bs = s

    tage, zuteil, min_kg, min_np = bs
    print(f'best solution has lowest number of prio: {min_np} and lowest ksize: {min_kg}')

    for t, tname in zip(tage, TAGE):
        kgs = [len(k) for k in t]
        plt.figure()
        plt.hist(kgs, KMAX+1, (0, KMAX+1), align='left')
        plt.xticks(list(range(KMAX+1)))
        plt.title(tname)
        print(f'kleinster kurs {tname}: {min(kgs)}')


    nps = []
    for k in kinder.values():
        zt = zuteil[k.code]
        np = sum(p in zt for p in k.kprio)
        nps.append(np)
    plt.figure()
    plt.hist(nps, 4, (0, 4), align='left')
    plt.xticks(list(range(4)))
    plt.title('num prio')
    plt.draw()
    print(f'kind mit wenigsten prios: {min(nps)}')


    sh.rm('-r', '-f', 'out')
    sh.mkdir('out')
    for kn in range(NK):
        with open(f'out/Kurs {kn+1}.csv', 'w') as f:
            f.write('Tag,Nachname,Vorname,Code,Lehrperson,Stufe\n')
            for t, tname in zip(tage, TAGE):
                kurs = t[kn]
                for c in sorted(kurs):
                    kind = kinder[c]
                    line = ','.join((tname, kind.nname, kind.vname, kind.code, kind.lehrer, kind.stufe)) + '\n'
                    f.write(line)

    
    keyfunc = lambda k: k.lehrer
    for l, lg in itt.groupby(sorted(list(kinder.values()), key=keyfunc), keyfunc):
        with open(f'out/LP {l}.csv', 'w') as f:
            f.write('Nachname,Vorname,Code,Montag,Dienstag,Mittwoch,Donnerstag,Freitag\n')
            for k in sorted(lg, key=lambda k: k.code):
                line = ','.join([k.nname, k.vname, k.code] + list(str(z+1) for z in zuteil[k.code])) + '\n'
                f.write(line)


    # plt.show()


if __name__ == '__main__':
    main()
