class Filler:
    def __init__(self, name, r, g, b, t, amount=0, is_inf=False):
        self.name = name
        self.color = (r, g, b)
        self.transparency = t
        self.amount = amount
        self.is_inf = is_inf
