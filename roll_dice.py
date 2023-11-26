import tkinter as tk
import random


def roll_dice():
    # Rolling two dice
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)

    # ASCII art for dice faces, adjusted for square shape
    dice_faces = {
        1: ["-------", "|     |", "|  o  |", "|     |", "-------"],
        2: ["-------", "|o    |", "|     |", "|    o|", "-------"],
        3: ["-------", "|o    |", "|  o  |", "|    o|", "-------"],
        4: ["-------", "|o   o|", "|     |", "|o   o|", "-------"],
        5: ["-------", "|o   o|", "|  o  |", "|o   o|", "-------"],
        6: ["-------", "|o   o|", "|o   o|", "|o   o|", "-------"],
    }

    # Clear the previous result
    result_label.config(text="")

    # Display dice
    for i in range(5):
        result_label["text"] += (
            dice_faces[dice1][i] + "   " + dice_faces[dice2][i] + "\n"
        )


# Set up the GUI window
root = tk.Tk()
root.title("Dice Roller")
root.geometry("600x400")  # Larger window size

# Create a button with increased size
roll_button = tk.Button(root, text="Roll Dice", command=roll_dice, height=5, width=10)
roll_button.pack(pady=20)  # Add padding for spacing

# Create a label to show the dice, centered
result_label = tk.Label(root, font=("Courier", 16), justify="center")
result_label.pack(expand=True)

# Start the GUI event loop
root.mainloop()
