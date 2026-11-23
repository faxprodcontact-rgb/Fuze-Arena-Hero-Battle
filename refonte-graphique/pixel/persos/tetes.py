# Les têtes des héros, dessinées pixel par pixel (une lettre = une couleur ; '.' = rien). Vues de trois quarts, tournées
# vers la droite ; la lumière vient d'en haut à droite (clair à droite, ombre à gauche). Les deux yeux ont la même forme.
# BLINK : les lettres des yeux remplacées pour le clignement (yeux fermés = un trait sombre).
# Vérifier : python3 persos/tetes.py sortie.png  (les cinq têtes en grand, ouvertes puis fermées).

ELDRA = [
    ".......KK..KK..KK....",
    "......KFLKKFLKKFLK...",
    ".....KfFFFFFFFFFFLK..",
    "....KfFFFFFFFFFFFLLK.",
    "...KffFFFFFFFFFFFFLK.",
    "..KdfFFFFFFFFFFFFFLK.",
    "..KdgGGGGGGGYRGGGGYK.",
    "..KdggggGGGGGrGGGGGK.",
    "..KddfKSSSSSSSSSSSHK.",
    ".KKKdfKbbSSSSSSSSbbK.",
    "KFFLKfKSbbbSSSbbbSHK.",
    "KFEEFfKSwppSSSwppSHK.",
    "KFEsFfKSsssSsSsssSSSK",
    "KFEEFfKSSSSSssSSSSSSK",
    "KfFFKfKSSSSSSSSSSmSK.",
    ".KKKfKsSSSmtttttmSK..",
    "......KSSSsmmmmmSSK..",
    ".......KSSssssSSK....",
    "........KsSSSSHK.....",
    ".........KKKKKK......",
]
ELDRA_C = {'K': '#2a140c', 'd': '#341c10', 'f': '#5a321e', 'F': '#865234', 'L': '#aa7450',
           'g': '#b07418', 'G': '#eab036', 'Y': '#ffd870', 'R': '#d02818', 'r': '#8a1010',
           'S': '#f6c098', 's': '#d48a64', 'H': '#ffdcbc', 'E': '#e0a080',
           'b': '#3a1e10', 'w': '#ffffff', 'p': '#4a1a08', 'm': '#5a1a12', 't': '#ffffff'}
ELDRA_BLINK = {'w': 'b', 'p': 'b'}

ROOK = [
    "............KK.......",
    "...........KYGK......",
    "......KKKKKKRrKKK....",
    "....KqaaaaaKGgKaAAK..",
    "...KqaaaaaaaGgaaaAAK.",
    "..KqqaaaGGGGGGGGGYGK.",
    "..KqaaagggggggggggK..",
    "..KqaaKSSaaSSSSSSHK..",
    ".KqaaKSbbSSSSSSSbbHK.",
    ".KqaaKSSbbbSSSbbbSHK.",
    ".KqaaKSSwppSSSwppSHK.",
    ".KqqaKSSsssSsSsssSSSK",
    ".KqqaKSSSSSSssSSSSSK.",
    "..KqaKSSSSSSSSSSSSK..",
    "..KqaKSSSSmmmmmSSK...",
    "..KqqKsSSSmtttmSSK...",
    "...KqKssSSSmmmSSK....",
    "....KqKsSSSSSSHK.....",
    ".....KqKKssssKK......",
    ".........KKKK........",
]
ROOK_C = {'K': '#3a120c', 'q': '#9a2018', 'a': '#d23e1e', 'A': '#f05e28',
          'g': '#b07418', 'G': '#eab036', 'Y': '#ffd870', 'R': '#d02818', 'r': '#901010',
          'S': '#f8ccb4', 's': '#e09480', 'H': '#fff0e4',
          'b': '#7a1e14', 'w': '#ffffff', 'p': '#b8600c', 'm': '#5a1018', 't': '#ffffff'}
ROOK_BLINK = {'w': 'b', 'p': 'b'}

