class Thesis:
    def __init__(self, tokens_lst=[], accumulation=1):
        self.tokens_lst = tokens_lst
        self.accumulation = accumulation
    
    def add(self, node, value):
        new = Thesis(self.tokens_lst[:], self.accumulation)
        
        if node in new.tokens_lst:
            new.accumulation *= -1

        new.tokens_lst.append(node)
        new.accumulation *= value

        return new
    
    def __eq__(self, b):
        return set(b.tokens_lst) == set(self.tokens_lst)
    
    def __hash__(self):
        return round(self.accumulation * 10*10)  # int(hashlib.sha1(str(self.tokens_lst).encode("utf-8")).hexdigest(), 16) % (10 ** 8)

    def __repr__(self):

        return f"Thesis(tokens_lst={self.tokens_lst}, accumulation={self.accumulation})"

class MyPredicter:
    def __init__(self, pagerank_dct, connections_dct):
        self.pagerank_dct = {k: v*100 for k, v in pagerank_dct.items()}
        self.connections_dct = connections_dct
    
    def find_thesis(self, max_lenght: int, node_name: str = None, answer: list = None):
        def f(th: Thesis):
            node_name = th.tokens_lst[-1]
            next_nodes = self.connections_dct[node_name]
            return [th.add(n, self.pagerank_dct[n]) for n in next_nodes]
        
        if not max_lenght:
            for i, th in enumerate(answer):
                print(f'{i+1}. "{", ".join(th.tokens_lst)}" (acc value = {round(th.accumulation)})')
            
            return answer
        
        if answer is None:
            current_value = self.pagerank_dct[node_name]
            th = Thesis().add(node_name, current_value)
            return self.find_thesis(max_lenght-1, answer=f(th))
        
        lst = []
        for th in answer:
            lst.extend(f(th))
        
        new_answer = sorted(list(set(lst)), key=lambda x: -x.accumulation)[:10]
        return self.find_thesis(max_lenght-1, answer=new_answer)