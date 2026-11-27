# Outil copié de ../aurelle/outils.py (FigureM) : la racine d'un membre se fond dans un autre morceau par un masque en
# dégradé (raccord épaule / buste sans couture). Aucun flou.
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from atelier import Figure  # noqa: E402


class FigureM(Figure):
    """La Figure d'atelier.py, plus des MASQUES par morceau : fig.masks[nom] = (dégradé, ref) ; le morceau (son ombre
    portée, sa couleur, ses ombres et lumières) est peint à travers un masque qui le rend transparent PAR-DESSUS le
    morceau `ref` (dans le sens du dégradé : (x1, y1) opaque → (x2, y2) transparent), et opaque partout ailleurs.
    Sert au raccord épaule / buste : la racine du bras se fond dans la poitrine (aucune couture, aucun bord de boule),
    alors que le bras reste devant le buste (il peut passer devant le ventre dans les coups). Aucun flou."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.masks = {}

    def svg(self, size=None, bg=None):
        n0 = self.n
        s = super().svg(size, bg)
        names = [p.name for p in self.parts]
        pid = lambda nm: 'p%d' % (n0 + names.index(nm) + 1)
        add_defs = []
        for k, (name, (x1, y1, x2, y2, ref)) in enumerate(self.masks.items()):
            if name not in names or ref not in names:
                continue
            P = pid(name)
            mid, gid = 'mk%s' % P, 'mg%s' % P
            add_defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%.3f" y1="%.3f" x2="%.3f" y2="%.3f">'
                            '<stop offset="0" stop-color="#fff"/><stop offset="0.35" stop-color="#fff"/>'
                            '<stop offset="0.75" stop-color="#3a3a3a"/><stop offset="1" stop-color="#000"/></linearGradient>'
                            % (gid, x1, y1, x2, y2))
            add_defs.append('<mask id="%s" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="%.2f" y="%.2f" '
                            'width="%.2f" height="%.2f"><rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="#fff"/>'
                            '<use href="#%s" fill="url(#%s)"/></mask>'
                            % (mid, self.x0 - 50, self.y0 - 50, self.w + 100, self.h + 100,
                               self.x0 - 50, self.y0 - 50, self.w + 100, self.h + 100, pid(ref), gid))
            i_fill = s.index('<use href="#%s" fill="url(#' % P)        # la couleur du morceau (pas sa silhouette)
            start = i_fill
            i_cast = s.rfind('<g clip-path=', 0, i_fill)
            if i_cast >= 0 and ('<use href="#%s" opacity="0.2"' % P) in s[i_cast:i_fill]:
                start = i_cast
            end = s.index('/>', i_fill) + 2
            if s.startswith('<g clip-path="url(#', end):
                depth, j = 0, end
                while True:
                    a_ = s.find('<g', j)
                    b_ = s.find('</g>', j)
                    if a_ != -1 and a_ < b_:
                        depth += 1
                        j = a_ + 2
                    else:
                        depth -= 1
                        j = b_ + 4
                        if depth == 0:
                            break
                end = j
            s = s[:start] + '<g mask="url(#%s)">' % mid + s[start:end] + '</g>' + s[end:]
        if add_defs:
            i = s.index('</defs>')
            s = s[:i] + ''.join(add_defs) + s[i:]
        return s