ILIAN = [
    ".....KKKKKKKKKKKK......",
    "...KKvWWWWWWWWWWVVKK...",
    "..KvWWWWWWWWWWWWWVVK...",
    ".KvWWWWWWWWWWWWWWWVVK..",
    ".KvWWWKSSWWSSSWSSSSHK..",
    ".KvWWWKSSSWSSSSSSSSHK..",
    ".KvWWWKVVVSSSSSSVVVHK..",
    ".KvWWWKSsWWWSSWWWsSHK..",
    ".KvWWWKSSeEeSSeEeSSHK..",
    ".KvWWWKSSsssSSsssSSSSK.",
    ".KvWWWKSSSSSssSSSSSSK..",
    ".KvWWWWWWSSSSSSSSWWWK..",
    ".KvWWWWWVVVVVVVVVVWWK..",
    ".KvWWWWVWWtttttWVWWWK..",
    ".KvvWWWWWmmmmmmmWWWWK..",
    "..KvWWWWWWWWWWWWWWWWK..",
    "..KvvWWWWWWWWWWWWWWK...",
    "....KvWWWWvWWWWWWVWK...",
    "....KvvWWWWvWWWWWWWK...",
    ".....KvWWWWWvWWWWWK....",
    "......KvvWWWWWvWWWWK...",
    ".......KvWWWWWvWWWK....",
    "........KvWWWWWWWK.....",
    ".........KvWWWWWK......",
    "..........KvWWWK.......",
    "...........KvWK........",
    "............KK.........",
]
# la couronne, posée sur les cheveux : son bandeau (2 dernières lignes) recouvre les lignes 2 et 3 de la tête
CROWN = [
    ".......K.......",
    "....K.KYK.K....",
    ".K.KYKKGKKYK.K.",
    "KYKKGKKGKKGKKYK",
    "KGGGGGGcGGGGGYK",
    "KgggggggggggggK",
]
ILIAN_C = {'K': '#1a1830', 'v': '#97a6c6', 'W': '#dfe7f4', 'V': '#ffffff',
           'S': '#d68a62', 's': '#a85a3c', 'H': '#f0b48a',
           'e': '#22c8e8', 'E': '#d0ffff', 'm': '#3a0e14', 't': '#f4ece4',
           'g': '#b07418', 'G': '#eab036', 'Y': '#ffd870', 'c': '#2ee6ff'}
ILIAN_BLINK = {'e': 's', 'E': 's'}

SABLE = [
    "....KKK..KKK............",
    "...KdfFKKfFFK...........",
    "...KdfFFKfFFFKK.........",
    "....KfFFFFFFFFFLLK......",
    "...KfFFFFFFFFFFFLLK.....",
    "..KffFFFFFFFFFFFFFLK....",
    "..KfFFFFddFFFFFFFFFddLK.",
    "..KffFFFFkkkkFFkkkkFFLK.",
    "..KfFFFFFkaapkFkaapkFFLK",
    "..KffFFFkFfffFFFfffkFLK.",
    "..KfFFFFFFFFFLLLLLLLLnnK",
    "..KffFFFFFFFCCCCCCCnnnK.",
    "...KfFFFFFFCCCCCCCCcK...",
    "...KffFFFFCmtmmmmtmK....",
    "....KfFFFFCmmTTTmmK.....",
    "....KffFFFCmtmmmtK......",
    ".....KfFFFCCCCCCK.......",
    "......KfFFcCCCCK........",
    ".......KffcccK..........",
    "........KKKKK...........",
]
# le cobra d'or posé au front
COBRA = [".KK.", "KYGK", "KGRK", ".KgK", "..K."]
SABLE_C = {'K': '#24120a', 'd': '#6a3a12', 'f': '#b0702a', 'F': '#e09e4a', 'L': '#f6c676',
           'C': '#f2dfbc', 'c': '#d4b488', 'n': '#3a1a10', 'm': '#3e0a0e', 'T': '#c84a58', 't': '#ffffff',
           'k': '#24120a', 'a': '#f0a018', 'p': '#1a0a04',
           'g': '#b07418', 'G': '#eab036', 'Y': '#ffd870', 'R': '#d02818'}
