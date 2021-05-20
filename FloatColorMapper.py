
import numpy as np

def colorScaleTupleToHex(t):
    digs = '0123456789abcdef'
    ans = '#'
    for x in t:
        y = int(x*255)
        ans += digs[y//16]
        ans += digs[y%16]
    return ans

def floatScaleToColor(x):
    # blue -> green -> red
    if x < 0.5:
        return (0,x*2,1-x*2)
    else:
        y = x-.5
        return (y*2,1-y*2,0)

def normalize_minmax(fs):
    fs = np.array(fs)
    fs -= fs.min()
    fs /= fs.max()
    return fs

def normalize_sort(fs):
    N = len(fs)
    pts = [(val, idx) for idx,val in enumerate(fs)]
    pts.sort()
    idx_sort = [p[1] for p in pts]
    val_sort = [p[0] for p in pts]
    ans = np.zeros(N)
    ans[idx_sort] = np.arange(N) / (N-1)
    return ans
    
def genJSON(points, floatScale, norm_func=normalize_minmax):
    ans = []
    N = len(floatScale)
    normed = norm_func(floatScale)
    for i in range(N):
        ans.append({
            'point': list(points[i]),
            'color': colorScaleTupleToHex(floatScaleToColor(normed[i]))
        })
    return ans
