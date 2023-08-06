from collections import defaultdict
from random import shuffle
from itertools import combinations
from collections import defaultdict
from sortedcontainers import SortedList
try:
    from tqdm import tqdm
except ModuleNotFoundError:
    def tqdm(x):
        return x

class DictionaryWithBackup(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backup = {}
    def __setitem__(self, key, value):
        if key not in self.backup:
            self.backup[key] = self[key] if key in self else None
        super().__setitem__(key, value)
    def __delitem__(self, key):
        if key not in self.backup:
            self.backup[key] = self[key]
        super().__delitem__(key)
    def restore(self, B):
        for k, v in B.items():
            self[k] = v
            if v is None:
                del self[k]

class Ranking:

    def __init__(self, n_rerankings, data, basis, heads, tails):
        self.data = data
        self.basis = basis
        self.n_rerankings = 2 ** (n_rerankings + 1)
        self.placement = {x: (i + 1) * self.n_rerankings for i, x in enumerate(basis)}
        self.ranks = SortedList(self.placement.values())
        self.ranks.add(0)
        self.memo = DictionaryWithBackup()
        self.lookup = {i: x for x, i in self.placement.items()}
        self.heads, self.tails = heads, tails

    def rerank(self, current, lower_bound):
        self.memo.backup.clear()
        backup = [SortedList(self.ranks), dict(self.lookup)]
        self.ranks.remove(current)
        position = self.ranks.bisect_left(lower_bound)
        new = (self.ranks[position - 1] + self.ranks[position]) // 2
        if new in self.ranks:
            return new, [*backup, self.memo.backup]
        self.ranks.add(new)
        basis_item = self.lookup[current]
        del self.lookup[current]
        self.lookup[new] = basis_item
        if basis_item in self.memo:
            self.memo[basis_item] = min(self.memo[basis_item], new)
        news = {basis_item}
        while news:
            old_news = news
            news = set()
            def insert(a, b, c):
                for key in [(a + b), (b + c), (a + c), (a + b + c)]:
                    if key not in self.memo:
                        return
                self.memo[a + b + c] = min(self.memo[a + b + c], 
                    max(self.memo[a + b], self.memo[b + c], self.memo[a + c])
                )
                if self.memo[a + b + c] == new:
                    news.add(a + b + c)
                ab = a + b + c
                for i in range(1, len(ab)):
                    a, b = ab[:i], ab[i:]
                    self.heads[b].add(a)
                    self.tails[a].add(b) 
            for ab in old_news:
                for i in range(1, len(ab)):
                    a, b = ab[:i], ab[i:]
                    for c in self.tails[a] & self.tails[b]:
                        insert(a, b, c)
            for ac in old_news:
                for i in range(1, len(ac)):
                    a, c = ac[:i], ac[i:]
                    for b in self.tails[a] & self.heads[c]:
                        insert(a, b, c)
            for bc in old_news:
                for i in range(1, len(bc)):
                    b, c = bc[:i], bc[i:]
                    for a in self.heads[b] & self.heads[c]:
                        insert(a, b, c) 
        backup.append(dict(self.memo.backup))
        self.placement.clear()
        for k, v in self.lookup.items():
            self.placement[v] = k
        return new, backup

    def restore(self, backup):
        self.ranks, self.lookup, memo_backup = backup
        self.memo.restore(memo_backup)
        self.placement.clear()
        for k, v in self.lookup.items():
            self.placement[v] = k

    def rank(self, x):
        if x in self.memo:
            return self.memo[x]
        minimum = max(self.ranks) + 1
        if x in self.placement:
            minimum = self.placement[x]
        for i, j in combinations(range(1, len(x)), 2):
            a, b, c = x[:i], x[i:j], x[j:]
            sub = self.rank(a + b)
            if sub < minimum:
                sub = max(sub, self.rank(b + c))
                if sub < minimum:
                    sub = max(sub, self.rank(a + c))
                    if sub < minimum:
                        minimum = sub
        if x not in self.memo:
            ab = x
            for i in range(1, len(ab)):
                a, b = ab[:i], ab[i:]
                self.heads[b].add(a)
                self.tails[a].add(b)
        self.memo[x] = minimum
        return minimum
    
    def loss(self, reverse=False):
        result = []
        for x in self.data:
            r = self.rank(x)
            try: 
                i = self.ranks.index(r)
            except:
                i = len(self.ranks)
            if reverse:
                i = len(self.ranks) - i
            result.append(i / len(self.ranks))
        result.sort()
        n = len(result)
        return sum(result) / n

    def p(self, x):
        r = self.rank(x)
        if r > max(self.ranks):
            return 0
        if r not in self.ranks:
            self.ranks.add(r)
        return 1 - self.ranks.index(r) / len(self.basis)

    def ranked_basis(self):
        return [self.lookup[x] for x in self.ranks if x > 0]


def ternary_search_optimize(R, num_iterations, reverse=False):
    visited = set()
    for _ in tqdm(range(num_iterations)):
        bottom = len(R.ranks) - 1
        while bottom > 0 and R.lookup[R.ranks[bottom]] in visited:
            bottom -= 1
        if bottom <= 0:
            break
        b = R.lookup[R.ranks[bottom]]
        visited.add(b)
        left, right = 0, bottom - 1
        while abs(left - right) > 2:
            left_third  = left  + (right - left) // 3
            right_third = right - (right - left) // 3
            _, left_backup = R.rerank(R.placement[b], R.ranks[left_third])
            left_loss = R.loss(reverse)
            R.restore(left_backup)
            _, right_backup = R.rerank(R.placement[b], R.ranks[right_third])
            right_loss = R.loss(reverse)
            R.restore(right_backup)
            if left_loss > right_loss:
                left = left_third
            else:
                right = right_third
        mid = (left + right) // 2
        pre_loss = R.loss(reverse)
        _, backup = R.rerank(R.placement[b], R.ranks[mid])
        post_loss = R.loss(reverse)
        if pre_loss < post_loss:
            R.restore(backup)
    return R

class Learner:

    def __init__(self, data, N=4):
        self.loss = 1.0
        self.N = N
        self.data = data
        self.alphabet = sorted({x for xs in data for x in xs})
        self.basis = []
        for m in range(2, self.N + 1):
            subseqs = set()
            for x in data:
                for s in combinations(x, m):
                    subseqs.add(''.join(s))
            self.basis.extend(sorted(subseqs))
        shuffle(self.basis)
        self._prepare()
    
    def _prepare(self):
        self.heads, self.tails = self._heads_and_tails()
        self.ranking = Ranking(len(self.basis), self.data, self.basis, self.heads, self.tails)

    def _heads_and_tails(self):
        heads, tails = defaultdict(set), defaultdict(set)
        for ab in self.basis:
            for i in range(1, len(ab)):
                a, b = ab[:i], ab[i:]
                heads[b].add(a)
                tails[a].add(b)
        return heads, tails

    def optimize(self):
        backup = list(self.basis)
        loss_before = self.ranking.loss()
        self.basis = list(reversed(self.basis))
        self._prepare()
        self.ranking = ternary_search_optimize(self.ranking, len(self.basis), reverse=True)
        self.basis = list(reversed(self.ranking.ranked_basis()))
        self._prepare()
        self.ranking = ternary_search_optimize(self.ranking, len(self.basis))
        self.basis = list(self.ranking.ranked_basis())
        loss_after = self.ranking.loss()
        if loss_after > loss_before:
            self.basis = backup
            self._prepare()
            return False
        self.loss = loss_after
        return True
    
    def rate(self, word):
        return self.ranking.p(word)
