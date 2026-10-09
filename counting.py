"""Finite line crossing logic, independent of the detector."""
from dataclasses import dataclass, field

def side(p, a, b):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])

def intersects(p, q, a, b):
    """A movement crosses the finite counting segment, not its extension."""
    return side(p,a,b)*side(q,a,b)<0 and side(a,p,q)*side(b,p,q)<=0

@dataclass
class LineCounter:
    lines: dict
    previous: dict = field(default_factory=dict)
    crossed: set = field(default_factory=set)
    counts: dict = field(init=False)

    def __post_init__(self):
        self.counts = {name:0 for name in self.lines}
        if any(a==b for a,b in self.lines.values()):
            raise ValueError('Counting lines must have distinct endpoints')

    def update(self, track_id, point):
        events=[]
        for name,(a,b) in self.lines.items():
            key=(name,int(track_id))
            # Retain the last non-zero side so a point exactly on the line
            # followed by a point on the opposite side is counted once.
            if side(point,a,b)==0:
                continue
            prev=self.previous.get(key)
            if prev is not None and key not in self.crossed and intersects(prev,point,a,b):
                self.crossed.add(key); self.counts[name]+=1; events.append(name)
            self.previous[key]=point
        return events
