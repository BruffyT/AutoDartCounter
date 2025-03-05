import tkinter as tk

class DartGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Dart Scoring System")

        self.players = 1
        self.scores = [501, 501]

        self.label = tk.Label(root, text="Select Players:", font=("Arial", 14))
        self.label.pack()

        self.player_button1 = tk.Button(root, text="1 Player", command=lambda: self.set_players(1))
        self.player_button1.pack()

        self.player_button2 = tk.Button(root, text="2 Players", command=lambda: self.set_players(2))
        self.player_button2.pack()

        self.score_label = tk.Label(root, text=f"Player 1: {self.scores[0]}", font=("Arial", 20))
        self.score_label.pack()

        if self.players == 2:
            self.score_label2 = tk.Label(root, text=f"Player 2: {self.scores[1]}", font=("Arial", 20))
            self.score_label2.pack()

    def set_players(self, num):
        self.players = num
        print(f"Players set to {num}")

    def update_score(self, player, score):
        self.scores[player] -= score
        self.score_label.config(text=f"Player 1: {self.scores[0]}")
        if self.players == 2:
            self.score_label2.config(text=f"Player 2: {self.scores[1]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DartGame(root)
    root.mainloop()