SABLE_BLINK = {'a': 'k', 'p': 'k'}

KAEL = [
    "....KKKKKKKK........",
    "..KKsSSSSSSHKK......",
    ".KsSSSSSSSSSHHK.....",
    "KzsSSSSSSSSSSHHK....",
    "KzsSSSSSSSSSSSShKK..",
    "KzsSSSSSSHHHHHHHhhhK",
    "KzsSSSSSzzzzzzzzzzK.",
    "KzsSSSSSzyywzyywzzK.",
    "KzsSSSSSSzzzzzzzSSHK",
    "KzssSlSSSSSSSSSSSShK",
    ".KzsSlLSSSSSSSSSzzK.",
    ".KzsSSlSSHHSSSSSSK..",
    ".KzzsSSlSSSSSSSSSSK.",
    "..KzzsSSSSSSSSSSSShK",
    "..KzzzssSSSSSSSSSShK",
    "...KKzzzsssssssssHK.",
    ".....KKKKzzzzzzzzK..",
    ".........KKKKKKKK...",
]
KAEL_C = {'K': '#0e0a0c', 'z': '#1a1216', 's': '#33262a', 'S': '#4e3a3a', 'H': '#6e5450', 'h': '#94746a',
          'y': '#ffa418', 'w': '#fff6c0', 'l': '#ff8a1a', 'L': '#ffe070'}
KAEL_BLINK = {'y': 'z', 'w': 'z'}

HEADS = {'eldra': (ELDRA, ELDRA_C, ELDRA_BLINK), 'rook': (ROOK, ROOK_C, ROOK_BLINK), 'ilian': (ILIAN, ILIAN_C, ILIAN_BLINK),
         'sable': (SABLE, SABLE_C, SABLE_BLINK), 'kael': (KAEL, KAEL_C, KAEL_BLINK)}


def check():
    for name, (rows, legend, _) in HEADS.items():
        w = {len(r) for r in rows}
        miss = {ch for r in rows for ch in r if ch != '.' and ch not in legend}
        assert len(w) == 1, (name, w, [i for i, r in enumerate(rows) if len(r) != max(w)])
        assert not miss, (name, miss)
    for name, rows in (('CROWN', CROWN), ('COBRA', COBRA)):
        assert len({len(r) for r in rows}) == 1, name


def ilian(c, x, y, blink):
    c.sprite(x, y, ILIAN, ILIAN_C, ILIAN_BLINK if blink else None)
    c.sprite(x + 5, y - 2, CROWN, ILIAN_C)


def sable(c, x, y, blink):
    c.sprite(x, y, SABLE, SABLE_C, SABLE_BLINK if blink else None)
    c.sprite(x + 10, y + 1, COBRA, SABLE_C)


if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from PIL import Image
    from pix import Canvas
    check()
    tiles = []
    for name, (rows, legend, blink) in HEADS.items():
        for bl in (False, True):
            c = Canvas(30, 32, 0, 0)
            if name == 'ilian':
                ilian(c, 3, 4, bl)
            elif name == 'sable':
                sable(c, 3, 4, bl)
            else:
                c.sprite(3, 4, rows, legend, blink if bl else None)
            bg = Image.new('RGBA', (30, 32), (47, 111, 154, 255))
            bg.alpha_composite(c.image())
            tiles.append(bg.resize((30 * 8, 32 * 8), Image.NEAREST))
    im = Image.new('RGB', (sum(t.width for t in tiles) // 2 * 1 + 0, 32 * 8 * 2), (17, 17, 17))
    for k, t in enumerate(tiles):
        im.paste(t, ((k // 2) * 240, (k % 2) * 256))
    im.save(sys.argv[1])
    print(sys.argv[1], im.size)
