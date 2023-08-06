import os.path
from chardet.universaldetector import UniversalDetector


def guess_file_encoding(path, max_line=1000):
    if not os.path.isfile(path):
        raise ValueError(f'guess_file_encoding: {path} is not a file')
    detector = UniversalDetector()
    detector.reset()

    if path.endswith(".tmx"):
        with open(path,"r") as f, open(path,"rb") as fb:
            source = True
            i = 1
            for line, line_bits in zip(f, fb):
                src_seg = line.split("<seg>")
                if len(src_seg)>1: 
                    if source:
                        src_seg = src_seg[1]
                        src_seg = src_seg.split("</seg>")[0]
                        detector.feed(line_bits)
                        i = i + 1
                        source = False
                    else:
                        source = True

                if i > max_line or detector.done:
                    break

    else:
        with open(path, "rb") as f:
            for i, line in enumerate(f):
                detector.feed(line)
                if detector.done:
                    break
                if i!=0 and i%max_line == 0:
                    break
    detector.close()

    # Corrección de fallo de la librería que confunde los emojis en utf-8 con encoding Windows-1254 y lenguage turco
    if detector.result['encoding'] == 'Windows-1254' and detector.result['language'] == 'Turkish':
        return 'utf-8'

    # Leer ascii como utf-8 puesto que son equivalentes
    if detector.result['encoding'] == 'ascii':
        return 'utf-8'

    return detector.result['encoding']