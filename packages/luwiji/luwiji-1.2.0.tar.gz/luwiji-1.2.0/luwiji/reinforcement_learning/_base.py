import os
from IPython.display import Image
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


class BaseDemoReinforcement:
    def __init__(self):
        self.states = ['start', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'goal']
        self._edges = [
            ("start", "1"), ("start", "3"), ("start", "2"), ("1", "5"),
            ("1", "4"), ("3", "2"), ("4", "6"), ("5", "4"), ("5", "6"),
            ("6", "7"), ("2", "8"), ("8", "9"), ("3", "9"), ("8", "6"),
            ("6", "goal"), ("7", "goal"), ("8", "10"), ("9", "10"), ("7", "10"), ("4", "8")
        ]
        self._steps = ["start"]
        self.start = "start"
        self.goal = "goal"

        self.current_state = self.start
        self.n_state = len(self.states)

        self._reward_rule = {}
        for s, a in self._edges:
            self._reward_rule[s, a] = 100 if a == self.goal else 0
            self._reward_rule[a, s] = 100 if s == self.goal else 0
        self._reward_rule[self.goal, self.goal] = 100

    def render(self):
        G = nx.Graph()
        G.add_edges_from(self._edges)

        position = nx.spring_layout(G, seed=0)

        plt.figure(figsize=(6, 6))
        color = ["w" if node not in self._steps else "r" for node in G]
        nx.draw_networkx_nodes(G, position, node_size=1000, node_color=color, edgecolors='k')
        nx.draw_networkx_edges(G, position)
        nx.draw_networkx_labels(G, position)
        plt.show()

    def step(self, action):
        new_state = action
        self._steps.append(new_state)
        reward = self._reward_rule[self.current_state, action]
        self.current_state = new_state
        done = True if self.current_state == self.goal else False
        return new_state, reward, done

    def random_action(self):
        return np.random.choice([a for s, a in self._reward_rule if s == self.current_state])

    def reset(self):
        self.current_state = self.start
        self._steps = ["start"]
        return self.current_state


class BaseIllustrationReinforcement:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.vocabulary = Image(f"{here}/assets/vocabulary.png", width=400)
        self.action_value = Image(f"{here}/assets/action_value.png", width=600)
