# Documentation for `textWahl`

> ⚠️ **Low Confidence Warning**: Incomplete context.


> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.
### textWahl() -> None

**Description:**
The `textWahl` function facilitates user interaction in a Rock-Paper-Scissors game by prompting the player to make a choice between rock, paper, or scissors. It handles user input, validates it, and provides feedback based on the player's selection.

**Parameters:**
None

**Expected Input:**
- The function expects the user to input a string representing their choice. Valid inputs are "rock", "paper", or "scissors". The function is case-insensitive and will prompt the user again if the input is invalid.

**Returns:**
None

**Detailed Logic:**
- The function begins by displaying a prompt to the user, asking them to select one of the three options: rock, paper, or scissors.
- It captures the user's input using the `input` function and normalizes it to lowercase to ensure case insensitivity.
- The function checks if the input is one of the valid options. If the input is valid, it prints a confirmation message displaying the player's choice.
- If the input is invalid, it raises a `ValueError`, which is a built-in exception in Python, indicating that the user has provided an invalid selection.
- The function may also include a delay using the `sleep` function to enhance user experience by pacing the interaction.
- Overall, `textWahl` serves as a critical component for gathering user input in the game, ensuring that the input is both valid and user-friendly.

---
*Generated with 0% context confidence*